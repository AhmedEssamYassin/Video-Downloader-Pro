"""
Data models for the YouTube Downloader application
"""

class VideoInfo:
    """Data class to store video information"""
    
    def __init__(self, title="", duration="", thumbnail="", formats=None):
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.formats = formats or []
    
    def __repr__(self):
        return f"VideoInfo(title='{self.title}', duration='{self.duration}')"

class PlaylistInfo:
    """Data class to store playlist information"""

    def __init__(self, title="", videos=None):
        self.title = title
        self.videos = videos or []

    def __repr__(self):
        return f"PlaylistInfo(title='{self.title}', videos={len(self.videos)})"

class DownloadConfig:
    """Configuration for download operations"""
    
    def __init__(self, url, outputPath, quality, formatType):
        self.url = url
        self.outputPath = outputPath
        self.quality = quality
        self.formatType = formatType
    
    def validate(self):
        """Validate configuration parameters"""
        if not self.url:
            raise ValueError("URL is required")
        if not self.outputPath:
            raise ValueError("Output path is required")
        return True