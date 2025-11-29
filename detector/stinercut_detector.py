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
import signal
import subprocess
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import pyudev
import requests


class StinercutDetector:
    """USB device detector that notifies backend of mount events."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.running = False
        self.monitoring_enabled = False  # Disabled by default, must be enabled via API
        self.shutdown_event = threading.Event()
        self.pending_events = {}  # device_node -> timestamp for debouncing

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
                            # Decode escaped characters (e.g., \040 for space)
                            mount_path = mount_path.encode().decode("unicode_escape")
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

    def notify_mount(self, device_node: str, mount_path: str):
        """Send mount notification to backend API."""
        api_url = self.config["api"]["url"].rstrip("/")
        url = f"{api_url}/api/devices/mount"

        payload = {
            "device_node": device_node,
            "mount_path": mount_path,
        }

        self.logger.info(f"Notifying backend of mount: {device_node} -> {mount_path}")

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Backend notified successfully: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Failed to connect to backend API: {e}")
        except requests.exceptions.Timeout:
            self.logger.error("Backend API request timed out")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Backend API returned error: {e}")

    def notify_unmount(self, device_node: str):
        """Send unmount notification to backend API."""
        api_url = self.config["api"]["url"].rstrip("/")
        url = f"{api_url}/api/devices/unmount"

        payload = {
            "device_node": device_node,
        }

        self.logger.info(f"Notifying backend of unmount: {device_node}")

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Backend notified successfully: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Failed to connect to backend API: {e}")
        except requests.exceptions.Timeout:
            self.logger.error("Backend API request timed out")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Backend API returned error: {e}")

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

            def _send_json(self, data: dict, status: int = 200):
                """Send JSON response."""
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

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

                elif self.path == "/control/disable":
                    detector.logger.info("Monitoring disabled via HTTP API")
                    detector.monitoring_enabled = False
                    self._send_json({"status": "disabled", "monitoring_enabled": False})

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
