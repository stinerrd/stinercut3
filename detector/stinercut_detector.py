#!/usr/bin/env python3
"""
Stinercut Media Detection Host Service

Monitors USB device events using pyudev and notifies the backend API
when removable media is mounted or unmounted.
"""

import configparser
import getpass
import json
import logging
import os
import pwd
import re
import select
import signal
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

import pyudev
import websocket


# Video extensions for GOPRO copy (case-insensitive)
GOPRO_VIDEO_EXTENSIONS = {'.mp4', '.lrv'}

# Regex pattern for GOPRO folders (100GOPRO, 101GOPRO, etc.)
GOPRO_FOLDER_PATTERN = re.compile(r'^\d{3}GOPRO$', re.IGNORECASE)

# Regex for parsing rsync progress2 output (supports both US and EU number formats)
# US: 542,449,068  40%  20.74MB/s
# EU: 542.449.068  40%  20,74MB/s
RSYNC_PROGRESS_PATTERN = re.compile(r'^\s*([\d.,]+)\s+(\d+)%\s+([\d.,]+\w+/s)')

# Copy log filename on SD card (tracks which files were already copied)
COPY_LOG_FILENAME = "_stinercut_copied.txt"


@dataclass
class CopyJob:
    """Represents a single GOPRO copy operation."""
    job_id: str
    device_node: str
    mount_path: str
    target_dir: str
    gopro_info: dict = field(default_factory=dict)  # Original gopro_info from detection
    files_to_copy: list = field(default_factory=list)  # List of relative paths to copy
    total_bytes: int = 0
    video_count: int = 0
    bytes_copied: int = 0
    percent: int = 0
    speed: str = ""
    last_reported_percent: int = -10  # For 10% interval reporting
    start_time: float = field(default_factory=time.time)
    process: Optional[subprocess.Popen] = None
    error: Optional[str] = None
    reusing_uuid: bool = False  # True if reusing existing UUID from copy log


