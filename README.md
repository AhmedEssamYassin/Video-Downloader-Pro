# Video Downloader Pro - Modular Structure compliant with SOLID principles and Design patterns 

## System Design (UML Diagram)
![UML Diagram](./docs/system%20design/UML_Diagram.svg)

## Project Structure

```
Video Downloader/
│
├── assets/
│   ├── data/
│   │   ├── default_config.json
│   │   └── translations/
│   │       ├── ar.json
│   │       └── en.json
│   ├── images/
│   │   ├── icon.ico
│   │   └── icon.png
│   └── README.md
|
├── src/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── download_controller.py          # Business logic controller
│   │   └── download_manager.py             # Download operations facade
│   │
│   ├── data_models/
│   │   ├── __init__.py
│   │   └── models.py                       # Data models (VideoInfo, DownloadConfig)
│   │
│   ├── downloaders/
│   │   ├── __init__.py
│   │   └── base_downloader.py              # Abstract base class
│   │   └── downloader_factory.py           # Factory for creating downloaders
│   │   └── facebook_downloader.py          # Facebook implementation
│   │   └── youtube_downloader.py           # YouTube implementation
│   │   └── instagram_downloader.py         # Instagram implementation
│   │   └── tiktok_downloader.py            # Tiktok implementation
│   │   └── twitter_downloader.py           # Twitter/X implementation
│   │
|   ├── services/
│   │   ├── __init__.py
│   │   └── history_service.py              # A service for history management (load, save, add, get ...)
│   │   └── notification_service.py         # A service for notifications (send desktop notifications)
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── theme.py                        # UI theme configuration
│   │   └── custom_widgets.py               # Custom UI components
│   │   └── history_view.py                 # Download history window
│   │   └── gui.py                          # Main GUI application
|
|   ├── utils/
│   │   ├── __init__.py
│   │   └── asset_loader.py                 # Asset loader utility for accessing application assets
│   │   └── settings_manager.py             # Settings manager for user preferences and configuration persistence
|
│── main.py                                 # Application entry point
│
│
├── requirements.txt                        # Project dependencies
├── README.md                               # Project documentation
└── VideoDownloaderPro.spec                 # PyInstaller config file
```

## Key Features

### Platform Support
- **YouTube** - Videos, playlists, quality selection
- **Facebook** - Public videos and posts
- **Instagram** - Reels, posts, stories
- **TikTok** - Videos and audio from photo posts
- **Twitter/X** - Video tweets

### Download Options
- **Video Formats** - MP4 with quality selection (best, 1080p, 720p, 480p, 360p)
- **Audio Extraction** - MP3 format with 192kbps quality
- **Custom Naming** - Edit video title before downloading
- **Flexible Output** - Choose download location with quick folder access

### User Experience
- **Modern Dark Theme** - Eye-friendly interface with smooth animations
- **Progress Tracking** - Real-time download progress with visual feedback
- **Download History** - View, search, and manage past downloads
- **Re-download** - Easy re-download from history
- **Desktop Notifications** - Get notified when downloads complete
- **URL Detection** - Automatic platform detection and validation

### Technical Highlights
- **Asynchronous Downloads** - Non-blocking UI during downloads
- **Modular Architecture** - SOLID principles and design patterns
- **Extensible** - Easy to add new platforms without breaking existing code
- **Error Handling** - Comprehensive error messages and recovery
---

## Architecture Overview

### Separation of Concerns + SOLID Principles

1. **Presentation Layer** (`ui/`)
   - `gui.py` - Main application window and user interactions
   - `history_view.py` - Download history management window
   - `custom_widgets.py` - Reusable UI components (ModernButton, ModernEntry, etc.)
   - `theme.py` - Centralized styling and color scheme
   - **No business logic** - Pure presentation code

2. **Business Logic Layer** (`core/`)
   - `download_controller.py` - Orchestrates downloads, manages state
   - Handles threading for non-blocking operations
   - Coordinates between UI and services
   - **Separation** - No UI code, no direct platform logic

3. **Service Layer** (`services/`)
   - `history_service.py` - Persistent download history (JSON storage)
   - `notification_service.py` - Desktop notifications via plyer
   - **Abstraction** - Platform-independent services

