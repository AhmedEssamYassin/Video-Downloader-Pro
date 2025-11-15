"""
Abstract base class for video downloaders
Implements the Strategy Pattern for different download providers
"""

from abc import ABC, abstractmethod
from ..data_models import VideoInfo


class BaseDownloader(ABC):
    """Abstract base class for video download providers"""
    
    @abstractmethod
    def canHandle(self, url: str) -> bool:
        """
        Check if this downloader can handle the given URL
        
        Args:
            url: Video URL to check
            
        Returns:
            True if this downloader supports the URL
        """
        pass
    
    def isPlaylist(self, url: str) -> bool:
        """
        Check if the URL is a playlist.
        
        Args:
            url: URL to check.
        Returns:
            True if the URL is a playlist, False otherwise.
        """
        return 'playlist' in url

    @abstractmethod
    def getVideoInfo(self, url: str) -> VideoInfo:
        """
        Fetch video information without downloading
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo object with video metadata
            
        Raises:
            Exception: If fetching info fails
        """
        pass
    
    @abstractmethod
    def downloadVideo(self, url: str, outputPath: str, quality: str, 
                      formatType: str, progressCallback, title: str = None):
        """
        Download video with specified parameters
        
        Args:
            url: Video URL
            outputPath: Directory to save the video
            quality: Video quality (e.g., 'best', '720p')
            formatType: Output format ('MP4' or 'MP3')
            progressCallback: Function to call with progress updates
            title: Optional custom title for the video
        
        Raises:
            Exception: If download fails
        """
        pass
    
    @abstractmethod
    def getProviderName(self) -> str:
        """
        Get the name of this provider
        
        Returns:
            Provider name (e.g., 'YouTube', 'Facebook')
        """
        pass
    
    def getDefaultFormats(self) -> list:
        """
        Get default quality formats for this provider
        
        Returns:
            List of quality options
        """
        return ['best', '1080p', '720p', '480p', '360p']