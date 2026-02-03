"""
Main GUI with proper asset integration and internationalization
"""

import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import os
from pathlib import Path
import subprocess

from .theme import Theme
from .custom_widgets import ModernButton, ModernEntry, AnimatedProgressBar, InfoCard
from ..core import DownloadController 
from ..data_models import DownloadConfig, PlaylistInfo
from .history_view import HistoryView
from .custom_messagebox import CustomMessageBox
from ..utils import AssetLoader, getTranslation, SettingsManager
import threading
from ..services.update_service import UpdateService

class VideoDownloaderGUI:
    """Enhanced main GUI with asset integration and i18n support"""
    
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
        
        # Configure styles and apply saved theme
        savedTheme = SettingsManager.getTheme()
        ctk.set_appearance_mode(savedTheme)
        ctk.set_default_color_theme("blue")
        
        self.root.configure(fg_color=Theme.BG_COLOR)
        
        # Toast notification container
        self.toastFrame = None
        
        # Create widgets with fade-in effect
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
            self.updateBtn = ctk.CTkButton(
                self.actionsFrame,
                text=f"🚀 Update to v{latestVer}",
                fg_color="#2ecc71",
                text_color="white",
                command=lambda: self._startAutoUpdate(url)
            )
            self.updateBtn.pack(side="right", padx=(0, 10))

    def _startAutoUpdate(self, url):
        """Handles the UI during update"""
        # Disable button to prevent double clicks
        self.updateBtn.configure(state="disabled", text="Downloading...")
        
        self.statusLabel.configure(text="Downloading Update...")
        self.progressBar.configure(mode='determinate')
        self.progressBar.set(0)
        
        # Start download in a thread
        import threading
        threading.Thread(
            target=UpdateService.downloadAndInstall,
            args=(
                url, 
                self._updateProgress,  # Callback for progress bar
                None                   # Callback for completion 
            ),
            daemon=True
        ).start()

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
        self.toastFrame = ctk.CTkFrame(
            self.root,
            fg_color=Theme.SUCCESS_COLOR if isSuccess else Theme.ACCENT_COLOR,
            corner_radius=12,
            border_width=0
        )
        
        # Toast icon and message
        toastContent = ctk.CTkFrame(self.toastFrame, fg_color="transparent")
        toastContent.pack(padx=20, pady=12)
        
        icon = "✅" if isSuccess else "❌"
        iconLabel = ctk.CTkLabel(
            toastContent,
            text=icon,
            font=("Segoe UI", 16),
            text_color="white"
        )
        iconLabel.pack(side="left", padx=(0, 10))
        
        messageLabel = ctk.CTkLabel(
            toastContent,
            text=message,
            font=("Segoe UI", 12, "bold"),
            text_color="white"
        )
        messageLabel.pack(side="left")
        
        # Position toast at bottom center
        self.toastFrame.place(relx=0.5, rely=0.92, anchor="center")
        
        # Fade in
        self.toastFrame.lift()
        self._animateToastIn(self.toastFrame, duration)
    
    def _animateToastIn(self, toast, duration):
        """Animate toast in and schedule fade out"""
        toast.configure(fg_color=toast.cget("fg_color"))
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
        mainContainer = ctk.CTkFrame(self.root, fg_color="transparent")
        mainContainer.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._createHeader(mainContainer)
        self._createMainCard(mainContainer)
        
    def _createHeader(self, parent):
        """Create modern header section with gradient accent"""
        headerFrame = ctk.CTkFrame(parent, fg_color="transparent")
        headerFrame.pack(fill="x", pady=(0, 20))
        
        # Left side - Title with modern styling
        titleContainer = ctk.CTkFrame(headerFrame, fg_color="transparent")
        titleContainer.pack(side="left")
        
        # App icon/logo
        logoLabel = ctk.CTkLabel(
            titleContainer,
            text="▶",
            font=("Segoe UI", 36),
            text_color=Theme.SECONDARY_COLOR
        )
        logoLabel.pack(side="left", padx=(0, 14))
        
        # Title stack
        titleStack = ctk.CTkFrame(titleContainer, fg_color="transparent")
        titleStack.pack(side="left")
        
        titleLabel = ctk.CTkLabel(
            titleStack, 
            text=self._t("app_title"),
            font=Theme.TITLE_FONT,
            text_color=Theme.TEXT_COLOR
        )
        titleLabel.pack(anchor="w")
        
        subtitleLabel = ctk.CTkLabel(
            titleStack,
            text=self._t("app_subtitle"),
            font=Theme.TINY_FONT,
            text_color=Theme.TEXT_SECONDARY
        )
        subtitleLabel.pack(anchor="w")
        
        # Right side - Action buttons
        self.actionsFrame = ctk.CTkFrame(headerFrame, fg_color="transparent")
        self.actionsFrame.pack(side="right")
        
        # Pro badge
        proBadge = ctk.CTkFrame(
            self.actionsFrame,
            fg_color=Theme.GRADIENT_START,
            corner_radius=8
        )
        proBadge.pack(side="left", padx=(0, 12))
        
        proLabel = ctk.CTkLabel(
            proBadge, 
            text="✨ PRO", 
            font=Theme.PRO_LABEL_FONT,
            text_color="white"
        )
        proLabel.pack(padx=12, pady=6)

        # Settings button
        self.settingsBtn = ctk.CTkButton(
            self.actionsFrame, 
            text="⚙️", 
            command=self._showSettings,
            fg_color=Theme.CARD_COLOR, 
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_COLOR,
            width=45, 
            height=38,
            font=("Segoe UI", 16),
            corner_radius=10
        )
        self.settingsBtn.pack(side="right", padx=(0, 8))

        # History button
        historyBtn = ctk.CTkButton(
            self.actionsFrame, 
            text=f"📋 {self._t('buttons.history')}", 
            command=self._showHistory,
            fg_color=Theme.CARD_COLOR, 
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_COLOR,
            width=110, 
            height=38,
            font=Theme.SMALL_FONT,
            corner_radius=10
        )
        historyBtn.pack(side="right", padx=(0, 12))
        
    def _createMainCard(self, parent):
        """Create main content card with enhanced styling"""
        # Card with subtle shadow effect
        cardShadow = ctk.CTkFrame(
            parent, 
            fg_color=Theme.SHADOW_COLOR,
            corner_radius=Theme.BORDER_RADIUS + 1
        )
        cardShadow.pack(fill="both", expand=True)
        
        mainCard = ctk.CTkFrame(
            cardShadow, 
            fg_color=Theme.CARD_COLOR, 
            corner_radius=Theme.BORDER_RADIUS
        )
        mainCard.pack(fill="both", expand=True, padx=2, pady=2)
        
        self._createUrlSection(mainCard)
        self._createInfoCard(mainCard)
        self._createSettingsSection(mainCard)
        self._createProgressSection(mainCard)
        self._createDownloadButton(mainCard)
        
    def _createUrlSection(self, parent):
        """Create enhanced URL input section"""
        urlSection = ctk.CTkFrame(parent, fg_color="transparent")
        urlSection.pack(fill="x", padx=Theme.CARD_PADDING, pady=(Theme.CARD_PADDING, 0))
        
        # Label with icon
        labelFrame = ctk.CTkFrame(urlSection, fg_color="transparent")
        labelFrame.pack(anchor="w", pady=(0, 10))
        
        urlLabel = ctk.CTkLabel(
            labelFrame, 
            text=f"🔗 {self._t('labels.video_url')}", 
            font=Theme.SECTION_LABEL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        urlLabel.pack(side="left")
        
        # Helper text with supported platforms
        platforms = ", ".join(self.config['supported_platforms'][:3])
        helperText = ctk.CTkLabel(
            labelFrame,
            text=f"• {platforms} & more",
            font=Theme.TINY_FONT,
            text_color=Theme.MUTED_COLOR
        )
        helperText.pack(side="left", padx=(8, 0))
        
        urlInputFrame = ctk.CTkFrame(urlSection, fg_color="transparent")
        urlInputFrame.pack(fill="x")
        
        self.urlEntry = ModernEntry(
            urlInputFrame, 
            "https://youtube.com/watch?v=...", 
            "🔗"
        )
        self.urlEntry.pack(side="left", fill="both", expand=True, padx=(0, 12))
        
        self.fetchBtn = ModernButton(
            urlInputFrame, 
            self._t("buttons.fetch_info"),
            self._onFetchClicked,
            bgColor=Theme.SECONDARY_COLOR, 
            hoverColor=Theme.SECONDARY_HOVER,
            width=130, 
            height=52
        )
        self.fetchBtn.pack(side="right")
        
    def _createInfoCard(self, parent):
        """Create enhanced video info display card"""
        self.infoCard = InfoCard(parent)
        self.infoCard.pack(fill="x", padx=Theme.CARD_PADDING, pady=(Theme.ELEMENT_SPACING, 0))
        
        infoContent = ctk.CTkFrame(self.infoCard, fg_color="transparent")
        infoContent.pack(expand=True, pady=16, padx=20, fill="both")
        
        # Status icon and title
        titleFrame = ctk.CTkFrame(infoContent, fg_color="transparent")
        titleFrame.pack(fill="x", anchor="w")
        
        self.statusIcon = ctk.CTkLabel(
            titleFrame,
            text="⏳",
            font=("Segoe UI", 24),
            fg_color="transparent"
        )
        self.statusIcon.pack(side="left", padx=(0, 12), anchor="n")
        
        titleStack = ctk.CTkFrame(titleFrame, fg_color="transparent")
        titleStack.pack(side="left", fill="both", expand=True)
        
        self.videoTitleEntry = ctk.CTkEntry(
            titleStack,
            placeholder_text=self._t("messages.paste_url"),
            font=Theme.NORMAL_FONT,
            text_color=Theme.TEXT_COLOR,
            fg_color=Theme.INPUT_BG,
            border_width=1,
            border_color=Theme.INPUT_BORDER,
            height=40
        )
        self.videoTitleEntry.pack(anchor="w", fill="x")
        
        def onTitleFocusIn(e):
            self.videoTitleEntry.configure(border_color=Theme.SECONDARY_COLOR)
            
        def onTitleFocusOut(e):
            self.videoTitleEntry.configure(border_color=Theme.INPUT_BORDER)

        self.videoTitleEntry.bind("<FocusIn>", onTitleFocusIn)
        self.videoTitleEntry.bind("<FocusOut>", onTitleFocusOut)

        self.videoDurationLabel = ctk.CTkLabel(
            titleStack,
            text=self._t("messages.paste_url"),
            font=Theme.SMALL_FONT,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.videoDurationLabel.pack(anchor="w", pady=(4, 0))
        
    def _createSettingsSection(self, parent):
        """Create enhanced settings section"""
        settingsFrame = ctk.CTkFrame(parent, fg_color="transparent")
        settingsFrame.pack(fill="x", padx=Theme.CARD_PADDING, pady=(Theme.ELEMENT_SPACING, 0))
        
        # Two column layout
        leftColumn = ctk.CTkFrame(settingsFrame, fg_color="transparent")
        leftColumn.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self._createFormatSelection(leftColumn)
        self._createQualitySelection(leftColumn)
        
        rightColumn = ctk.CTkFrame(settingsFrame, fg_color="transparent")
        rightColumn.pack(side="right", fill="both", expand=True, padx=(8, 0))
        
        self._createPathSelection(rightColumn)
        
    def _createFormatSelection(self, parent):
        """Create modern format selection with toggle style"""
        formatSection = ctk.CTkFrame(parent, fg_color="transparent")
        formatSection.pack(fill="x")

        formatLabel = ctk.CTkLabel(
            formatSection, 
            text=f"🎹 {self._t('labels.output_format')}", 
            font=Theme.SECTION_LABEL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        formatLabel.pack(anchor="w", pady=(0, 10))
        
        # Segmented control style
        formatBtnFrame = ctk.CTkFrame(
            formatSection, 
            fg_color=Theme.INPUT_BG, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.INPUT_BORDER
        )
        formatBtnFrame.pack(fill="x", pady=3)
        
        self.mp4Btn = ctk.CTkRadioButton(
            formatBtnFrame, 
            text=self._t("formats.video_mp4"),
            variable=self.formatVar, 
            value="MP4",
            font=Theme.SMALL_FONT,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.TEXT_COLOR,
            command=self._onFormatChange,
            radiobutton_width=20,
            radiobutton_height=20
        )
        self.mp4Btn.pack(side="left", padx=18, pady=12)
        
        self.mp3Btn = ctk.CTkRadioButton(
            formatBtnFrame, 
            text=self._t("formats.audio_mp3"),
            variable=self.formatVar, 
            value="MP3",
            font=Theme.SMALL_FONT,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.TEXT_COLOR,
            command=self._onFormatChange,
            radiobutton_width=20,
            radiobutton_height=20
        )
        self.mp3Btn.pack(side="left", padx=18, pady=12)
        
    def _createQualitySelection(self, parent):
        """Create enhanced quality dropdown"""
        qualityLabel = ctk.CTkLabel(
            parent, 
            text=f"⚙️ {self._t('labels.video_quality')}", 
            font=Theme.SECTION_LABEL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        qualityLabel.pack(anchor="w", pady=(Theme.ELEMENT_SPACING, 10))
        
        # Get quality options from config
        qualityOptions = self.config.get('quality_options', ['best', '1080p', '720p', '480p', '360p'])
        
        from .custom_widgets import CustomDropdown
        
        self.qualityCombo = CustomDropdown(
            parent,
            variable=self.qualityVar,
            values=qualityOptions,
            font=Theme.SMALL_FONT,
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_COLOR,
            corner_radius=12,
            height=48
        )
        self.qualityCombo.pack(fill="x")
        
    def _createPathSelection(self, parent):
        """Create enhanced output path section"""
        pathLabel = ctk.CTkLabel(
            parent, 
            text=f"📁 {self._t('labels.save_location')}", 
            font=Theme.SECTION_LABEL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        pathLabel.pack(anchor="w", pady=(0, 10))
        
        pathInputFrame = ctk.CTkFrame(
            parent, 
            fg_color=Theme.INPUT_BG, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.INPUT_BORDER
        )
        pathInputFrame.pack(fill="x")
        
        pathEntry = ctk.CTkEntry(
            pathInputFrame, 
            textvariable=self.outputPathVar,
            font=Theme.SMALL_FONT,
            border_width=0,
            fg_color="transparent",
            text_color=Theme.TEXT_COLOR
        )
        pathEntry.pack(side="left", fill="both", expand=True, padx=16, pady=12)
        
        # Open folder button
        openDirBtn = ModernButton(
            pathInputFrame,
            "📂",
            self._openDownloadPath,
            bgColor=Theme.SECONDARY_COLOR,
            hoverColor=Theme.SECONDARY_HOVER,
            width=36,
            height=36
        )
        openDirBtn.pack(side="right", padx=8, pady=8)

        browseBtn = ModernButton(
            pathInputFrame,
            self._t("buttons.browse"),
            self._browsePath,
            bgColor=Theme.SECONDARY_COLOR,
            hoverColor=Theme.SECONDARY_HOVER,
            width=90,
            height=36
        )
        browseBtn.pack(side="right", padx=8, pady=8)
        
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
        """Create enhanced progress section"""
        progressFrame = ctk.CTkFrame(parent, fg_color="transparent")
        progressFrame.pack(fill="x", padx=Theme.CARD_PADDING, pady=(Theme.ELEMENT_SPACING, 0))
        
        # Status with better hierarchy
        statusContainer = ctk.CTkFrame(progressFrame, fg_color="transparent")
        statusContainer.pack(fill="x", pady=(0, 10))
        
        self.statusLabel = ctk.CTkLabel(
            statusContainer, 
            text=self._t("status.ready"),
            font=Theme.SMALL_FONT,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.statusLabel.pack(side="left")
        
        self.percentLabel = ctk.CTkLabel(
            statusContainer,
            text="",
            font=Theme.SMALL_FONT,
            text_color=Theme.SECONDARY_COLOR,
            anchor="e"
        )
        self.percentLabel.pack(side="right")
        
        # Enhanced progress bar
        self.progressBar = AnimatedProgressBar(progressFrame)
        self.progressBar.pack(fill="x")
        self.progressBar.set(0)
        
    def _createDownloadButton(self, parent):
        """Create enhanced download button"""
        downloadBtnFrame = ctk.CTkFrame(parent, fg_color="transparent")
        downloadBtnFrame.pack(pady=(Theme.ELEMENT_SPACING, Theme.CARD_PADDING))
        
        self.downloadBtn = ModernButton(
            downloadBtnFrame, 
            f"⬇️  {self._t('buttons.download_now')}",
            self._onDownloadClicked,
            bgColor=Theme.ACCENT_COLOR,
            hoverColor=Theme.ACCENT_HOVER,
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
            self.qualityCombo.configure(state='normal')
    
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
        
        # Show toast for errors
        self._showToast(f"Error: {errorMsg}", duration=3000, isSuccess=False)