4. **Download Strategy Layer** (`downloaders/`) - **OCP Implementation** ⭐
   - `base_downloader.py` - Abstract contract defining downloader interface
   - Platform implementations - Each platform in isolated file
   - `downloader_factory.py` - Automatic platform detection and selection
   - **Key Benefit** - Add platforms without modifying existing code

5. **Data Layer** (`data_models/`)
   - `models.py` - Data structures with validation
     - `VideoInfo` - Video metadata
     - `PlaylistInfo` - Playlist information
     - `DownloadConfig` - Configuration with validation

### Data Flow Diagram
```
User Input (URL) 
    ↓
GUI (Presentation Layer)
    ↓
DownloadController (Business Logic)
    ↓
DownloadManager (Facade)
    ↓
DownloaderFactory (Factory Pattern)
    ↓
Platform Downloader (Strategy Pattern)
    ↓
yt-dlp (External Library)
    ↓
Downloaded File + History Entry
```

## 🎯 SOLID Principles Applied

### S - Single Responsibility Principle
Each module has one clear purpose:
- GUI only handles presentation
- Controller only manages business logic
- Each downloader only handles one platform

### O - Open/Closed Principle ⭐
**Open for extension, closed for modification:**
```python
# Adding a new platform (e.g., Instagram)
class InstagramDownloader(BaseDownloader):
    def canHandle(self, url): 
        return "instagram.com" in url
    # Implement required methods
    
# Register it - NO OTHER CODE CHANGES NEEDED!
DownloaderFactory.registerDownloader(InstagramDownloader())
```

### L - Liskov Substitution Principle
Any `BaseDownloader` implementation can be substituted for another without breaking the application

### I - Interface Segregation Principle
Clean, minimal abstract interface in `BaseDownloader` with only necessary methods

### D - Dependency Inversion Principle
High-level modules (GUI, Controller) depend on abstractions (DownloadManager interface), not concrete implementations

## Open/Closed Principle Deep Dive

### The Problem It Solves

**Without OCP:**
```python
# BAD: Every new platform requires modifying existing code
def downloadVideo(url, ...):
    if "youtube.com" in url:
        # YouTube logic
    elif "facebook.com" in url:
        # Facebook logic
    elif "instagram.com" in url:  # Modification!
        # Instagram logic
    # Growing if/else chain = high risk of bugs
```

**With OCP:**
```python
# GOOD: Just add a new class, zero modifications
class TikTokDownloader(BaseDownloader):
    def canHandle(self, url):
        return "tiktok.com" in url
    # Implement interface
    
# Register and done!
DownloaderFactory.registerDownloader(TikTokDownloader())
```

### Architecture Flow

```
User enters URL → DownloadManager → Factory selects downloader
                                         ↓
                    ┌────────────────────┴────────────────────┐
                    ↓                    ↓                     ↓
            YouTubeDownloader    FacebookDownloader    [other Downloaders]
                    
Each downloader inherits from BaseDownloader (abstract)
```

### Benefits

1. **Zero Risk**: Adding platforms can't break existing ones
2. **Parallel Development**: Different developers work on different platforms
3. **Easy Testing**: Test each platform independently
4. **No Code Duplication**: Shared interface via base class
5. **Plugin Architecture**: Platform implementations are like plugins

## Setup Instructions

### 1. Install `pipreqs` library (if not installed already)

### 2. Create requirements.txt (if not created already)
```bash
pipreqs freeze > requirements.txt
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python main.py
```

## 🔧 Module Dependencies

