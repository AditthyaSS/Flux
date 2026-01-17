"""
Async file writer with resume support.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Optional

import aiofiles


class AsyncFileWriter:
    """
    Handles concurrent chunk writes with resume capability.
    """
    
    def __init__(self, filepath: str, total_size: int) -> None:
        """
        Initialize file writer.
        
        Args:
            filepath: Destination file path
            total_size: Total file size in bytes
        """
        self.filepath = Path(filepath)
        self.total_size = total_size
        self.partial_path = Path(f"{filepath}.flux.partial")
        self.metadata_path = Path(f"{filepath}.flux.meta")
        self._lock = asyncio.Lock()
        self._file_handle: Optional[asyncio.streams.StreamWriter] = None
    
    async def initialize(self) -> tuple[int, Dict[int, int]]:
        """
        Initialize file for writing. Resume if partial file exists.
        
        Returns:
            Tuple of (bytes_downloaded, completed_chunks_map)
        """
        # Check for existing partial download
        bytes_downloaded = 0
        completed_chunks = {}
        
        if self.partial_path.exists() and self.metadata_path.exists():
            # Resume mode
            try:
                async with aiofiles.open(self.metadata_path, "r") as f:
                    metadata_str = await f.read()
                    metadata = json.loads(metadata_str)
                    bytes_downloaded = metadata.get("bytes_downloaded", 0)
                    
                    # Restore completed chunks map
                    chunks_data = metadata.get("chunks", {})
                    completed_chunks = {int(k): v for k, v in chunks_data.items()}
                    
                    # Verify total size matches
                    if metadata.get("total_size") != self.total_size:
                        # File size mismatch, start fresh
                        bytes_downloaded = 0
                        completed_chunks = {}
                        await self._create_fresh()
                    # else: valid resume
            except Exception:
                # Metadata corrupted, start fresh
                bytes_downloaded = 0
                completed_chunks = {}
                await self._create_fresh()
        else:
            # Fresh download
            await self._create_fresh()
        
        return bytes_downloaded, completed_chunks
    
    async def _create_fresh(self) -> None:
        """Create a fresh partial file."""
        # Delete any existing partial/metadata
        if self.partial_path.exists():
            self.partial_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()
        
        # Create directory if needed
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Pre-allocate file (sparse on Unix, may not work on all systems)
        async with aiofiles.open(self.partial_path, "wb") as f:
            if self.total_size > 0:
                await f.seek(self.total_size - 1)
                await f.write(b"\0")
    
    async def write_chunk(self, offset: int, data: bytes) -> None:
        """
        Write a chunk at the specified offset.
        
        Args:
            offset: Byte offset to write at
            data: Chunk data
        """
        async with self._lock:
            async with aiofiles.open(self.partial_path, "r+b") as f:
                await f.seek(offset)
                await f.write(data)
    
    async def save_metadata(self, bytes_downloaded: int, chunks: Dict[int, int]) -> None:
        """
        Save resume metadata.
        
        Args:
            bytes_downloaded: Total bytes downloaded
            chunks: Dictionary of {offset: size} for completed chunks
        """
        metadata = {
            "bytes_downloaded": bytes_downloaded,
            "total_size": self.total_size,
            "chunks": {str(k): v for k, v in chunks.items()},
        }
        
        async with aiofiles.open(self.metadata_path, "w") as f:
            await f.write(json.dumps(metadata))
    
    async def finalize(self) -> None:
        """
        Finalize download: rename partial to final and clean up metadata.
        """
        async with self._lock:
            # Rename partial to final
            if self.partial_path.exists():
                # Remove final file if it exists
                if self.filepath.exists():
                    self.filepath.unlink()
                
                self.partial_path.rename(self.filepath)
            
            # Remove metadata
            if self.metadata_path.exists():
                self.metadata_path.unlink()
    
    async def cleanup(self) -> None:
        """Clean up partial files (on cancel/error)."""
        if self.partial_path.exists():
            self.partial_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()
