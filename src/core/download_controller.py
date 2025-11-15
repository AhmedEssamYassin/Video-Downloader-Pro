"""
Controller for handling business logic and coordinating between UI and services
"""

import threading
from .download_manager import DownloadManager
from ..data_models import DownloadConfig, PlaylistInfo
from ..services import HistoryService
from ..services import DesktopNotifier

class DownloadController:
    """Coordinates download operations and manages state"""
    
    def __init__(self):
        self.isDownloading = False
        self.videoInfo = None
        self.historyService = HistoryService()
        self.notifier = DesktopNotifier()
    
    def fetchVideoInfo(self, url, onSuccess, onError, onComplete):
        """
        Fetch video information in a background thread
        
        Args:
            url: YouTube video URL
            onSuccess: Callback for successful fetch (receives VideoInfo)
            onError: Callback for errors (receives error message)
            onComplete: Callback when operation completes
        """
        def fetchThread():
            try:
                self.videoInfo = DownloadManager.getVideoInfo(url)
                onSuccess(self.videoInfo)
            except Exception as e:
                onError(str(e))
            finally:
                onComplete()
        
        thread = threading.Thread(target=fetchThread, daemon=True)
        thread.start()
    
    def startDownload(self, config, title, progressCallback, onSuccess, onError, onComplete):
        """
        Start download in a background thread
        
        Args:
            config: DownloadConfig object
            title: The title of the video to be downloaded
            progressCallback: Callback for progress updates
            onSuccess: Callback for successful download
            onError: Callback for errors (receives error message)
            onComplete: Callback when operation completes
        """
        if self.isDownloading:
            onError("Download already in progress")
            return
        
        try:
            config.validate()
        except ValueError as e:
            onError(str(e))
            return
        
        self.isDownloading = True

        def downloadThread():
            try:
                if isinstance(self.videoInfo, PlaylistInfo):
                    for video in self.videoInfo.videos:
                        DownloadManager.downloadVideo(
                            video['url'],
                            config.outputPath,
                            config.quality,
                            config.formatType,
                            progressCallback
                        )
                        self.historyService.addEntry(video['title'], video['url'], config.outputPath, "Completed")
                else:
                    DownloadManager.downloadVideo(
                        config.url,
                        config.outputPath,
                        config.quality,
                        config.formatType,
                        progressCallback,
                        title
                    )
                    self.historyService.addEntry(self.videoInfo.title, config.url, config.outputPath, "Completed")
                
                self.notifier.sendNotification("Download Complete", f"Finished downloading: {self.videoInfo.title}")
                onSuccess()
            except Exception as e:
                self.notifier.sendNotification("Download Failed", f"Error downloading: {self.videoInfo.title}")
                onError(str(e))
            finally:
                self.isDownloading = False
                onComplete()

        thread = threading.Thread(target=downloadThread, daemon=True)
        thread.start()
    
    def getVideoInfo(self):
        """Get currently loaded video info"""
        return self.videoInfo
    
    def isDownloadInProgress(self):
        """Check if download is currently in progress"""
        return self.isDownloading
    
    def getHistory(self):
        """Get download history"""
        return self.historyService.getHistory()
    
    def removeHistoryEntry(self, index: int):
        """Remove a single entry from the history"""
        self.historyService.removeEntry(index)

    def clearHistory(self):
        """Clear the entire download history"""
        self.historyService.clearHistory()