```
main.py (Application Entry Point)
└── src.ui.gui.py (Main Application Window)
    ├── src.ui.theme.py
    ├── src.ui.custom_widgets.py
    ├── src.ui.history_view.py
    │   ├── src.services.history_service.py
    │   └── (Imports custom_widgets, theme)
    ├── src.core.download_controller.py (Business Logic Orchestrator)
    │   ├── src.core.download_manager.py (Facade)
    │   │   └── src.downloaders.downloader_factory.py (Factory Pattern)
    │   │       ├── src.downloaders.base_downloader.py (Abstract Interface)
    │   │       │   └── src.data_models.models.py
    │   │       ├── src.downloaders.youtube_downloader.py (Strategy)
    │   │       ├── src.downloaders.facebook_downloader.py (Strategy)
    │   │       ├── src.downloaders.instagram_downloader.py (Strategy)
    │   │       ├── src.downloaders.tiktok_downloader.py (Strategy)
    │   │       └── src.downloaders.twitter_downloader.py (Strategy)
    │   ├── src.services.history_service.py
    │   ├── src.services.notification_service.py
    │   ├── src.utils.settings_manager.py
    │   │   └── src.utils.asset_loader.py
    │   └── src.data_models.models.py
    └── src.utils.asset_loader.py (For icons/images)
```

## 🎯 Benefits of This Architecture

### Scalability via Open/Closed Principle
- **Easy to add platforms**: Create one new file, no modifications needed
- **Independent modules**: Changes in one platform don't affect others
- **Testing friendly**: Each platform can be tested independently
- **Plugin-like architecture**: Platforms are self-contained implementations

### Maintainability
- **Clear responsibilities**: Each module has a single, well-defined purpose
- **Easy to debug**: Issues can be isolated to specific modules/platforms
- **Code reusability**: Widgets, components, and base classes are reused
- **No regression risk**: Adding features can't break existing platforms

### Extensibility
- **Platform support**: YouTube, Facebook, Instagram, TikTok, Twitter, etc.
- **Theme switching**: Simple to implement multiple themes
- **Custom widgets**: Easy to create and integrate new UI components
- **Format support**: Easy to add new output formats (WebM, AVI, etc.)

## Future Enhancement Ideas

### Potential Platform Additions (OCP Makes This Easy!)

2. **Feature Enhancements**
   - `config_manager.py`: User preferences and settings persistence
   - `subtitle_downloader.py`: Subtitle/caption support
   - `scheduler.py`: Scheduled downloads

3. **Architecture Improvements**
   - Dependency injection for better testing
   - Event system for module communication
   - Configuration file support (JSON/YAML)
   - Logging system implementation
   - Plugin loader for dynamic platform discovery

### Adding a New Platform (Template)

```python
# new_platform_downloader.py
from base_downloader import BaseDownloader
from models import VideoInfo
import yt_dlp
import re

class NewPlatformDownloader(BaseDownloader):
    """Downloader for NewPlatform videos"""
    
    def canHandle(self, url: str) -> bool:
        """Check if URL is from NewPlatform"""
        patterns = [
            r'newplatform\.com/',
            r'nplat\.tv/'
        ]
        return any(re.search(pattern, url) for pattern in patterns)
    
    def getVideoInfo(self, url: str) -> VideoInfo:
        """Fetch video information"""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return VideoInfo(
                title=info.get('title', 'NewPlatform Video'),
                duration=str(info.get('duration', 0)) + 's',
                formats=['best', '1080p', '720p', '480p']
            )
    
    def downloadVideo(self, url: str, outputPath: str, quality: str, 
                      formatType: str, progressCallback):
        """Download video"""
        # Platform-specific download logic
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{outputPath}/%(title)s.%(ext)s',
            'progress_hooks': [progressCallback]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    def getProviderName(self) -> str:
        """Get provider name"""
        return "NewPlatform"

# Register in downloader_factory.py:
# DownloaderFactory.registerDownloader(NewPlatformDownloader())
```

That's it! One file = one new platform support! 🎉

## Usage Example

```python
# Example 1: Using the controller independently
from controller import DownloadController
from models import DownloadConfig

controller = DownloadController()

# Fetch video info (works for YouTube, Facebook, etc.)
def onSuccess(info):
    print(f"Title: {info.title}")
    print(f"Duration: {info.duration}")

controller.fetch_video_info(
    url="https://youtube.com/watch?v=...",  # or facebook.com/...
    onSuccess=onSuccess,
    onError=lambda e: print(f"Error: {e}"),
    onComplete=lambda: print("Done")
)

# Example 2: Using the factory directly
from downloader_factory import DownloaderFactory

url = "https://facebook.com/video/123"
downloader = DownloaderFactory.getDownloader(url)
if downloader:
    print(f"Provider: {downloader.getProviderName()}")  # "Facebook"
    video_info = downloader.getVideoInfo(url)
    print(f"Title: {video_info.title}")

# Example 3: Check if URL is supported
from download_manager import DownloadManager

if DownloadManager.isUrlSupported("https://tiktok.com/..."):
    print("Supported!")
else:
    print("Not supported yet. Add TikTokDownloader!")
```

