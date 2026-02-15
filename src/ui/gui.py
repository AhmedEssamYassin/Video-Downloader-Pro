"""
Main GUI with modern flat design using ttkbootstrap
Provides the primary user interface for the video downloader
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import os
from pathlib import Path
import subprocess
import threading

from .theme import Theme
from .custom_widgets import ModernButton, ModernEntry, AnimatedProgressBar, InfoCard
from ..core import DownloadController 
from ..data_models import DownloadConfig, PlaylistInfo
from .history_view import HistoryView
from .custom_messagebox import CustomMessageBox
from ..utils import AssetLoader, getTranslation, SettingsManager
from ..services.update_service import UpdateService


class VideoDownloaderGUI:
    """Enhanced main GUI with modern flat design"""
    
    def __init__(self, root):
        self.root = root
        
        # Load configuration and translations
        self.config = AssetLoader.loadConfig()
        self.currentLanguage = SettingsManager.getLanguage()
        self.translations = AssetLoader.loadTranslations(self.currentLanguage)
        
        # Set application icon
        try:
            iconPath = AssetLoader.getImagePath("icon.ico")
            if iconPath.exists():
                self.root.iconbitmap(iconPath)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Set window title from translations
        appTitle = getTranslation("app_title", self.currentLanguage)
        self.root.title(appTitle)
        
        # Center window on screen
        windowWidth = 850
        windowHeight = 720
        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()
        centerX = int(screenWidth/2 - windowWidth/2)
        centerY = int(screenHeight/2 - windowHeight/2)
        self.root.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        self.root.minsize(750, 650)
        
        # Initialize controller
        self.controller = DownloadController()
        
        # Variables - using settings manager
        defaultPath = SettingsManager.getDefaultDownloadPath()
        if not defaultPath:
            defaultPath = str(Path.home() / "Downloads")
        
        self.outputPathVar = tk.StringVar(value=defaultPath)
        self.qualityVar = tk.StringVar(value=SettingsManager.getDefaultQuality())
        self.formatVar = tk.StringVar(value=SettingsManager.getDefaultFormat())
        
        # Apply saved theme
        savedTheme = SettingsManager.getTheme()
        Theme.setTheme(savedTheme)
        
        # Configure root background
        self.root.configure(bg=Theme.BG_COLOR)
        
        # Toast notification container
        self.toastFrame = None
        
        # Create widgets
        self._createWidgets()

        self.VERSION = self.config.get("version", "2.0.0")
        
        # Check for updates in background
        self.root.after(2000, self._startUpdateCheck)

    def _startUpdateCheck(self):
        """Runs update check in background thread"""
        threading.Thread(target=self._performUpdateCheck, daemon=True).start()

    def _performUpdateCheck(self):
        isAvailable, latestVer, url = UpdateService.checkForUpdates(self.VERSION)
        if isAvailable:
            # Schedule UI update on main thread
            self.root.after(0, lambda: self._showUpdateNotification(latestVer, url))

    def _showUpdateNotification(self, latestVer, url):
        """Show the update button"""
        if hasattr(self, 'actionsFrame'):
            self.updateBtn = ttk.Button(
            self.actionsFrame,
            text=f"🚀 Update to v{latestVer}",
            command=lambda: self._startAutoUpdate(url),
            bootstyle=SUCCESS,  # Green button
            width=18,  # Characters (similar to history button's width=12)
            cursor="hand2"
        )
        self.updateBtn.pack(side=RIGHT, padx=(0, 10), before=self.settingsBtn)

    def _startAutoUpdate(self, url):
        """Handles the UI during update"""
        # Disable button to prevent double clicks
        self.updateBtn.configure(state="disabled")
        
        self.statusLabel.configure(text="Downloading Update...")
        self.progressBar.configure(mode='indeterminate')
        self.progressBar.set(0)
        
        # Start download in a thread
        UpdateService.downloadAndInstall(
            downloadUrl=url,
            progressCallback=self._updateProgress,
            completedCallback=lambda: self.root.after(0, lambda: self.statusLabel.configure(text="Restarting...")),
            errorCallback=self._onUpdateError
        )

    def _onUpdateError(self, errorMsg):
        """Safely handle update failures from the background thread"""
        self.root.after(0, lambda: self._resetUpdateUI(errorMsg))

    def _resetUpdateUI(self, errorMsg):
        """Reset the UI if an update fails so the user can try again"""
        if hasattr(self, 'updateBtn') and self.updateBtn.winfo_exists():
            self.updateBtn.configure(state="normal")
        
        self.progressBar.set(0)
        self.percentLabel.configure(text="")
        
        self._showError(f"Update Failed: {errorMsg}")        

    def _updateProgress(self, percent):
        """Updates the progress bar from the background thread"""
        # Use .after to safely update UI from background thread
        self.root.after(0, lambda: self.progressBar.set(percent))
        self.root.after(0, lambda: self.percentLabel.configure(text=f"{int(percent*100)}%"))
        
        if percent >= 1.0:
            self.root.after(0, lambda: self.statusLabel.configure(text="Restarting..."))

    def _t(self, key):
        """Shorthand for getting translations"""
        return getTranslation(key, self.currentLanguage)
    
    def _showToast(self, message, duration=3000, isSuccess=True):
        """Show a toast notification"""
        # Remove existing toast if any
        if self.toastFrame:
            self.toastFrame.destroy()
        
        # Create toast frame
        bgColor = Theme.SUCCESS_COLOR if isSuccess else Theme.ACCENT_COLOR
        self.toastFrame = tk.Frame(
            self.root,
            bg=bgColor,
            relief=FLAT
        )
        
        # Toast content
        toastContent = tk.Frame(self.toastFrame, bg=bgColor)
        toastContent.pack(padx=20, pady=12)
        
        icon = "✅" if isSuccess else "❌"
        iconLabel = tk.Label(
            toastContent,
            text=icon,
            font=("Segoe UI", 16),
            fg="white",
            bg=bgColor
        )
        iconLabel.pack(side=LEFT, padx=(0, 10))
        
        messageLabel = tk.Label(
            toastContent,
            text=message,
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg=bgColor
        )
        messageLabel.pack(side=LEFT)
        
        # Position toast at bottom center
        self.toastFrame.place(relx=0.5, rely=0.89, anchor=CENTER)
        
        # Fade in
        self.toastFrame.lift()
        self._animateToastIn(self.toastFrame, duration)
    
    def _animateToastIn(self, toast, duration):
        """Animate toast in and schedule fade out"""
        self.root.after(duration, lambda: self._animateToastOut(toast))
    
    def _animateToastOut(self, toast):
        """Animate toast out"""
        if toast and toast.winfo_exists():
            toast.place_forget()
            toast.destroy()
            self.toastFrame = None
        
    def _createWidgets(self):
        """Create and layout all GUI widgets"""
        # Main container with padding
        mainContainer = tk.Frame(self.root, bg=Theme.BG_COLOR)
        mainContainer.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        self._createHeader(mainContainer)
        self._createMainCard(mainContainer)
        
    def _createHeader(self, parent):
        """Create modern header section"""
        headerFrame = tk.Frame(parent, bg=Theme.BG_COLOR)
        headerFrame.pack(fill=X, pady=(0, 20))
        
        # Left side - Title
        titleContainer = tk.Frame(headerFrame, bg=Theme.BG_COLOR)
        titleContainer.pack(side=LEFT)
        
        # App icon/logo
        logoLabel = tk.Label(
            titleContainer,
            text="▶",
            font=("Segoe UI", 48),
            fg=Theme.SECONDARY_COLOR,
            bg=Theme.BG_COLOR
        )
        logoLabel.pack(side=LEFT, padx=(0, 14))
        
        # Title stack
        titleStack = tk.Frame(titleContainer, bg=Theme.BG_COLOR)
        titleStack.pack(side=LEFT)
        
        titleLabel = tk.Label(
            titleStack, 
            text=self._t("app_title"),
            font=Theme.TITLE_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.BG_COLOR
        )
        titleLabel.pack(anchor=W)
        
        subtitleLabel = tk.Label(
            titleStack,
            text=self._t("app_subtitle"),
            font=Theme.TINY_FONT,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_COLOR
        )
        subtitleLabel.pack(anchor=W)
        
        # Right side - Action buttons
        self.actionsFrame = tk.Frame(headerFrame, bg=Theme.BG_COLOR)
        self.actionsFrame.pack(side=RIGHT)
        
        # Pro badge
        proBadge = tk.Frame(
            self.actionsFrame,
            bg=Theme.GRADIENT_START,
            relief=FLAT
        )
        proBadge.pack(side=LEFT, padx=(0, 12))
        
        proLabel = tk.Label(
            proBadge, 
            text="✨ PRO", 
            font=Theme.PRO_LABEL_FONT,
            fg="white",
            bg=Theme.GRADIENT_START
        )
        proLabel.pack(padx=12, pady=6)

        # Settings button
        self.settingsBtn = ttk.Button(
            self.actionsFrame, 
            text="⚙️", 
            command=self._showSettings,
            bootstyle=SECONDARY,
            width=3,
            cursor="hand2"
        )
        self.settingsBtn.pack(side=RIGHT, padx=(0, 8))

        # History button
        historyBtn = ttk.Button(
            self.actionsFrame, 
            text=f"{self._t('buttons.history')}", 
            command=self._showHistory,
            bootstyle=SECONDARY,
            width=12,
            cursor="hand2"
        )
        historyBtn.pack(side=RIGHT, padx=(0, 12))
        
    def _createMainCard(self, parent):
        """Create main content card"""
        # Card frame
        mainCard = tk.Frame(
            parent, 
            bg=Theme.CARD_COLOR, 
            relief=FLAT,
            borderwidth=1,
            highlightbackground=Theme.INPUT_BORDER,
            highlightthickness=1
        )
        mainCard.pack(fill=BOTH, expand=True)
        
        self._createUrlSection(mainCard)
        self._createInfoCard(mainCard)
        self._createSettingsSection(mainCard)
        self._createProgressSection(mainCard)
        self._createDownloadButton(mainCard)
        
    def _createUrlSection(self, parent):
        """Create URL input section"""
        urlSection = tk.Frame(parent, bg=Theme.CARD_COLOR)
        urlSection.pack(fill=X, padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING, 0))
        
        # Label with icon
        labelFrame = tk.Frame(urlSection, bg=Theme.CARD_COLOR)
        labelFrame.pack(anchor=W, pady=(0, 10))
        
        urlLabel = tk.Label(
            labelFrame, 
            text=f"🔗 {self._t('labels.video_url')}", 
            font=Theme.SECTION_LABEL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.CARD_COLOR
        )
        urlLabel.pack(side=LEFT)
        
        # Helper text
        platforms = ", ".join(self.config['supported_platforms'][:3])
        helperText = tk.Label(
            labelFrame,
            text=f"• {platforms} & more",
            font=Theme.TINY_FONT,
            fg=Theme.MUTED_COLOR,
            bg=Theme.CARD_COLOR
        )
        helperText.pack(side=LEFT, padx=(8, 0))
        
        urlInputFrame = tk.Frame(urlSection, bg=Theme.CARD_COLOR)
        urlInputFrame.pack(fill=X)
        
        self.urlEntry = ModernEntry(
            urlInputFrame, 
            "https://youtube.com/watch?v=...", 
            "🔗"
        )
        self.urlEntry.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12))
        
        self.fetchBtn = ModernButton(
            urlInputFrame, 
            self._t("buttons.fetch_info"),
            self._onFetchClicked,
            bgColor=Theme.SECONDARY_COLOR,
            width=110, 
            height=56,
            font=("Segoe UI", 14, "bold")
        )
        self.fetchBtn.pack(side=RIGHT, fill=Y)
        
    def _createInfoCard(self, parent):
        """Create video info display card"""
        self.infoCard = tk.Frame(
            parent,
            bg=Theme.INFO_CARD_BG,
            relief=FLAT,
            borderwidth=1,
            highlightbackground=Theme.INPUT_BORDER,
            highlightthickness=1
        )
        self.infoCard.pack(fill=X, padx=Theme.CARD_PADDING, pady=(Theme.ELEMENT_SPACING, 0))
        
        infoContent = tk.Frame(self.infoCard, bg=Theme.INFO_CARD_BG)
        infoContent.pack(expand=True, pady=16, padx=20, fill=BOTH)
        
        # Status icon and title
        titleFrame = tk.Frame(infoContent, bg=Theme.INFO_CARD_BG)
        titleFrame.pack(fill=X, anchor=W)
        
        self.statusIcon = tk.Label(
            titleFrame,
            text="⏳",
            font=("Segoe UI", 16),
            bg=Theme.INFO_CARD_BG,
            fg=Theme.TEXT_COLOR
        )
        self.statusIcon.pack(side=LEFT, padx=(0, 12), anchor=N)
        
        titleStack = tk.Frame(titleFrame, bg=Theme.INFO_CARD_BG)
        titleStack.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.videoTitleEntry = ttk.Entry(
            titleStack,
            font=Theme.NORMAL_FONT,
            bootstyle=INFO
        )
        self.videoTitleEntry.pack(anchor=W, fill=X)
        self.videoTitleEntry.insert(0, self._t("messages.paste_url"))
        self.videoTitleEntry.configure(state=DISABLED)

        self.videoDurationLabel = tk.Label(
            titleStack,
            text=self._t("messages.paste_url"),
            font=Theme.SMALL_FONT,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.INFO_CARD_BG,
            anchor=W
        )
        self.videoDurationLabel.pack(anchor=W, pady=(4, 0))
        
    def _createSettingsSection(self, parent):
        """Create settings section"""
        settingsFrame = tk.Frame(parent, bg=Theme.CARD_COLOR)
        settingsFrame.pack(fill=X, padx=Theme.CARD_PADDING, pady=(Theme.ELEMENT_SPACING, 0))
        
        # Create grid layout for settings
        settingsFrame.grid_columnconfigure(0, weight=1)
        settingsFrame.grid_columnconfigure(1, weight=1)
        
        # Left column - Format
        formatSection = tk.Frame(settingsFrame, bg=Theme.CARD_COLOR)
        formatSection.grid(row=0, column=0, sticky=EW, padx=(0, 8))
        self._createFormatSelection(formatSection)
        
        # Right column - Quality
        qualitySection = tk.Frame(settingsFrame, bg=Theme.CARD_COLOR)
        qualitySection.grid(row=0, column=1, sticky=EW, padx=(8, 0))
        self._createQualitySelection(qualitySection)
        
        # Path selection (full width)
        pathSection = tk.Frame(settingsFrame, bg=Theme.CARD_COLOR)
        pathSection.grid(row=1, column=0, columnspan=2, sticky=EW, pady=(Theme.ELEMENT_SPACING, 0))
        self._createPathSelection(pathSection)
        
    def _createFormatSelection(self, parent):
        """Create format selection"""
        formatLabel = tk.Label(
            parent, 
            text=f"🎬 {self._t('labels.format')}", 
            font=Theme.SECTION_LABEL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.CARD_COLOR
        )
        formatLabel.pack(anchor=W, pady=(0, 10))
        
        # Radio button frame
        formatBtnFrame = tk.Frame(
            parent, 
            bg=Theme.INPUT_BG
        )
        formatBtnFrame.pack(fill=X, pady=3)
        
        self.mp4Btn = ttk.Radiobutton(
            formatBtnFrame, 
            text=self._t("formats.video_mp4"),
            variable=self.formatVar, 
            value="MP4",
            command=self._onFormatChange,
            bootstyle=INFO,
            cursor="hand2"
        )
        self.mp4Btn.pack(side=LEFT, padx=18, pady=12)
        
        self.mp3Btn = ttk.Radiobutton(
            formatBtnFrame, 
            text=self._t("formats.audio_mp3"),
            variable=self.formatVar, 
            value="MP3",
            command=self._onFormatChange,
            bootstyle=INFO,
            cursor="hand2"
        )
        self.mp3Btn.pack(side=LEFT, padx=18, pady=12)
        
    def _createQualitySelection(self, parent):
        """Create quality dropdown"""
        qualityLabel = tk.Label(
            parent, 
            text=f"⚙️ {self._t('labels.video_quality')}", 
            font=Theme.SECTION_LABEL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.CARD_COLOR
        )
        qualityLabel.pack(anchor=W, pady=(0, 10))
        
        # Get quality options from config
        qualityOptions = self.config.get('quality_options', ['best', '1080p', '720p', '480p', '360p'])
        
        from .custom_widgets import CustomDropdown
        
        self.qualityCombo = CustomDropdown(
            parent,
            variable=self.qualityVar,
            values=qualityOptions,
            font=Theme.SMALL_FONT,
            cursor="hand2"
        )
        self.qualityCombo.pack(fill=X)
        
    def _createPathSelection(self, parent):
        """Create output path section"""
        pathLabel = tk.Label(
            parent, 
            text=f"📁 {self._t('labels.save_location')}", 
            font=Theme.SECTION_LABEL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.CARD_COLOR
        )
        pathLabel.pack(anchor=W, pady=(0, 10))
        
        pathInputFrame = tk.Frame(
            parent, 
            bg=Theme.INPUT_BG
        )
        pathInputFrame.pack(fill=X)
        
        pathEntry = ttk.Entry(
            pathInputFrame, 
            textvariable=self.outputPathVar,
            font=Theme.SMALL_FONT,
            bootstyle=INFO
        )
        pathEntry.pack(side=LEFT, fill=BOTH, expand=True, padx=12, pady=8)
        
        # Open folder button
        openDirBtn = ttk.Button(
            pathInputFrame,
            text="📂",
            command=self._openDownloadPath,
            bootstyle=PRIMARY,
            width=3,
            cursor="hand2"
        )
        openDirBtn.pack(side=RIGHT, padx=(0, 8), pady=8)

        browseBtn = ttk.Button(
            pathInputFrame,
            text=self._t("buttons.browse"),
            command=self._browsePath,
            bootstyle=PRIMARY,
            width=10,
            cursor="hand2"
        )
        browseBtn.pack(side=RIGHT, padx=(0, 4), pady=8)
        
    def _openDownloadPath(self):
        """Open the download path in file explorer"""
        path = self.outputPathVar.get()
        
        if not os.path.exists(path):
            CustomMessageBox.showError(
                self.root, 
                self._t("errors.path_not_exist"),
                self._t("messages.invalid_path")
            )
            return
        
        try:
            path = os.path.normpath(path)
            
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':
                import subprocess
                import sys
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', path])
                else:  # Linux
                    subprocess.run(['xdg-open', path])
        except Exception as e:
            CustomMessageBox.showError(
                self.root, 
                "Error",
                f"{self._t('errors.folder_open_failed')}: {str(e)}"
            )

    def _createProgressSection(self, parent):
        """Create progress section"""
        progressFrame = tk.Frame(parent, bg=Theme.CARD_COLOR)
        progressFrame.pack(fill=X, padx=Theme.CARD_PADDING, pady=(Theme.ELEMENT_SPACING, 0))
        
        # Status container
        statusContainer = tk.Frame(progressFrame, bg=Theme.CARD_COLOR)
        statusContainer.pack(fill=X, pady=(0, 10))
        
        self.statusLabel = tk.Label(
            statusContainer, 
            text=self._t("status.ready"),
            font=Theme.SMALL_FONT,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.CARD_COLOR,
            anchor=W
        )
        self.statusLabel.pack(side=LEFT)
        
        self.percentLabel = tk.Label(
            statusContainer,
            text="",
            font=Theme.SMALL_FONT,
            fg=Theme.SECONDARY_COLOR,
            bg=Theme.CARD_COLOR,
            anchor=E
        )
        self.percentLabel.pack(side=RIGHT)
        
        # Progress bar
        self.progressBar = AnimatedProgressBar(progressFrame)
        self.progressBar.pack(fill=X)
        self.progressBar.set(0)
        
    def _createDownloadButton(self, parent):
        """Create download button"""
        downloadBtnFrame = tk.Frame(parent, bg=Theme.CARD_COLOR)
        downloadBtnFrame.pack(pady=(Theme.ELEMENT_SPACING, Theme.CARD_PADDING))
        
        self.downloadBtn = ModernButton(
            downloadBtnFrame, 
            f"⬇️  {self._t('buttons.download_now')}",
            self._onDownloadClicked,
            bgColor=Theme.ACCENT_COLOR,
            width=300, 
            height=54
        )
        self.downloadBtn.pack()

    def reDownload(self, url, outputPath):
        """Handles the entire re-download process"""
        self.urlEntry.delete(0, tk.END)
        self.urlEntry.insert(0, url)
        self.statusIcon.configure(text="🔄")
        self.statusLabel.configure(text=self._t("status.fetching"))
        
        self.progressBar.configure(mode='indeterminate')
        self.progressBar.start()
        self.downloadBtn.setEnabled(False)

        def onFetchSuccess(videoInfo):
            self.progressBar.stop()
            self.progressBar.configure(mode='determinate')
            self.progressBar.set(0)
            self._displayVideoInfo(videoInfo)
            
            videoTitle = self.videoTitleEntry.get().strip()
            config = DownloadConfig(url, outputPath, "best", "MP4")
            self.controller.startDownload(
                config, 
                videoTitle,
                self.updateDownloadProgress, 
                self._downloadComplete, 
                self._showError, 
                self._onDownloadComplete
            )

        def onFetchError(errorMsg):
            self.progressBar.stop()
            self.progressBar.configure(mode='determinate')
            self._showError(f"{self._t('errors.fetch_failed')}: {errorMsg}")
            self._onDownloadComplete()
        
        self.controller.fetchVideoInfo(url, onFetchSuccess, onFetchError, lambda: None)

    def _showHistory(self):
        """Show the download history window"""
        HistoryView(self.root, self)
    
    def _showSettings(self):
        """Show the settings dialog"""
        from .settings_view import SettingsDialog
        SettingsDialog(self.root, self)
        
    def _onFormatChange(self):
        """Handle format type change"""
        if self.formatVar.get() == "MP3":
            self.qualityCombo.configure(state='disabled')
        else:
            self.qualityCombo.configure(state='readonly')
    
    def _browsePath(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(initialdir=self.outputPathVar.get())
        if directory:
            self.outputPathVar.set(directory)
            
            # Save as last used path if remember_last_path is enabled
            if SettingsManager.shouldRememberLastPath():
                SettingsManager.setDefaultDownloadPath(directory)
    
    def _onFetchClicked(self):
        """Handle fetch button click"""
        url = self.urlEntry.get().strip()
        if not url:
            CustomMessageBox.showWarning(
                self.root, 
                "Input Required",
                self._t("messages.enter_url")
            )
            return
        
        from ..core import DownloadManager
        
        if not DownloadManager.isUrlSupported(url):
            from ..downloaders import DownloaderFactory
            supported = ", ".join(self.config['supported_platforms'])
            CustomMessageBox.showError(
                self.root,
                self._t("errors.unsupported_platform"),
                f"{self._t('messages.unsupported_url')}\n\n{supported}"
            )
            return
        
        provider = DownloadManager.getProviderForUrl(url)
        self.statusIcon.configure(text="🔍")
        self.statusLabel.configure(text=f"{self._t('status.fetching')} {provider}...")
        self.percentLabel.configure(text="")
        self.progressBar.configure(mode='indeterminate')
        self.progressBar.start()
        self.fetchBtn.setEnabled(False)
        
        def onSuccess(videoInfo):
            self.root.after(0, lambda: self._displayVideoInfo(videoInfo, provider))
        
        def onError(errorMsg):
            self.root.after(0, lambda: self._showError(errorMsg))
        
        def onComplete():
            self.root.after(0, lambda: [
                self.progressBar.stop(), 
                self.progressBar.configure(mode='determinate'),
                self.progressBar.set(0),
                self.fetchBtn.setEnabled(True)
            ])
        
        self.controller.fetchVideoInfo(url, onSuccess, onError, onComplete)
    
    def _displayVideoInfo(self, videoInfo, provider=""):
        """Display fetched video information"""
        self.videoTitleEntry.configure(state=NORMAL)
        self.statusIcon.configure(text="✅")
        
        if isinstance(videoInfo, PlaylistInfo):
            titleText = f"{videoInfo.title}"
            self.videoTitleEntry.delete(0, tk.END)  
            self.videoTitleEntry.insert(0, titleText)  
            self.videoDurationLabel.configure(
                text=f"{len(videoInfo.videos)} videos in playlist"
            )
        else:
            titleText = videoInfo.title
            self.videoTitleEntry.delete(0, tk.END)  
            self.videoTitleEntry.insert(0, titleText)  
            self.videoDurationLabel.configure(
                text=f"Duration: {videoInfo.duration} • {provider}"
            )
            
            if videoInfo.formats:
                self.qualityCombo.configure(values=['best'] + videoInfo.formats)
        
        self.statusLabel.configure(text="Video info loaded successfully")
        self.progressBar.configure(mode='determinate')
        self.progressBar.set(0)
    
    def _onDownloadClicked(self):
        """Handle download button click"""
        if self.controller.isDownloadInProgress():
            CustomMessageBox.showInfo(
                self.root,
                "Download in Progress",
                self._t("messages.download_in_progress")
            )
            return
        
        url = self.urlEntry.get().strip()
        if not url:
            CustomMessageBox.showWarning(
                self.root,
                "Input Required",
                self._t("messages.enter_url")
            )
            return
        
        outputPath = self.outputPathVar.get()
        if not os.path.exists(outputPath):
            CustomMessageBox.showError(
                self.root,
                "Invalid Path",
                self._t("messages.invalid_path")
            )
            return
        
        videoTitle = self.videoTitleEntry.get().strip()
        config = DownloadConfig(
            url=url,
            outputPath=outputPath,
            quality=self.qualityVar.get(),
            formatType=self.formatVar.get()
        )
        
        self.downloadBtn.setEnabled(False)
        self.progressBar.configure(mode='determinate')
        self.progressBar.set(0)
        self.statusIcon.configure(text="⬇️")
        self.statusLabel.configure(text=self._t("status.downloading"))
        self.percentLabel.configure(text="0%")
        
        self.controller.startDownload(
            config, 
            videoTitle,
            self.updateDownloadProgress, 
            self._downloadComplete, 
            self._showError, 
            self._onDownloadComplete
        )
    
    def updateDownloadProgress(self, d):
        """Update download progress with smooth animations"""
        if d['status'] == 'downloading':
            totalBytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if totalBytes and d.get('downloaded_bytes'):
                percent = (d['downloaded_bytes'] / totalBytes)
                self.progressBar.animateTo(percent)
                self.statusLabel.configure(text=self._t("status.downloading"))
                self.percentLabel.configure(text=f"{percent:.0%}")
                self.statusIcon.configure(text="⬇️")
        elif d['status'] == 'finished':
            self.progressBar.animateTo(1)
            self.statusLabel.configure(text=self._t("status.processing"))
            self.percentLabel.configure(text="100%")
            self.statusIcon.configure(text="🔄")

    def _onDownloadComplete(self):
        """Callback for when any download operation finishes"""
        self.root.after(0, lambda: self.downloadBtn.setEnabled(True))

    def _downloadComplete(self):
        """Handle successful download completion"""
        self.statusIcon.configure(text="✅")
        self.statusLabel.configure(text=self._t("status.completed"))
        self.percentLabel.configure(text="")
        self.progressBar.set(1.0)
        
        # Show toast notification
        message = f"{self._t('messages.download_success')} to {self.outputPathVar.get()}"
        self._showToast(message, duration=3000, isSuccess=True)
    
    def _showError(self, errorMsg):
        """Display error message"""
        self.statusIcon.configure(text="❌")
        self.statusLabel.configure(text=self._t("status.failed"))
        self.percentLabel.configure(text="")
        self.progressBar.set(0)
        self.videoTitleEntry.configure(state=NORMAL)
        self.videoTitleEntry.delete(0, tk.END)
        self.videoTitleEntry.insert(0, self._t("messages.paste_url"))
        self.videoTitleEntry.configure(state=DISABLED)
        # Show toast for errors
        self._showToast(f"Error: {errorMsg}", duration=3000, isSuccess=False)
