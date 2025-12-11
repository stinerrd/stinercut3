"""
Jump Resolver service.
Handles jump splitting and folder organization based on QR codes and freefall detection.
"""
import os
import shutil
from typing import List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path

from models.video_file import VideoFile
from models.video_file_segment import VideoFileSegment


@dataclass
class JumpMapping:
    """Mapping of files to a workload."""
    workload_uuid: str
    files: List[VideoFile] = field(default_factory=list)


@dataclass
class ResolutionResult:
    """Result of jump resolution."""
    status: str  # resolved, needs_manual
    resolution_type: str  # auto_single, auto_multi, missing_qr, ambiguous
    message: Optional[str] = None
    mappings: List[JumpMapping] = field(default_factory=list)
    detected_qr_uuids: List[str] = field(default_factory=list)
    freefall_count: int = 0


class JumpResolver:
    """
    Resolves jump assignments based on QR codes and freefall detection.
    Handles file organization into workload folders.
    """

    def __init__(self, base_path: str):
        """
        Args:
            base_path: Base path for video files (e.g., /videodata/input)
        """
        self.base_path = Path(base_path)

    def count_freefall_segments(self, files: List[VideoFile]) -> int:
        """
        Count total freefall segments across all files.
        Considers consecutive freefall segments in adjacent files as one jump.
        """
        # Sort files by recorded_at
        sorted_files = sorted(files, key=lambda f: f.recorded_at or f.created_at)

        freefall_count = 0
        in_freefall_sequence = False

        for file in sorted_files:
            has_freefall = file.dominant_classification == 'freefall'

            if has_freefall and not in_freefall_sequence:
                # New freefall sequence starts
                freefall_count += 1
                in_freefall_sequence = True
            elif not has_freefall and file.dominant_classification in ('canopy', 'ground_after'):
                # Freefall sequence ends
                in_freefall_sequence = False

        return freefall_count

    def resolve_jumps(self, files: List[VideoFile]) -> ResolutionResult:
        """
        Determine how to organize videos based on QR codes and freefall detection.

        Args:
            files: List of analyzed VideoFile objects

        Returns:
            ResolutionResult with status and actions
        """
        # Count unique workload UUIDs from QR codes
        qr_uuids: Set[str] = set()
        for f in files:
            if f.detected_workload_uuid:
                qr_uuids.add(f.detected_workload_uuid)

        # Count freefall segments
        freefall_count = self.count_freefall_segments(files)

        qr_count = len(qr_uuids)

        # CASE 1: Single QR + Single Freefall → Auto-resolve
        if qr_count == 1 and freefall_count == 1:
            workload_uuid = list(qr_uuids)[0]
            return ResolutionResult(
                status='resolved',
                resolution_type='auto_single',
                mappings=[JumpMapping(workload_uuid=workload_uuid, files=files)],
                detected_qr_uuids=list(qr_uuids),
                freefall_count=freefall_count
            )

        # CASE 2: Multiple QRs matching Multiple Freefalls → Auto-split
        if qr_count == freefall_count and qr_count > 1:
            mappings = self._map_qr_to_freefalls(files)
            return ResolutionResult(
                status='resolved',
                resolution_type='auto_multi',
                mappings=mappings,
                detected_qr_uuids=list(qr_uuids),
                freefall_count=freefall_count
            )

        # CASE 3: No QR detected but single freefall → Needs manual QR
        if qr_count == 0 and freefall_count == 1:
            return ResolutionResult(
                status='needs_manual',
                resolution_type='missing_qr',
                message='Single jump detected but no QR code found. Manual workload assignment needed.',
                detected_qr_uuids=[],
                freefall_count=freefall_count
            )

        # CASE 4: Ambiguous (mismatched counts) → Needs manual resolution
        return ResolutionResult(
            status='needs_manual',
            resolution_type='ambiguous',
            message=f'Found {qr_count} QR codes but {freefall_count} freefalls. Manual splitting required.',
            detected_qr_uuids=list(qr_uuids),
            freefall_count=freefall_count
        )

    def _map_qr_to_freefalls(self, files: List[VideoFile]) -> List[JumpMapping]:
        """
        Map QR codes to freefall segments based on video sequence.

        Logic: Files are ordered by recording time. Each QR code "claims"
        the freefall that follows it until the next QR code.
        """
        # Sort files by recorded_at timestamp
        sorted_files = sorted(files, key=lambda f: f.recorded_at or f.created_at)

        mappings = []
        current_qr: Optional[str] = None
        current_jump_files: List[VideoFile] = []

        for file in sorted_files:
            if file.detected_workload_uuid and file.detected_workload_uuid != current_qr:
                # New QR found - save previous group if exists
                if current_qr and current_jump_files:
                    mappings.append(JumpMapping(
                        workload_uuid=current_qr,
                        files=current_jump_files.copy()
                    ))
                current_qr = file.detected_workload_uuid
                current_jump_files = [file]
            else:
                current_jump_files.append(file)

        # Don't forget the last group
        if current_qr and current_jump_files:
            mappings.append(JumpMapping(
                workload_uuid=current_qr,
                files=current_jump_files
            ))

        return mappings

    def move_files_to_workload(
        self,
        files: List[VideoFile],
        workload_uuid: str,
        source_folder_uuid: str
    ) -> bool:
        """
        Move files from source folder to workload folder.

        Args:
            files: List of VideoFile objects to move
            workload_uuid: Target workload UUID (new folder name)
            source_folder_uuid: Source folder UUID

        Returns:
            True if successful, False otherwise
        """
        source_dir = self.base_path / source_folder_uuid
        target_dir = self.base_path / workload_uuid

        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            for file in files:
                source_path = self.base_path / file.filepath
                target_path = target_dir / file.original_filename

                if source_path.exists():
                    shutil.move(str(source_path), str(target_path))

                    # Update file record
                    file.current_folder_uuid = workload_uuid
                    file.filepath = f"{workload_uuid}/{file.original_filename}"

            # Remove empty source directory
            if source_dir.exists() and not any(source_dir.iterdir()):
                source_dir.rmdir()

            return True

        except Exception as e:
            print(f"Error moving files: {e}")
            return False

    def execute_resolution(self, result: ResolutionResult, source_folder_uuid: str) -> bool:
        """
        Execute the resolution result (move files to workload folders).

        Args:
            result: ResolutionResult from resolve_jumps()
            source_folder_uuid: Original import folder UUID

        Returns:
            True if successful, False otherwise
        """
        if result.status != 'resolved':
            return False

        success = True
        for mapping in result.mappings:
            if not self.move_files_to_workload(
                mapping.files,
                mapping.workload_uuid,
                source_folder_uuid
            ):
                success = False

        return success