## 🔧 Troubleshooting

### Common Issues

**"Failed to fetch video info"**
- Check if the URL is publicly accessible
- Verify your internet connection
- Some platforms may block automated downloads

**"FFmpeg not found" error**
- Install FFmpeg: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH

**"Download failed" for Instagram/TikTok**
- These platforms frequently change their API
- Update yt-dlp: `pip install --upgrade yt-dlp`

**Slow download speeds**
- Check your internet connection
- Some platforms throttle download speeds
- Try different quality settings

**Desktop notifications not working**
- Install plyer: `pip install plyer`
- On Linux, ensure notification-daemon is installed

---

## 📊 Module Complexity Comparison

### Before OCP (Monolithic)
| Component | Lines | Complexity | Extensibility |
|-----------|-------|------------|---------------|
| download_manager.py | ~150 | High | ❌ Hard to extend |
| **Total** | **~150** | **High** | **Requires modification** |

### After OCP (Modular - Downloaders Only)
| Module | Lines | Complexity | Purpose |
|--------|-------|------------|---------|
| base_downloader.py | ~70 | Low | Abstract contract |
| youtube_downloader.py | ~120 | Medium | YouTube logic |
| facebook_downloader.py | ~105 | Medium | Facebook logic |
| instagram_downloader.py | ~100 | Medium | Instagram logic |
| tiktok_downloader.py | ~150 | Medium | TikTok logic |
| twitter_downloader.py | ~120 | Medium | Twitter/X logic |
| downloader_factory.py | ~70 | Low | Provider selection |
| download_manager.py | ~90 | Low | Facade |
| **Total** | **~825** | **Low per file** | **✅ Just add files** |

**Trade-off**: More code (~675 lines), but:
- ✅ **5 platforms** vs 1-2 in monolithic
- ✅ Each file is simple and focused (~100 lines each)
- ✅ Zero risk when adding platforms
- ✅ Parallel development possible
- ✅ Easy to test individually
- ✅ No if/else chains - clean architecture

### Architecture Benefits

**Code Distribution:**
- 📊 **~1,170 lines (49%)** - UI/Presentation layer
- 🎯 **~735 lines (31%)** - Download strategy (OCP)
- ⚙️ **~290 lines (12%)** - Core logic & services
- 📦 **~175 lines (8%)** - Data models & utilities

The ~1,400-1,600 line increase buys us:
- ✅ **5 platforms** with isolated implementations
- ✅ **Complete UI** with history management
- ✅ **Desktop notifications** and persistence
- ✅ **SOLID principles** throughout
- ✅ **Easy extensibility** - Add platforms in ~100 lines each
- ✅ **Better testability** - Each module independently testable
- ✅ **Team-friendly** - Multiple developers can work in parallel
- ✅ **Maintainability** - Average ~135 lines per file (17 files)

### Scalability Analysis

**Adding a new platform (e.g., Reddit):**
- Monolithic: Modify 3-4 existing files, risk breaking 5 platforms
- OCP: Create 1 new file (~100 lines), register in factory (1 line)

**Bug in TikTok downloader:**
- Monolithic: Risk affecting all platforms in same file
- OCP: Fix isolated to `tiktok_downloader.py` only

**Team of 5 developers:**
- Monolithic: Constant merge conflicts, blocking each other
- OCP: Each developer owns a platform, parallel work with zero conflicts

---
## Deployment

**Use the `build.py` file and it will build the executable file directly using `PyInstaller`**
```bash
py build.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Libraries

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video download engine
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [plyer](https://github.com/kivy/plyer) - Desktop notifications
- [Pillow](https://python-pillow.org/) - Image processing

### Disclaimer

This tool is for personal use only. Please respect copyright laws and platform terms of service. The developers are not responsible for misuse of this software.