"""
Adaptive HTTP client for downloading files.
"""

import asyncio
import ssl
import time
from typing import Optional, Tuple
from urllib.parse import urlparse

import aiohttp


class AdaptiveHTTPClient:
    """HTTP client with adaptive features."""
    
    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Create SSL context that doesn't verify certificates
        # (for testing and to avoid SSL errors with some hosts)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def __aenter__(self) -> "AdaptiveHTTPClient":
        """Async context manager entry."""
        # Create connector with connection pooling and keepalive
        connector = aiohttp.TCPConnector(
            ssl=self.ssl_context,
            limit=200,  # Connection pool limit (increased for performance)
            limit_per_host=20,  # Per-host limit (increased for performance)
            ttl_dns_cache=300,  # DNS cache TTL
            enable_cleanup_closed=True,  # Clean up closed connections
            force_close=False,  # Keep connections alive
        )
        
        self._session = aiohttp.ClientSession(
            timeout=self.timeout,
            connector=connector,
            # Add headers to help with connection persistence
            headers={
                "Connection": "keep-alive",
                "User-Agent": "Flux/1.0.0",
            },
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            # Wait for connector to close properly
            await asyncio.sleep(0.25)
            self._session = None
    
    async def get_file_info(self, url: str) -> Tuple[int, bool, str]:
        """
        Get file information from URL.
        
        Args:
            url: File URL
        
        Returns:
            Tuple of (file_size, supports_ranges, filename)
        
        Raises:
            aiohttp.ClientError: On HTTP errors
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async with.")
        
        start_time = time.time()
        
        # Use a shorter timeout for HEAD requests (5 seconds)
        head_timeout = aiohttp.ClientTimeout(total=5)
        
        try:
            async with self._session.head(url, allow_redirects=True, timeout=head_timeout) as response:
                response.raise_for_status()
                
                # Get file size
                content_length = response.headers.get("Content-Length")
                file_size = int(content_length) if content_length else 0
                
                # Check range support
                accept_ranges = response.headers.get("Accept-Ranges", "none")
                supports_ranges = accept_ranges.lower() != "none"
                
                # Extract filename from URL or Content-Disposition
                filename = self._extract_filename(url, response.headers)
                
                rtt_ms = (time.time() - start_time) * 1000
                
                return file_size, supports_ranges, filename
                
        except (aiohttp.ClientError, asyncio.TimeoutError):
            # If HEAD fails, try GET with Range header
            try:
                headers = {"Range": "bytes=0-0"}
                async with self._session.get(url, headers=headers, allow_redirects=True) as response:
                    response.raise_for_status()
                    
                    content_range = response.headers.get("Content-Range")
                    if content_range:
                        # Parse "bytes 0-0/12345"
                        parts = content_range.split("/")
                        file_size = int(parts[1]) if len(parts) > 1 else 0
                        supports_ranges = True
                    else:
                        content_length = response.headers.get("Content-Length")
                        file_size = int(content_length) if content_length else 0  
                        supports_ranges = False
                    
                    filename = self._extract_filename(url, response.headers)
                    return file_size, supports_ranges, filename
                    
            except Exception:
                raise
    
    async def download_chunk(
        self,
        url: str,
        start: int,
        end: int,
        retry_count: int = 0,
    ) -> Tuple[bytes, float]:
        """
        Download a chunk of the file.
        
        Args:
            url: File URL
            start: Start byte position
            end: End byte position (inclusive)
            retry_count: Current retry attempt
        
        Returns:
            Tuple of (chunk_data, rtt_ms)
        
        Raises:
            aiohttp.ClientError: On HTTP errors after retries
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async with.")
        
        headers = {"Range": f"bytes={start}-{end}"}
        
        try:
            start_time = time.time()
            
            async with self._session.get(url, headers=headers) as response:
                # Accept 206 (Partial Content) or 200 (full content)
                if response.status not in (200, 206):
                    response.raise_for_status()
                
                data = await response.read()
                rtt_ms = (time.time() - start_time) * 1000
                
                return data, rtt_ms
        
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if retry_count < self.max_retries:
                # Exponential backoff with jitter
                wait_time = (2 ** retry_count) + (time.time() % 1)
                await asyncio.sleep(wait_time)
                return await self.download_chunk(url, start, end, retry_count + 1)
            else:
                raise
    
    async def download_full(self, url: str) -> Tuple[bytes, float]:
        """
        Download entire file (for servers that don't support ranges).
        
        Args:
            url: File URL
        
        Returns:
            Tuple of (file_data, rtt_ms)
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async with.")
        
        start_time = time.time()
        
        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.read()
            rtt_ms = (time.time() - start_time) * 1000
            
            return data, rtt_ms
    
    def _extract_filename(self, url: str, headers: dict) -> str:
        """
        Extract filename from URL or headers.
        
        Args:
            url: File URL
            headers: Response headers
        
        Returns:
            Extracted filename
        """
        # Try Content-Disposition header
        content_disp = headers.get("Content-Disposition", "")
        if "filename=" in content_disp:
            parts = content_disp.split("filename=")
            if len(parts) > 1:
                filename = parts[1].strip('"').strip("'")
                if filename:
                    return filename
        
        # Fall back to URL path
        parsed = urlparse(url)
        path = parsed.path
        
        if path and "/" in path:
            filename = path.split("/")[-1]
            if filename:
                return filename
        
        # Last resort
        return "download"
    
    @staticmethod
    def is_network_error(exception: Exception) -> bool:
        """
        Classify if error is network-related vs server error.
        
        Args:
            exception: Exception to classify
        
        Returns:
            True if network error, False if server error
        """
        if isinstance(exception, asyncio.TimeoutError):
            return True
        
        if isinstance(exception, aiohttp.ClientError):
            # Connection errors are network issues
            if isinstance(
                exception,
                (
                    aiohttp.ClientConnectionError,
                    aiohttp.ClientConnectorError,
                    aiohttp.ServerDisconnectedError,
                ),
            ):
                return True
            
            # 5xx errors could be transient
            if hasattr(exception, "status") and 500 <= exception.status < 600:
                return True
        
        return False