class GoproCopyManager:
    """Manages GOPRO file copy operations with progress tracking."""

    def __init__(self, detector: 'StinercutDetector'):
        self.detector = detector
        self.active_jobs: dict[str, CopyJob] = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger("gopro-copy")
        # Get target base from config (host path, not Docker path)
        self.target_base = detector.config["gopro"].get("target_base", "/videodata/input")

    def start_copy(self, mount_path: str, device_node: str, gopro_info: dict) -> str | None:
        """
        Start a copy operation for a GOPRO device.

        Args:
            mount_path: Path where device is mounted
            device_node: Device node (e.g., /dev/sdb1)
            gopro_info: Dict with gopro_folders, total_size, video_count

        Returns:
            job_id (UUID) for tracking, or None if all files already copied
        """
        dcim_path = os.path.join(mount_path, "DCIM")

        # Load existing copy log to check what's already copied
        copied_files, existing_uuid = self._load_copy_log(dcim_path)

        # Determine which files need to be copied
        files_to_copy, new_bytes = self._get_files_to_copy(gopro_info, copied_files)

        if not files_to_copy:
            self.logger.info("All GOPRO files already copied, skipping")
            # Send skipped signal
            self.detector._send_ws_message("gopro.copy_skipped", {
                "device_node": device_node,
                "mount_path": mount_path,
                "reason": "all_copied",
                "existing_uuid": existing_uuid,
            })
            return None

        # Determine UUID: reuse existing if target dir exists, otherwise generate new
        reusing_uuid = False
        if existing_uuid:
            existing_target = os.path.join(self.target_base, existing_uuid)
            if os.path.isdir(existing_target):
                job_id = existing_uuid
                target_dir = existing_target
                reusing_uuid = True
                self.logger.info(f"Reusing existing UUID: {existing_uuid}")
            else:
                job_id = str(uuid.uuid4())
                target_dir = os.path.join(self.target_base, job_id)
        else:
            job_id = str(uuid.uuid4())
            target_dir = os.path.join(self.target_base, job_id)

        job = CopyJob(
            job_id=job_id,
            device_node=device_node,
            mount_path=mount_path,
            target_dir=target_dir,
            gopro_info=gopro_info,
            files_to_copy=files_to_copy,
            total_bytes=new_bytes,
            video_count=len(files_to_copy),
            reusing_uuid=reusing_uuid,
        )

        with self.lock:
            self.active_jobs[job_id] = job

        # Start copy in background thread
        thread = threading.Thread(
            target=self._copy_worker,
            args=(job,),
            daemon=True,
        )
        thread.start()

        return job_id

    def _copy_worker(self, job: CopyJob):
        """Execute the copy operation with progress tracking using selective file list."""
        files_list_path = None
        try:
            # Create target directory with proper permissions
            os.makedirs(job.target_dir, mode=0o755, exist_ok=True)
            os.chmod(job.target_dir, 0o755)

            self.logger.info(
                f"Starting GOPRO copy: {len(job.files_to_copy)} files "
                f"({job.total_bytes / (1024**3):.2f} GB) -> {job.target_dir}"
                f"{' (reusing UUID)' if job.reusing_uuid else ''}"
            )

            # Send copy_started signal
            self._send_signal("gopro.copy_started", job)

            # Build rsync command with --files-from for selective copy
            dcim_path = os.path.join(job.mount_path, "DCIM")

            # Create temp file with list of files to copy (inside target folder)
            files_list_path = os.path.join(job.target_dir, ".rsync_files.txt")
            with open(files_list_path, 'w') as f:
                for rel_path in job.files_to_copy:
                    f.write(f"{rel_path}\n")

            cmd = [
                "rsync",
                "-a",  # Archive mode (preserves timestamps!)
                "--info=progress2",
                "--no-inc-recursive",
                "--whole-file",
                "--inplace",
                "--files-from", files_list_path,
                f"{dcim_path}/",
                f"{job.target_dir}/",
            ]

            self.logger.debug(f"rsync command: {' '.join(cmd)}")

            # Start rsync process
            job.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Binary mode for manual line handling
                bufsize=0,   # Unbuffered
            )

            # Read progress output (rsync uses \r for progress updates)
            stall_counter = 0
            buffer = b""
            while job.process.poll() is None:
                # Use select to check if data is available (non-blocking)
                ready, _, _ = select.select([job.process.stdout], [], [], 1.0)
                if ready:
                    chunk = job.process.stdout.read(4096)
                    if chunk:
                        stall_counter = 0
                        buffer += chunk
                        self.logger.debug(f"rsync raw output: {chunk[:200]!r}")

                        # Process complete lines (split by \r or \n)
                        while b'\r' in buffer or b'\n' in buffer:
                            # Find first separator
                            r_pos = buffer.find(b'\r')
                            n_pos = buffer.find(b'\n')

                            if r_pos == -1:
                                sep_pos = n_pos
                            elif n_pos == -1:
                                sep_pos = r_pos
                            else:
                                sep_pos = min(r_pos, n_pos)

                            line = buffer[:sep_pos].decode('utf-8', errors='replace')
                            buffer = buffer[sep_pos + 1:]

                            if line.strip():
                                self.logger.debug(f"rsync line: {line}")
                                self._parse_and_report_progress(job, line)
                else:
                    stall_counter += 1
                    if stall_counter > 300:  # 5 minutes with no output
                        self.logger.warning(f"Copy stalled for job {job.job_id}")
                        job.process.terminate()
                        job.error = "Copy operation stalled - no progress for 5 minutes"
                        self._send_signal("gopro.copy_failed", job)
                        return

            # Check exit code
            exit_code = job.process.returncode
            stderr = job.process.stderr.read()

            if exit_code == 0:
                job.percent = 100
                duration = time.time() - job.start_time
                self.logger.info(f"GOPRO copy completed: {job.job_id} in {duration:.1f}s")

                # Fix permissions on copied files (644 for files)
                self._fix_permissions(job.target_dir)

                # Update copy log on SD card
                self._append_to_copy_log(dcim_path, job.files_to_copy, job.job_id)

                self._send_signal("gopro.copy_completed", job, duration=duration)

                # Organize SD card - rename DCIM to UUID (separate from copy success)
                organize_success, organize_error = self._organize_sd_card(job.mount_path, job.job_id)
                if organize_success:
                    self._send_signal("gopro.sd_organized", job)
                else:
                    self.logger.warning(f"SD card organization failed: {job.job_id} - {organize_error}")
                    self._send_signal("gopro.sd_organize_failed", job, error=organize_error)
            else:
                job.error = stderr.strip() if stderr else f"rsync failed with code {exit_code}"
                self.logger.error(f"GOPRO copy failed: {job.job_id} - {job.error}")
                self._send_signal("gopro.copy_failed", job)

        except Exception as e:
            job.error = str(e)
            self.logger.error(f"GOPRO copy error: {job.job_id} - {e}", exc_info=True)
            self._send_signal("gopro.copy_failed", job)

        finally:
            # Clean up temp files list
            if files_list_path and os.path.exists(files_list_path):
                try:
                    os.remove(files_list_path)
                except OSError:
                    pass

            with self.lock:
                self.active_jobs.pop(job.job_id, None)

    def _parse_and_report_progress(self, job: CopyJob, line: str):
        """Parse rsync progress line and send update if threshold crossed."""
        match = RSYNC_PROGRESS_PATTERN.search(line)
        if not match:
            return

        # Remove thousand separators (both . and ,) from bytes string
        bytes_str = match.group(1).replace('.', '').replace(',', '')
        job.bytes_copied = int(bytes_str)
        job.percent = int(match.group(2))
        job.speed = match.group(3)

        # Report at 10% intervals
        next_threshold = ((job.last_reported_percent // 10) + 1) * 10
        if job.percent >= next_threshold and job.percent < 100:
            job.last_reported_percent = (job.percent // 10) * 10
            self.logger.debug(f"Sending progress: {job.percent}%")
            self._send_signal("gopro.copy_progress", job)

    def _send_signal(self, command: str, job: CopyJob, **extra):
        """Send WebSocket signal for copy operation."""
        data = {
            "uuid": job.job_id,
            "device_node": job.device_node,
            "mount_path": job.mount_path,
            "target_dir": job.target_dir,
            "percent": job.percent,
            "bytes_copied": job.bytes_copied,
            "total_bytes": job.total_bytes,
            "video_count": job.video_count,
            "speed": job.speed,
            "reusing_uuid": job.reusing_uuid,
        }

        if job.error:
            data["error"] = job.error

        data.update(extra)

        self.detector._send_ws_message(command, data)

    def _fix_permissions(self, target_dir: str):
        """Set proper permissions on copied files (644 for files, 755 for dirs)."""
        try:
            for root, dirs, files in os.walk(target_dir):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
        except OSError as e:
            self.logger.warning(f"Could not fix permissions: {e}")

    def _organize_sd_card(self, mount_path: str, uuid: str) -> tuple[bool, str | None]:
        """
        Rename DCIM folder to UUID on SD card (instant metadata operation).

        Args:
            mount_path: Root of mounted SD card (e.g., /media/user/SDCARD)
            uuid: The job UUID used for the import

        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        dcim_path = os.path.join(mount_path, "DCIM")
        uuid_path = os.path.join(mount_path, uuid)

        try:
            os.rename(dcim_path, uuid_path)
            self.logger.info(f"Organized SD card: renamed DCIM to {uuid}")
            return True, None

        except PermissionError as e:
            return False, f"Permission denied: {e}"
        except OSError as e:
            return False, f"Failed to rename DCIM: {e}"

    def _load_copy_log(self, dcim_path: str) -> tuple[dict[str, str], str | None]:
        """
        Load existing copy log from SD card.

        Args:
            dcim_path: Path to DCIM folder on SD card

        Returns:
            Tuple of (copied_files: {relative_path: uuid}, last_uuid: str or None)
        """
        log_path = os.path.join(dcim_path, COPY_LOG_FILENAME)
        copied_files = {}
        last_uuid = None

        if not os.path.exists(log_path):
            return copied_files, None

        try:
            with open(log_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ' => ' in line:
                        rel_path, file_uuid = line.split(' => ', 1)
                        copied_files[rel_path] = file_uuid
                        last_uuid = file_uuid  # Track last UUID for reuse
            self.logger.debug(f"Loaded copy log with {len(copied_files)} entries, last UUID: {last_uuid}")
        except (IOError, OSError) as e:
            self.logger.warning(f"Could not read copy log {log_path}: {e}")

        return copied_files, last_uuid

    def _get_files_to_copy(self, gopro_info: dict, copied_files: dict) -> tuple[list[str], int]:
        """
        Get list of files that haven't been copied yet.

        Args:
            gopro_info: Dict with gopro_folders list
            copied_files: Dict of {relative_path: uuid} already copied

        Returns:
            Tuple of (list of relative paths to copy, total size in bytes)
        """
        files_to_copy = []
        total_size = 0

        for folder_path in gopro_info.get("gopro_folders", []):
            folder_name = os.path.basename(folder_path)  # e.g., "100GOPRO"

            try:
                for filename in os.listdir(folder_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in GOPRO_VIDEO_EXTENSIONS:
                        continue

                    rel_path = f"{folder_name}/{filename}"
                    if rel_path not in copied_files:
                        files_to_copy.append(rel_path)
                        try:
                            total_size += os.path.getsize(os.path.join(folder_path, filename))
                        except OSError:
                            pass
            except OSError as e:
                self.logger.warning(f"Error scanning folder {folder_path}: {e}")

        return files_to_copy, total_size

    def _append_to_copy_log(self, dcim_path: str, copied_files: list[str], job_uuid: str):
        """
        Append successfully copied files to the log on SD card.

        Args:
            dcim_path: Path to DCIM folder on SD card
            copied_files: List of relative paths that were copied
            job_uuid: UUID of the target folder
        """
        log_path = os.path.join(dcim_path, COPY_LOG_FILENAME)

        try:
            with open(log_path, 'a') as f:
                for rel_path in copied_files:
                    f.write(f"{rel_path} => {job_uuid}\n")

            # Set permissions (644)
            os.chmod(log_path, 0o644)
            self.logger.info(f"Updated copy log with {len(copied_files)} entries")
        except (IOError, OSError) as e:
            self.logger.error(f"Could not write to copy log {log_path}: {e}")


class StinercutDetector:
    """USB device detector that notifies backend of mount events."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.running = False
        self.monitoring_enabled = False  # Disabled by default, must be enabled via API
        self.shutdown_event = threading.Event()
        self.pending_events = {}  # device_node -> timestamp for debouncing
        self.ws = None  # WebSocket connection to backend
        self.ws_lock = threading.Lock()  # Thread-safe WebSocket access
        self.copy_manager = GoproCopyManager(self)  # GOPRO copy manager

    def _load_config(self, config_path: str = None) -> configparser.ConfigParser:
        """Load configuration from config.ini."""
        config = configparser.ConfigParser()

        if config_path is None:
            config_path = Path(__file__).parent / "config.ini"

        if os.path.exists(config_path):
            config.read(config_path)

        # Set defaults
        if "api" not in config:
            config["api"] = {}
        config["api"].setdefault("url", "http://localhost:8000")
        config["api"].setdefault("websocket_url", "ws://localhost:8002/ws?client_type=detector")

        if "detector" not in config:
            config["detector"] = {}
        config["detector"].setdefault("debounce_delay", "2.0")
        config["detector"].setdefault("mount_retries", "6")
        config["detector"].setdefault("mount_retry_interval", "0.5")
        config["detector"].setdefault("automount", "true")
        config["detector"].setdefault("mount_base", "/media/{user}")

        if "control" not in config:
            config["control"] = {}
        config["control"].setdefault("enabled", "false")
        config["control"].setdefault("host", "0.0.0.0")
        config["control"].setdefault("port", "8001")
        config["control"].setdefault("api_key", "")

        if "logging" not in config:
            config["logging"] = {}
        config["logging"].setdefault("file", "")
        config["logging"].setdefault("level", "INFO")

        if "gopro" not in config:
            config["gopro"] = {}
        config["gopro"].setdefault("auto_copy", "true")
        config["gopro"].setdefault("target_base", "/videodata/input")
        config["gopro"].setdefault("progress_interval", "10")

        return config

    def _setup_logging(self):
        """Configure logging based on config."""
        log_level = getattr(logging, self.config["logging"]["level"].upper(), logging.INFO)
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        handlers = [logging.StreamHandler()]

        log_file = self.config["logging"]["file"]
        if log_file:
            try:
                handlers.append(logging.FileHandler(log_file))
            except (IOError, PermissionError) as e:
                print(f"Warning: Could not open log file {log_file}: {e}", file=sys.stderr)

        logging.basicConfig(level=log_level, format=log_format, handlers=handlers)
        self.logger = logging.getLogger("stinercut-detector")

    def get_mount_point(self, device_node: str) -> str | None:
        """
        Look up mount point for a device from /proc/mounts.
        Retries if mount is delayed.
        """
        retries = int(self.config["detector"]["mount_retries"])
        interval = float(self.config["detector"]["mount_retry_interval"])

        for attempt in range(retries):
            try:
                with open("/proc/mounts", "r") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2 and parts[0] == device_node:
                            mount_path = parts[1]
                            # Decode octal-escaped characters from /proc/mounts (e.g., \040 for space)
                            # Note: /proc/mounts uses octal escapes like \040, not unicode escapes
                            import re
                            mount_path = re.sub(
                                r'\\([0-7]{3})',
                                lambda m: chr(int(m.group(1), 8)),
                                mount_path
                            )
                            self.logger.debug(f"Found mount point for {device_node}: {mount_path}")
                            return mount_path
            except IOError as e:
                self.logger.warning(f"Error reading /proc/mounts: {e}")

            if attempt < retries - 1:
                if self.shutdown_event.wait(interval):
                    self.logger.debug("Shutdown requested during mount point lookup")
                    return None

        self.logger.warning(f"No mount point found for {device_node} after {retries} retries")
        return None

    def get_device_label(self, device_node: str) -> str | None:
        """Get filesystem label for a device using blkid."""
        try:
            result = subprocess.run(
                ["blkid", "-s", "LABEL", "-o", "value", device_node],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"Failed to get label for {device_node}: {e}")
        return None

    def get_device_uuid(self, device_node: str) -> str | None:
        """Get filesystem UUID for a device using blkid."""
        try:
            result = subprocess.run(
                ["blkid", "-s", "UUID", "-o", "value", device_node],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"Failed to get UUID for {device_node}: {e}")
        return None

    def get_device_fstype(self, device_node: str) -> str | None:
        """Get filesystem type for a device using blkid."""
        try:
            result = subprocess.run(
                ["blkid", "-s", "TYPE", "-o", "value", device_node],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().lower()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"Failed to get filesystem type for {device_node}: {e}")
        return None

    def is_gopro_device(self, mount_path: str) -> tuple[bool, dict]:
        """
        Detect if mounted device is a GOPRO by checking for DCIM/xxxGOPRO folder pattern.

        Args:
            mount_path: Path where device is mounted

        Returns:
            Tuple of (is_gopro: bool, info: dict with gopro_folders, total_size, video_count)
        """
        result = {
            "gopro_folders": [],
            "total_size": 0,
            "video_count": 0,
        }

        try:
            dcim_path = os.path.join(mount_path, "DCIM")
            if not os.path.isdir(dcim_path):
                return False, result

            # Scan for xxxGOPRO folders
            for item in os.listdir(dcim_path):
                item_path = os.path.join(dcim_path, item)
                if os.path.isdir(item_path) and GOPRO_FOLDER_PATTERN.match(item):
                    result["gopro_folders"].append(item_path)

                    # Count video files and calculate total size
                    for f in os.listdir(item_path):
                        ext = os.path.splitext(f)[1].lower()
                        if ext in GOPRO_VIDEO_EXTENSIONS:
                            file_path = os.path.join(item_path, f)
                            try:
                                result["total_size"] += os.path.getsize(file_path)
                                result["video_count"] += 1
                            except OSError:
                                pass

            is_gopro = len(result["gopro_folders"]) > 0 and result["video_count"] > 0
            if is_gopro:
                self.logger.info(
                    f"GOPRO detected: {len(result['gopro_folders'])} folders, "
                    f"{result['video_count']} videos, "
                    f"{result['total_size'] / (1024**3):.2f} GB"
                )

            return is_gopro, result

        except PermissionError as e:
            self.logger.warning(f"Permission denied scanning {mount_path}: {e}")
            return False, result
        except OSError as e:
            self.logger.warning(f"Error scanning {mount_path}: {e}")
            return False, result

    def mount_device(self, device_node: str) -> str | None:
        """
        Automount a device and return the mount path.
        Applies appropriate mount options for user access based on filesystem type.
        """
        # Get label or UUID for mount point name
        label = self.get_device_label(device_node)
        uuid = self.get_device_uuid(device_node)
        fstype = self.get_device_fstype(device_node)

        if not label and not uuid:
            # Use device name as fallback (e.g., sda1)
            label = os.path.basename(device_node)

        mount_name = label or uuid[:8] if uuid else os.path.basename(device_node)
        # Sanitize mount name (remove special characters)
        mount_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in mount_name)

        # Get mount base path and target user
        mount_base = self.config["detector"]["mount_base"]
        mount_user = self.config["detector"].get("mount_user", "")

        # Resolve target user - prefer config, fall back to SUDO_USER or current user
        if not mount_user:
            mount_user = os.environ.get("SUDO_USER", getpass.getuser())

        mount_base = mount_base.format(user=mount_user)
        mount_path = os.path.join(mount_base, mount_name)

        # Get UID/GID for target user
        try:
            pw = pwd.getpwnam(mount_user)
            uid = pw.pw_uid
            gid = pw.pw_gid
        except KeyError:
            self.logger.warning(f"User '{mount_user}' not found, using uid/gid 1000")
            uid = 1000
            gid = 1000

        self.logger.info(f"Automounting {device_node} ({fstype}) to {mount_path} for user {mount_user} (uid={uid})")

        # Create mount point directory if it doesn't exist
        try:
            os.makedirs(mount_path, exist_ok=True)
        except PermissionError as e:
            self.logger.error(f"Failed to create mount point {mount_path}: {e}")
            return None

        # Build mount command with appropriate options based on filesystem type
        mount_cmd = ["mount"]

        # Filesystems that support uid/gid/umask mount options
        fat_like_fs = {"vfat", "fat", "msdos", "exfat"}
        ntfs_fs = {"ntfs", "ntfs3", "ntfs-3g"}

        if fstype in fat_like_fs:
            # FAT/exFAT: use uid, gid, umask for permissions
            mount_cmd.extend(["-o", f"uid={uid},gid={gid},umask=0002,dmask=0002,fmask=0002"])
        elif fstype in ntfs_fs:
            # NTFS: use uid, gid, umask (ntfs-3g or ntfs3)
            mount_cmd.extend(["-o", f"uid={uid},gid={gid},umask=0002,dmask=0002,fmask=0002"])
        # For native Linux filesystems (ext4, xfs, btrfs, etc.), we'll chown after mounting

        mount_cmd.extend([device_node, mount_path])

        result = subprocess.run(
            mount_cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            self.logger.error(f"Failed to mount {device_node}: {result.stderr}")
            # Clean up empty directory
            try:
                os.rmdir(mount_path)
            except OSError:
                pass
            return None

        # For native Linux filesystems, change ownership of mount point
        native_fs = {"ext2", "ext3", "ext4", "xfs", "btrfs", "f2fs"}
        if fstype in native_fs:
            try:
                os.chown(mount_path, uid, gid)
                self.logger.debug(f"Changed ownership of {mount_path} to {uid}:{gid}")
            except OSError as e:
                self.logger.warning(f"Could not change ownership of {mount_path}: {e}")

        self.logger.info(f"Successfully mounted {device_node} at {mount_path}")
        return mount_path

    def unmount_device(self, device_node: str) -> bool:
        """Unmount a device."""
        mount_path = self.get_mount_point(device_node)
        if not mount_path:
            return True  # Already unmounted

        self.logger.info(f"Unmounting {device_node} from {mount_path}")

        result = subprocess.run(
            ["umount", mount_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            self.logger.error(f"Failed to unmount {mount_path}: {result.stderr}")
            return False

        # Clean up mount point directory
        try:
            os.rmdir(mount_path)
            self.logger.debug(f"Removed mount point directory: {mount_path}")
        except OSError as e:
            self.logger.debug(f"Could not remove mount point directory {mount_path}: {e}")

        return True

    def _send_ws_message(self, command: str, data: dict, target: str = "all"):
        """Send a message via WebSocket to backend hub."""
        with self.ws_lock:
            if self.ws is None:
                self.logger.warning(f"WebSocket not connected, cannot send: {command}")
                return

            message = json.dumps({
                "command": command,
                "sender": "detector",
                "target": target,
                "data": data,
            })
            try:
                self.ws.send(message)
                self.logger.debug(f"WebSocket sent: {command}")
            except Exception as e:
                self.logger.warning(f"Failed to send WebSocket message: {e}")
                self.ws = None  # Mark as disconnected

    def notify_mount(self, device_node: str, mount_path: str):
        """Send mount notification to frontend via WebSocket."""
        self.logger.info(f"Notifying frontend of mount: {device_node} -> {mount_path}")
        self._send_ws_message("device.mounted", {
            "device_node": device_node,
            "mount_path": mount_path,
        })

    def notify_unmount(self, device_node: str):
        """Send unmount notification to frontend via WebSocket."""
        self.logger.info(f"Notifying frontend of unmount: {device_node}")
        self._send_ws_message("device.unmounted", {
            "device_node": device_node,
        })

    def send_status(self):
        """Send current status to frontend via WebSocket."""
        self.logger.debug(f"Sending status: running={self.running}, monitoring_enabled={self.monitoring_enabled}")
        self._send_ws_message("detector.status", {
            "running": self.running,
            "monitoring_enabled": self.monitoring_enabled,
            "pending_events": len(self.pending_events),
        })

    def rename_sd_folder(self, mount_path: str, old_folder: str, new_folder: str):
        """
        Rename folder on SD card (from IMPORT_UUID to CLIENT_NAME_UUID).

        Args:
            mount_path: SD card mount path (e.g., /media/stiner/06D8-6152)
            old_folder: Current folder name (IMPORT_UUID)
            new_folder: New folder name (CLIENT_NAME_UUID)
        """
        old_path = os.path.join(mount_path, old_folder)
        new_path = os.path.join(mount_path, new_folder)

        if not os.path.exists(old_path):
            self.logger.warning(f"SD folder not found: {old_path}")
            self._send_ws_message("gopro.sd_rename_failed", {
                "mount_path": mount_path,
                "old_folder": old_folder,
                "new_folder": new_folder,
                "error": f"Folder not found: {old_folder}"
            })
            return

        if os.path.exists(new_path):
            self.logger.warning(f"Target folder already exists: {new_path}")
            self._send_ws_message("gopro.sd_rename_failed", {
                "mount_path": mount_path,
                "old_folder": old_folder,
                "new_folder": new_folder,
                "error": f"Target folder already exists: {new_folder}"
            })
            return

        try:
            os.rename(old_path, new_path)
            self.logger.info(f"Renamed SD folder: {old_folder} -> {new_folder}")
            self._send_ws_message("gopro.sd_renamed", {
                "mount_path": mount_path,
                "old_folder": old_folder,
                "new_folder": new_folder,
            })

            # Safely unmount SD card after successful rename
            self._safe_unmount(mount_path)

        except (PermissionError, OSError) as e:
            self.logger.error(f"Failed to rename SD folder: {e}")
            self._send_ws_message("gopro.sd_rename_failed", {
                "mount_path": mount_path,
                "old_folder": old_folder,
                "new_folder": new_folder,
                "error": str(e)
            })

    def _safe_unmount(self, mount_path: str):
        """Safely unmount SD card using udisksctl."""
        import subprocess

        try:
            # Sync filesystem first
            subprocess.run(["sync"], check=True, timeout=30)

            # Use udisksctl to safely unmount (handles all the cleanup)
            result = subprocess.run(
                ["udisksctl", "unmount", "-b", self._get_block_device(mount_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info(f"SD card safely unmounted: {mount_path}")
                self._send_ws_message("gopro.sd_unmounted", {
                    "mount_path": mount_path,
                })
            elif "NotMounted" in result.stderr:
                # Already unmounted - treat as success
                self.logger.info(f"SD card already unmounted: {mount_path}")
                self._send_ws_message("gopro.sd_unmounted", {
                    "mount_path": mount_path,
                })
            else:
                self.logger.warning(f"Failed to unmount SD card: {result.stderr}")
                self._send_ws_message("gopro.sd_unmount_failed", {
                    "mount_path": mount_path,
                    "error": result.stderr.strip()
                })

        except subprocess.TimeoutExpired:
            self.logger.error(f"Unmount timed out for {mount_path}")
            self._send_ws_message("gopro.sd_unmount_failed", {
                "mount_path": mount_path,
                "error": "Unmount timed out"
            })
        except Exception as e:
            self.logger.error(f"Error unmounting SD card: {e}")
            self._send_ws_message("gopro.sd_unmount_failed", {
                "mount_path": mount_path,
                "error": str(e)
            })

    def _get_block_device(self, mount_path: str) -> str:
        """Get block device from mount path using /proc/mounts."""
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == mount_path:
                        return parts[0]
        except Exception as e:
            self.logger.warning(f"Error reading /proc/mounts: {e}")

        # Fallback: try to find device from mount_path pattern
        # e.g., /media/stiner/06D8-6152 -> look for matching device
        import subprocess
        result = subprocess.run(
            ["findmnt", "-n", "-o", "SOURCE", mount_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()

        raise ValueError(f"Could not find block device for {mount_path}")

    def _start_websocket_client(self):
        """Start WebSocket client connection in background thread."""
        ws_url = self.config["api"]["websocket_url"]
        detector = self

        def on_open(ws):
            detector.logger.info(f"WebSocket connected to {ws_url}")
            with detector.ws_lock:
                detector.ws = ws

        def on_close(ws, close_status_code, close_msg):
            detector.logger.info(f"WebSocket disconnected: {close_status_code} {close_msg}")
            with detector.ws_lock:
                detector.ws = None

        def on_error(ws, error):
            detector.logger.warning(f"WebSocket error: {error}")

        def on_message(ws, message):
            """Handle incoming WebSocket messages (commands from frontend)."""
            try:
                data = json.loads(message)
            except json.JSONDecodeError as e:
                detector.logger.warning(f"Invalid JSON received: {e}")
                return

            # Ignore messages from self
            if data.get("sender") == "detector":
                return

            command = data.get("command", "")
            detector.logger.debug(f"WebSocket received: {command}")

            if command == "detector:status":
                detector.send_status()
            elif command == "detector:enable":
                detector.monitoring_enabled = True
                detector.logger.info("Monitoring enabled via WebSocket")
                detector.send_status()
            elif command == "detector:disable":
                detector.monitoring_enabled = False
                detector.logger.info("Monitoring disabled via WebSocket")
                detector.send_status()
            elif command == "gopro.organize_sd":
                # Rename SD card folder from old_folder to new_folder
                msg_data = data.get("data", {})
                mount_path = msg_data.get("mount_path")
                old_folder = msg_data.get("old_folder")
                new_folder = msg_data.get("new_folder")
                if mount_path and old_folder and new_folder:
                    detector.rename_sd_folder(mount_path, old_folder, new_folder)
                else:
                    detector.logger.warning(f"gopro.organize_sd missing data: {msg_data}")
            else:
                detector.logger.debug(f"Unknown command: {command}")

        def run_websocket():
            """Run WebSocket connection with auto-reconnect."""
            reconnect_delay = 5
            while detector.running:
                try:
                    detector.logger.info(f"Connecting to WebSocket: {ws_url}")
                    ws = websocket.WebSocketApp(
                        ws_url,
                        on_open=on_open,
                        on_close=on_close,
                        on_error=on_error,
                        on_message=on_message,
                    )
                    ws.run_forever()
                except Exception as e:
                    detector.logger.warning(f"WebSocket connection error: {e}")

                if detector.running:
                    detector.logger.info(f"Reconnecting in {reconnect_delay}s...")
                    if detector.shutdown_event.wait(reconnect_delay):
                        break

            detector.logger.info("WebSocket client stopped")

        thread = threading.Thread(target=run_websocket, daemon=True)
        thread.start()
        self.logger.debug("WebSocket client thread started")

    def _start_control_server(self):
        """Start HTTP control server in background thread."""
        if not self.config["control"].getboolean("enabled", False):
            self.logger.debug("HTTP control server disabled")
            return

        host = self.config["control"]["host"]
        port = int(self.config["control"]["port"])
        api_key = self.config["control"]["api_key"]

        detector = self

        class ControlHandler(BaseHTTPRequestHandler):
            """HTTP request handler for control API."""

            def log_message(self, format, *args):
                """Override to use detector's logger."""
                detector.logger.debug(f"HTTP: {format % args}")

            def _check_api_key(self) -> bool:
                """Check API key if configured."""
                if not api_key:
                    return True
                request_key = self.headers.get("X-API-Key", "")
                return request_key == api_key

            def _send_cors_headers(self):
                """Send CORS headers for cross-origin requests."""
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")

            def _send_json(self, data: dict, status: int = 200):
                """Send JSON response."""
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def do_OPTIONS(self):
                """Handle CORS preflight requests."""
                self.send_response(204)
                self._send_cors_headers()
                self.end_headers()

            def do_GET(self):
                """Handle GET requests."""
                if not self._check_api_key():
                    self._send_json({"error": "Unauthorized"}, 401)
                    return

                if self.path == "/status":
                    status = {
                        "running": detector.running,
                        "monitoring_enabled": detector.monitoring_enabled,
                        "pending_events": len(detector.pending_events),
                        "service": "stinercut-detector",
                    }
                    self._send_json(status)
                else:
                    self._send_json({"error": "Not found"}, 404)

            def do_POST(self):
                """Handle POST requests."""
                if not self._check_api_key():
                    self._send_json({"error": "Unauthorized"}, 401)
                    return

                if self.path == "/control/stop":
                    detector.logger.info("Stop requested via HTTP API")
                    detector.running = False
                    detector.shutdown_event.set()
                    self._send_json({"status": "stopping"})

                elif self.path == "/control/restart":
                    detector.logger.info("Restart requested via HTTP API")
                    detector.running = False
                    detector.shutdown_event.set()
                    # Clean exit with code 0 - systemd will restart
                    self._send_json({"status": "restarting"})

                elif self.path == "/control/enable":
                    detector.logger.info("Monitoring enabled via HTTP API")
                    detector.monitoring_enabled = True
                    self._send_json({"status": "enabled", "monitoring_enabled": True})
                    # Notify frontend via WebSocket
                    threading.Thread(target=detector.send_status, daemon=True).start()

                elif self.path == "/control/disable":
                    detector.logger.info("Monitoring disabled via HTTP API")
                    detector.monitoring_enabled = False
                    self._send_json({"status": "disabled", "monitoring_enabled": False})
                    # Notify frontend via WebSocket
                    threading.Thread(target=detector.send_status, daemon=True).start()

                else:
                    self._send_json({"error": "Not found"}, 404)

        def run_server():
            """Run the HTTP server loop."""
            try:
                server = HTTPServer((host, port), ControlHandler)
                server.timeout = 1.0
                detector.logger.info(f"HTTP control server listening on {host}:{port}")

                while detector.running:
                    server.handle_request()

                detector.logger.info("HTTP control server stopped")
            except Exception as e:
                detector.logger.error(f"HTTP control server error: {e}", exc_info=True)

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        self.logger.debug("HTTP control server thread started")

    def handle_device_event(self, device: pyudev.Device):
        """Handle a udev device event."""
        action = device.action
        device_node = device.device_node
        device_type = device.device_type

        self.logger.debug(f"Device event: action={action}, node={device_node}, type={device_type}")

        # Check if monitoring is enabled
        if not self.monitoring_enabled:
            self.logger.debug(f"Monitoring disabled, ignoring event: {device_node}")
            return

        # Only process partition events
        if device_type != "partition":
            self.logger.debug(f"Ignoring non-partition device: {device_node}")
            return

        if action == "add":
            # Debounce: record timestamp and wait
            debounce_delay = float(self.config["detector"]["debounce_delay"])
            self.pending_events[device_node] = time.time()

            self.logger.debug(f"Scheduling device add processing in {debounce_delay}s: {device_node}")
            if self.shutdown_event.wait(debounce_delay):
                self.logger.debug(f"Shutdown requested, aborting device processing for {device_node}")
                return

            # Check if this event is still pending (not superseded)
            if device_node not in self.pending_events:
                self.logger.debug(f"Event for {device_node} was cancelled")
                return

            del self.pending_events[device_node]

            # Check if already mounted
            mount_path = self.get_mount_point(device_node)

            # If not mounted and automount is enabled, mount it
            if not mount_path:
                automount = self.config["detector"].getboolean("automount", True)
                if automount:
                    self.logger.info(f"Device {device_node} not mounted, automounting...")
                    mount_path = self.mount_device(device_node)

            if mount_path:
                self.notify_mount(device_node, mount_path)

                # Check for GOPRO device and auto-start copy if enabled
                if self.config["gopro"].getboolean("auto_copy", True):
                    is_gopro, gopro_info = self.is_gopro_device(mount_path)
                    if is_gopro:
                        self.logger.info(f"GOPRO detected at {mount_path}, starting auto-copy...")
                        job_id = self.copy_manager.start_copy(mount_path, device_node, gopro_info)
                        self.logger.info(f"GOPRO copy started with job ID: {job_id}")
            else:
                self.logger.warning(f"Device {device_node} has no mount point, skipping")

        elif action == "remove":
            # Cancel any pending add event for this device
            if device_node in self.pending_events:
                del self.pending_events[device_node]
                self.logger.debug(f"Cancelled pending add event for {device_node}")

            self.notify_unmount(device_node)

    def run(self):
        """Main loop: monitor udev events."""
        self.logger.info("Starting Stinercut Media Detector")
        self.logger.info(f"Backend API URL: {self.config['api']['url']}")

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="block")

        self.running = True

        # Start WebSocket client connection
        self._start_websocket_client()

        # Start HTTP control server if enabled
        self._start_control_server()

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            self.shutdown_event.set()  # Wake up any waiting calls

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self.logger.info("Monitoring for USB device events...")

        while self.running:
            device = monitor.poll(timeout=1.0)
            if device is None:
                continue
            if not self.running:
                break
            try:
                self.handle_device_event(device)
            except Exception as e:
                self.logger.error(f"Error handling device event: {e}", exc_info=True)

        self.logger.info("Stinercut Media Detector stopped")


def main():
    """Entry point."""
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    detector = StinercutDetector(config_path)
    detector.run()


if __name__ == "__main__":
    main()
