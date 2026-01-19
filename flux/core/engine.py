"""
Main adaptive download engine.
"""

import asyncio
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

from flux.core.decisions import Decision, DecisionEngine
from flux.core.metrics import DownloadMetrics
from flux.network.client import AdaptiveHTTPClient
from flux.storage.writer import AsyncFileWriter


class DownloadStatus(Enum):
    """Download status states."""
    QUEUED = "queued"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a download task."""
    
    id: str
    url: str
    filepath: str
    filename: str
    total_size: int
    status: DownloadStatus
    supports_ranges: bool
    metrics: DownloadMetrics
    error_message: Optional[str] = None
    
    # Adaptive parameters
    chunk_size: int = 1024 * 1024  # 1MB default
    num_connections: int = 8  # Start with 8 for performance


class AdaptiveDownloadEngine:
    """
    Core download engine with adaptive intelligence.
    Emits events for UI consumption.
    """
    
    def __init__(self) -> None:
        """Initialize download engine."""
        self.downloads: Dict[str, DownloadTask] = {}
        self.decision_engine = DecisionEngine()
        self._event_callbacks: List[Callable] = []
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._http_client: Optional[AdaptiveHTTPClient] = None
        self._stopped: bool = False
    
    def on_event(self, callback: Callable) -> None:
        """
        Register event callback.
        
        Args:
            callback: Function to call on events
        """
        self._event_callbacks.append(callback)
    
    def _emit_event(self, event_type: str, data: dict) -> None:
        """
        Emit event to all registered callbacks.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        for callback in self._event_callbacks:
            try:
                callback(event_type, data)
            except Exception:
                pass  # Don't let callback errors break engine
    
    async def start(self) -> None:
        """Start the engine."""
        self._http_client = AdaptiveHTTPClient()
        await self._http_client.__aenter__()
        self._emit_event("engine_started", {})
    
    async def stop(self) -> None:
        """Stop the engine and cleanup."""
        if self._stopped:
            return  # Already stopped
        self._stopped = True
        
        # Cancel all active downloads
        for task_id in list(self._active_tasks.keys()):
            try:
                await self.cancel_download(task_id)
            except Exception:
                pass
        
        # Close HTTP client
        if self._http_client:
            try:
                await self._http_client.__aexit__(None, None, None)
            except Exception:
                pass
            self._http_client = None
        
        self._emit_event("engine_stopped", {})
    
    async def add_download(
        self, url: str, output_dir: str, filename: Optional[str] = None, auto_start: bool = True
    ) -> str:
        """
        Add a new download.
        
        Args:
            url: Download URL
            output_dir: Output directory
            filename: Optional custom filename
        
        Returns:
            Download ID
        """
        if not self._http_client:
            raise RuntimeError("Engine not started")
        
        # Get file info
        try:
            total_size, supports_ranges, detected_filename = (
                await self._http_client.get_file_info(url)
            )
        except Exception as e:
            download_id = str(uuid.uuid4())
            self._emit_event(
                "download_failed",
                {"download_id": download_id, "url": url, "error": str(e)},
            )
            raise
        
        # Use provided filename or detected
        final_filename = filename or detected_filename
        filepath = str(Path(output_dir) / final_filename)
        
        # Create download task
        download_id = str(uuid.uuid4())
        metrics = DownloadMetrics(download_id=download_id, total_size=total_size)
        
        task = DownloadTask(
            id=download_id,
            url=url,
            filepath=filepath,
            filename=final_filename,
            total_size=total_size,
            status=DownloadStatus.QUEUED,
            supports_ranges=supports_ranges,
            metrics=metrics,
        )
        
        self.downloads[download_id] = task
        
        self._emit_event(
            "download_added",
            {
                "download_id": download_id,
                "url": url,
                "filename": final_filename,
                "size": total_size,
                "supports_ranges": supports_ranges,
            },
        )
        
        # Only auto-start if requested
        if auto_start:
            await self.start_download(download_id)
        
        return download_id
    
    async def start_download(self, download_id: str) -> None:
        """
        Start a queued or paused download.
        
        Args:
            download_id: Download ID
        """
        task = self.downloads.get(download_id)
        if not task or task.status not in (DownloadStatus.QUEUED, DownloadStatus.PAUSED):
            return
        
        task.status = DownloadStatus.ACTIVE
        self._emit_event("download_started", {"download_id": download_id})
        
        # Create async task
        async_task = asyncio.create_task(self._download_worker(download_id))
        self._active_tasks[download_id] = async_task
    
    async def pause_download(self, download_id: str) -> None:
        """Pause an active download."""
        task = self.downloads.get(download_id)
        if not task or task.status != DownloadStatus.ACTIVE:
            return
        
        # Cancel async task if it exists
        async_task = self._active_tasks.get(download_id)
        if async_task:
            async_task.cancel()
            try:
                await async_task
            except asyncio.CancelledError:
                pass
            # Remove from active tasks (use pop to avoid KeyError)
            self._active_tasks.pop(download_id, None)
        
        task.status = DownloadStatus.PAUSED
        self._emit_event("download_paused", {"download_id": download_id})
    
    async def cancel_download(self, download_id: str) -> None:
        """Cancel a download and clean up files."""
        task = self.downloads.get(download_id)
        if not task:
            return
        
        # Cancel if active
        async_task = self._active_tasks.get(download_id)
        if async_task:
            async_task.cancel()
            try:
                await async_task
            except asyncio.CancelledError:
                pass
            # Remove from active tasks (use pop to avoid KeyError)
            self._active_tasks.pop(download_id, None)
        
        # Clean up files
        writer = AsyncFileWriter(task.filepath, task.total_size)
        await writer.cleanup()
        
        task.status = DownloadStatus.CANCELLED
        self._emit_event("download_cancelled", {"download_id": download_id})
    
    async def delete_download(self, download_id: str, delete_files: bool = False) -> bool:
        """
        Delete a download from the list and optionally from disk.
        
        Args:
            download_id: Download ID
            delete_files: If True, also delete downloaded files from disk
            
        Returns:
            True if download was deleted, False otherwise
        """
        task = self.downloads.get(download_id)
        if not task:
            return False
        
        filename = task.filename
        filepath = task.filepath
        
        # Cancel if active
        if task.status == DownloadStatus.ACTIVE:
            async_task = self._active_tasks.get(download_id)
            if async_task:
                async_task.cancel()
                try:
                    await async_task
                except asyncio.CancelledError:
                    pass
                self._active_tasks.pop(download_id, None)
        
        # Delete files from disk if requested
        if delete_files:
            try:
                writer = AsyncFileWriter(filepath, task.total_size)
                await writer.cleanup()
                
                # Also try to delete the actual file if it exists
                file_path = Path(filepath)
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass  # File might not exist or be inaccessible
        
        # Remove from downloads dict
        del self.downloads[download_id]
        
        self._emit_event(
            "download_deleted",
            {
                "download_id": download_id,
                "filename": filename,
                "delete_files": delete_files,
            },
        )
        
        return True
    
    async def _download_worker(self, download_id: str) -> None:
        """
        Worker coroutine that performs the download.
        
        Args:
            download_id: Download ID
        """
        task = self.downloads[download_id]
        writer = AsyncFileWriter(task.filepath, task.total_size)
        
        try:
            # Initialize file (may resume) and get completed chunks
            bytes_downloaded, completed_chunks = await writer.initialize()
            task.metrics.bytes_downloaded = bytes_downloaded
            
            # Auto-scale chunk size based on file size
            if task.total_size > 1024 * 1024 * 1024:  # >1GB
                task.chunk_size = 16 * 1024 * 1024  # 16MB
            elif task.total_size > 100 * 1024 * 1024:  # >100MB
                task.chunk_size = 8 * 1024 * 1024  # 8MB
            else:
                task.chunk_size = 1 * 1024 * 1024  # 1MB
            
            if task.supports_ranges:
                await self._download_multipart(task, writer, completed_chunks)
            else:
                await self._download_full(task, writer)
            
            # Finalize
            await writer.finalize()
            task.status = DownloadStatus.COMPLETED
            
            self._emit_event(
                "download_completed",
                {
                    "download_id": download_id,
                    "filepath": task.filepath,
                    "size": task.total_size,
                },
            )
        
        except asyncio.CancelledError:
            # Save complete state for resume: chunk map, metrics, parameters
            chunk_map = getattr(writer, '_completed_chunks', {})
            metadata = {
                'bytes_downloaded': task.metrics.bytes_downloaded,
                'chunks': chunk_map,
                'chunk_size': task.chunk_size,
                'num_connections': task.num_connections,
            }
            await writer.save_metadata(task.metrics.bytes_downloaded, chunk_map)
            raise
        
        except Exception as e:
            task.status = DownloadStatus.FAILED
            task.error_message = str(e)
            
            self._emit_event(
                "download_failed",
                {"download_id": download_id, "error": str(e)},
            )
        
        finally:
            if download_id in self._active_tasks:
                del self._active_tasks[download_id]
    
    async def _download_multipart(
        self, task: DownloadTask, writer: AsyncFileWriter, completed_chunks: Dict[int, int] = None
    ) -> None:
        """Download using multiple connections."""
        if completed_chunks is None:
            completed_chunks = {}
        
        # Track completed chunks for resume
        writer._completed_chunks = completed_chunks.copy()
        
        remaining = task.total_size - task.metrics.bytes_downloaded
        
        while remaining > 0:
            # Check for adaptive decisions
            decisions = self.decision_engine.analyze(
                task.metrics,
                task.chunk_size,
                task.num_connections,
                task.supports_ranges,
            )
            
            # Apply decisions
            for decision in decisions:
                await self._apply_decision(task, decision)
            
            # Create chunk tasks - skip already completed chunks
            chunks_to_download = []
            offset = 0
            
            while offset < task.total_size:
                chunk_size = min(task.chunk_size, task.total_size - offset)
                
                # Check if this chunk is already downloaded
                if offset not in writer._completed_chunks:
                    chunks_to_download.append((offset, chunk_size))
                    
                    # Limit concurrent downloads
                    if len(chunks_to_download) >= task.num_connections:
                        break
                
                offset += chunk_size
            
            if not chunks_to_download:
                break  # All chunks downloaded
            
            # Download chunks in parallel
            chunk_tasks = [
                self._download_and_write_chunk(task, writer, offset, size)
                for offset, size in chunks_to_download
            ]
            
            await asyncio.gather(*chunk_tasks)
            
            remaining = task.total_size - task.metrics.bytes_downloaded
            
            # Emit progress
            self._emit_event(
                "download_progress",
                {
                    "download_id": task.id,
                    "bytes_downloaded": task.metrics.bytes_downloaded,
                    "total_size": task.total_size,
                    "speed": task.metrics.current_speed,
                    "eta": task.metrics.eta_seconds,
                },
            )
    
    async def _download_and_write_chunk(
        self, task: DownloadTask, writer: AsyncFileWriter, offset: int, size: int
    ) -> None:
        """Download and write a single chunk."""
        try:
            end = offset + size - 1
            data, rtt_ms = await self._http_client.download_chunk(
                task.url, offset, end
            )
            
            # Write chunk (uses single file descriptor)
            await writer.write_chunk(offset, data)
            
            # Mark chunk as completed
            writer._completed_chunks[offset] = len(data)
            
            # Update metrics
            task.metrics.update(
                task.metrics.bytes_downloaded + len(data), rtt_ms
            )
        
        except Exception as e:
            task.metrics.increment_errors()
            if self._http_client.is_network_error(e):
                task.metrics.increment_retries()
            raise
    
    async def _download_full(
        self, task: DownloadTask, writer: AsyncFileWriter
    ) -> None:
        """Download entire file (no range support)."""
        data, rtt_ms = await self._http_client.download_full(task.url)
        
        # Write to file
        await writer.write_chunk(0, data)
        
        # Update metrics
        task.metrics.update(len(data), rtt_ms)
        
        self._emit_event(
            "download_progress",
            {
                "download_id": task.id,
                "bytes_downloaded": len(data),
                "total_size": task.total_size,
                "speed": task.metrics.current_speed,
                "eta": 0,
            },
        )
    
    async def _apply_decision(self, task: DownloadTask, decision: Decision) -> None:
        """Apply an adaptive decision to a task."""
        from flux.core.decisions import DecisionType
        
        if decision.decision_type == DecisionType.INCREASE_CHUNK_SIZE:
            new_size = min(task.chunk_size * 2, DecisionEngine.MAX_CHUNK_SIZE)
            task.chunk_size = new_size
        
        elif decision.decision_type == DecisionType.DECREASE_CHUNK_SIZE:
            new_size = max(task.chunk_size // 2, DecisionEngine.MIN_CHUNK_SIZE)
            task.chunk_size = new_size
        
        elif decision.decision_type == DecisionType.INCREASE_CONNECTIONS:
            new_conns = min(task.num_connections * 2, DecisionEngine.MAX_CONNECTIONS)
            task.num_connections = new_conns
        
        elif decision.decision_type == DecisionType.DECREASE_CONNECTIONS:
            new_conns = max(task.num_connections // 2, DecisionEngine.MIN_CONNECTIONS)
            task.num_connections = new_conns
        
        # Emit decision event
        self._emit_event(
            "adaptive_decision",
            {
                "download_id": task.id,
                "decision": decision.to_dict(),
            },
        )
    
    def get_download(self, download_id: str) -> Optional[DownloadTask]:
        """Get download task by ID."""
        return self.downloads.get(download_id)
    
    def get_downloads_by_status(self, status: DownloadStatus) -> List[DownloadTask]:
        """Get all downloads with a specific status."""
        return [d for d in self.downloads.values() if d.status == status]
