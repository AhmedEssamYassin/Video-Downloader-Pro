"""
Settings dialog window using ttkbootstrap
Provides theme switcher, language selector, and preferences with modern flat design
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from pathlib import Path

from .theme import Theme
from .custom_widgets import CustomDropdown
from .custom_messagebox import CustomMessageBox
from ..utils import AssetLoader, getTranslation, SettingsManager


class SettingsDialog(tk.Toplevel):
    """Settings dialog for user preferences"""
    
    def __init__(self, parent, mainGUI):
        super().__init__(parent)
        self.mainGUI = mainGUI
        self.currentLanguage = mainGUI.currentLanguage
        
        # Load current settings
        self.settings = SettingsManager.loadSettings()
        self.originalSettings = self.settings.copy()
        
        # Track if restart is needed
        self.needsRestart = False
        
        self.title(self._t("settings.title"))
        
        # Set icon
        try:
            iconPath = AssetLoader.getImagePath("icon.ico")
            if iconPath.exists():
                self.iconbitmap(iconPath)
        except:
            pass
        
        # Window size and position
        windowWidth = 650
        windowHeight = 600
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        centerX = int(screenWidth/2 - windowWidth/2)
        centerY = int(screenHeight/2 - windowHeight/2)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        self.resizable(False, False)
        
        self.configure(bg=Theme.BG_COLOR)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Fade in
        self.attributes('-alpha', 0.0)
        self._createWidgets()
        self._loadCurrentSettings()
        self._fadeIn()
        
        self.protocol("WM_DELETE_WINDOW", self._onClose)
    
    def _t(self, key):
        """Get translation"""
        return getTranslation(key, self.currentLanguage)
    
    def _fadeIn(self):
        """Smooth fade-in animation"""
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(20, self._fadeIn)
    
    def _createWidgets(self):
        """Create all dialog widgets"""
        mainContainer = tk.Frame(self, bg=Theme.BG_COLOR)
        mainContainer.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self._createHeader(mainContainer)
        
        # Settings card
        settingsCard = tk.Frame(
            mainContainer,
            bg=Theme.CARD_COLOR,
            relief=FLAT,
            borderwidth=1,
            highlightbackground=Theme.INPUT_BORDER,
            highlightthickness=1
        )
        settingsCard.pack(fill=BOTH, expand=True, pady=(0, 16))
        
        # Scrollable frame for settings
        scrollCanvas = tk.Canvas(settingsCard, bg=Theme.CARD_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(settingsCard, orient=VERTICAL, command=scrollCanvas.yview, bootstyle=INFO)
        scrollFrame = tk.Frame(scrollCanvas, bg=Theme.CARD_COLOR)
        
        scrollFrame.bind(
            "<Configure>",
            lambda e: scrollCanvas.configure(scrollregion=scrollCanvas.bbox("all"))
        )
        
        scrollCanvas.create_window((0, 0), window=scrollFrame, anchor=NW)
        scrollCanvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollCanvas.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)
        
        # Settings sections
        self._createAppearanceSection(scrollFrame)
        self._createLanguageSection(scrollFrame)
        self._createDownloadSection(scrollFrame)
        self._createNotificationSection(scrollFrame)
        self._createAdvancedSection(scrollFrame)
        
        # Action buttons
        self._createActionButtons(mainContainer)
    
    def _createHeader(self, parent):
        """Create header section"""
        headerFrame = tk.Frame(parent, bg=Theme.BG_COLOR)
        headerFrame.pack(fill=X, pady=(0, 16))
        
        # Icon and title
        titleContainer = tk.Frame(headerFrame, bg=Theme.BG_COLOR)
        titleContainer.pack(side=LEFT)
        
        iconLabel = tk.Label(
            titleContainer,
            text="⚙️",
            font=("Segoe UI", 28),
            bg=Theme.BG_COLOR,
            fg=Theme.TEXT_COLOR
        )
        iconLabel.pack(side=LEFT, padx=(0, 12))
        
        titleStack = tk.Frame(titleContainer, bg=Theme.BG_COLOR)
        titleStack.pack(side=LEFT)
        
        titleLabel = tk.Label(
            titleStack,
            text=self._t("settings.title"),
            font=("Segoe UI", 24, "bold"),
            fg=Theme.TEXT_COLOR,
            bg=Theme.BG_COLOR
        )
        titleLabel.pack(anchor=W)
        
        subtitleLabel = tk.Label(
            titleStack,
            text=self._t("settings.subtitle"),
            font=Theme.SMALL_FONT,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_COLOR
        )
        subtitleLabel.pack(anchor=W)
    
    def _createSectionHeader(self, parent, icon, title):
        """Create a section header"""
        headerFrame = tk.Frame(parent, bg=Theme.CARD_COLOR)
        headerFrame.pack(fill=X, pady=(16, 12))
        
        headerLabel = tk.Label(
            headerFrame,
            text=f"{icon} {title}",
            font=("Segoe UI", 16, "bold"),
            fg=Theme.TEXT_COLOR,
            bg=Theme.CARD_COLOR
        )
        headerLabel.pack(side=LEFT)
        
        # Divider line
        divider = tk.Frame(headerFrame, bg=Theme.DIVIDER, height=2)
        divider.pack(side=LEFT, fill=X, expand=True, padx=(12, 0))
    
    def _createAppearanceSection(self, parent):
        """Create appearance settings section"""
        self._createSectionHeader(parent, "🎨", self._t("settings.appearance.title"))
        
        sectionFrame = tk.Frame(parent, bg=Theme.INFO_CARD_BG)
        sectionFrame.pack(fill=X, pady=(0, 8))
        
        contentFrame = tk.Frame(sectionFrame, bg=Theme.INFO_CARD_BG)
        contentFrame.pack(fill=X, padx=20, pady=16)
        
        # Theme selector
        themeFrame = tk.Frame(contentFrame, bg=Theme.INFO_CARD_BG)
        themeFrame.pack(fill=X, pady=(0, 12))
        
        themeLabel = tk.Label(
            themeFrame,
            text=self._t("settings.appearance.theme"),
            font=Theme.NORMAL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.INFO_CARD_BG
        )
        themeLabel.pack(side=LEFT)
        
        self.themeVar = tk.StringVar(value=self.settings.get('theme', 'dark'))
        
        themeToggleFrame = tk.Frame(themeFrame, bg=Theme.INPUT_BG)
        themeToggleFrame.pack(side=RIGHT)
        
        darkBtn = ttk.Radiobutton(
            themeToggleFrame,
            text="Dark",
            variable=self.themeVar,
            value="dark",
            command=self._onThemeChange,
            bootstyle=INFO,
            cursor="hand2"
        )
        darkBtn.pack(side=LEFT, padx=12, pady=8)
        
        lightBtn = ttk.Radiobutton(
            themeToggleFrame,
            text="Light",
            variable=self.themeVar,
            value="light",
            command=self._onThemeChange,
            bootstyle=INFO,
            cursor="hand2"
        )
        lightBtn.pack(side=LEFT, padx=12, pady=8)
        
        # Theme description
        themeDesc = tk.Label(
            contentFrame,
            text=self._t("settings.appearance.theme_desc"),
            font=Theme.TINY_FONT,
            fg=Theme.MUTED_COLOR,
            bg=Theme.INFO_CARD_BG,
            wraplength=550,
            justify=LEFT
        )
        themeDesc.pack(fill=X)
    
    def _createLanguageSection(self, parent):
        """Create language settings section"""
        self._createSectionHeader(parent, "🌐", self._t("settings.language.title"))
        
        sectionFrame = tk.Frame(parent, bg=Theme.INFO_CARD_BG)
        sectionFrame.pack(fill=X, pady=(0, 8))
        
        contentFrame = tk.Frame(sectionFrame, bg=Theme.INFO_CARD_BG)
        contentFrame.pack(fill=X, padx=20, pady=16)
        
        # Language selector
        langFrame = tk.Frame(contentFrame, bg=Theme.INFO_CARD_BG)
        langFrame.pack(fill=X, pady=(0, 12))
        
        langLabel = tk.Label(
            langFrame,
            text=self._t("settings.language.select"),
            font=Theme.NORMAL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.INFO_CARD_BG
        )
        langLabel.pack(side=LEFT)
        
        # Get available languages
        languages = AssetLoader.getAvailableLanguages()
        self.languageNames = {
            'en': 'English',
            'ar': 'العربية'
        }
        
        self.langVar = tk.StringVar(value=self.settings.get('language', 'en'))
        
        self.langCombo = CustomDropdown(
            langFrame,
            variable=self.langVar,
            values=[self.languageNames.get(lang, lang) for lang in languages],
            command=self._onLanguageChange,
            font=Theme.SMALL_FONT
        )
        self.langCombo.pack(side=RIGHT)
        
        # Set current value
        currentLang = self.languageNames.get(self.settings.get('language', 'en'), 'English')
        self.langCombo.set(currentLang)
        
        # Language description
        langDesc = tk.Label(
            contentFrame,
            text=self._t("settings.language.restart_required"),
            font=Theme.TINY_FONT,
            fg=Theme.WARNING_COLOR,
            bg=Theme.INFO_CARD_BG,
            wraplength=550,
            justify=LEFT
        )
        langDesc.pack(fill=X)
    
    def _createDownloadSection(self, parent):
        """Create download settings section"""
        self._createSectionHeader(parent, "⬇️", self._t("settings.downloads.title"))
        
        sectionFrame = tk.Frame(parent, bg=Theme.INFO_CARD_BG)
        sectionFrame.pack(fill=X, pady=(0, 8))
        
        contentFrame = tk.Frame(sectionFrame, bg=Theme.INFO_CARD_BG)
        contentFrame.pack(fill=X, padx=20, pady=16)
        
        # Default download path
        pathFrame = tk.Frame(contentFrame, bg=Theme.INFO_CARD_BG)
        pathFrame.pack(fill=X, pady=(0, 12))
        
        pathLabel = tk.Label(
            pathFrame,
            text=self._t("settings.downloads.default_path"),
            font=Theme.NORMAL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.INFO_CARD_BG
        )
        pathLabel.pack(anchor=W, pady=(0, 8))
        
        pathInputFrame = tk.Frame(pathFrame, bg=Theme.INPUT_BG)
        pathInputFrame.pack(fill=X)
        
        self.pathEntry = ttk.Entry(
            pathInputFrame,
            font=Theme.SMALL_FONT,
            bootstyle=INFO
        )
        self.pathEntry.pack(side=LEFT, fill=BOTH, expand=True, padx=12, pady=10)
        
        browseBtn = ttk.Button(
            pathInputFrame,
            text="📁",
            width=3,
            command=self._browsePath,
            bootstyle=PRIMARY
        )
        browseBtn.pack(side=RIGHT, padx=8, pady=8)
        
        # Default quality
        qualityFrame = tk.Frame(contentFrame, bg=Theme.INFO_CARD_BG)
        qualityFrame.pack(fill=X, pady=(0, 12))
        
        qualityLabel = tk.Label(
            qualityFrame,
            text=self._t("settings.downloads.default_quality"),
            font=Theme.NORMAL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.INFO_CARD_BG
        )
        qualityLabel.pack(side=LEFT)
        
        self.qualityVar = tk.StringVar(value=self.settings.get('default_quality', 'best'))
        
        qualityCombo = CustomDropdown(
            qualityFrame,
            variable=self.qualityVar,
            values=AssetLoader.getQualityOptions(),
            font=Theme.SMALL_FONT
        )
        qualityCombo.pack(side=RIGHT)
        
        # Default format
        formatFrame = tk.Frame(contentFrame, bg=Theme.INFO_CARD_BG)
        formatFrame.pack(fill=X, pady=(0, 12))
        
        formatLabel = tk.Label(
            formatFrame,
            text=self._t("settings.downloads.default_format"),
            font=Theme.NORMAL_FONT,
            fg=Theme.TEXT_COLOR,
            bg=Theme.INFO_CARD_BG
        )
        formatLabel.pack(side=LEFT)
        
        self.formatVar = tk.StringVar(value=self.settings.get('default_format', 'MP4'))
        
        formatCombo = CustomDropdown(
            formatFrame,
            variable=self.formatVar,
            values=AssetLoader.getFormatOptions(),
            font=Theme.SMALL_FONT
        )
        formatCombo.pack(side=RIGHT)
    
    def _createNotificationSection(self, parent):
        """Create notification settings section"""
        self._createSectionHeader(parent, "🔔", self._t("settings.notifications.title"))
        
        sectionFrame = tk.Frame(parent, bg=Theme.INFO_CARD_BG)
        sectionFrame.pack(fill=X, pady=(0, 8))
        
        contentFrame = tk.Frame(sectionFrame, bg=Theme.INFO_CARD_BG)
        contentFrame.pack(fill=X, padx=20, pady=16)
        
        # Enable notifications
        self.notificationsVar = tk.BooleanVar(value=self.settings.get('notifications_enabled', True))
        
        notifCheckbox = ttk.Checkbutton(
            contentFrame,
            text=self._t("settings.notifications.enable"),
            variable=self.notificationsVar,
            bootstyle="round-toggle"
        )
        notifCheckbox.pack(anchor=W, pady=(0, 8))
        
        notifDesc = tk.Label(
            contentFrame,
            text=self._t("settings.notifications.desc"),
            font=Theme.TINY_FONT,
            fg=Theme.MUTED_COLOR,
            bg=Theme.INFO_CARD_BG,
            wraplength=550,
            justify=LEFT
        )
        notifDesc.pack(fill=X)
    
    def _createAdvancedSection(self, parent):
        """Create advanced settings section"""
        self._createSectionHeader(parent, "🔧", self._t("settings.advanced.title"))
        
        sectionFrame = tk.Frame(parent, bg=Theme.INFO_CARD_BG)
        sectionFrame.pack(fill=X, pady=(0, 8))
        
        contentFrame = tk.Frame(sectionFrame, bg=Theme.INFO_CARD_BG)
        contentFrame.pack(fill=X, padx=20, pady=16)
        
        # Remember last path
        self.rememberPathVar = tk.BooleanVar(value=self.settings.get('remember_last_path', True))
        
        rememberCheckbox = ttk.Checkbutton(
            contentFrame,
            text=self._t("settings.advanced.remember_path"),
            variable=self.rememberPathVar,
            bootstyle="round-toggle"
        )
        rememberCheckbox.pack(anchor=W, pady=(0, 12))
        
        # Reset button
        resetBtn = ttk.Button(
            contentFrame,
            text="🔄 " + self._t("settings.advanced.reset_defaults"),
            command=self._resetToDefaults,
            bootstyle=SECONDARY,
            width=25
        )
        resetBtn.pack(anchor=W)
    
    def _createActionButtons(self, parent):
        """Create action buttons at bottom"""
        buttonFrame = tk.Frame(parent, bg=Theme.BG_COLOR)
        buttonFrame.pack(fill=X)
        
        # Cancel button
        cancelBtn = ttk.Button(
            buttonFrame,
            text=self._t("buttons.cancel"),
            command=self._onClose,
            bootstyle=SECONDARY,
            width=15,
            cursor="hand2"
        )
        cancelBtn.pack(side=LEFT, padx=(0, 12))
        
        # Save button
        saveBtn = ttk.Button(
            buttonFrame,
            text="💾 " + self._t("buttons.save"),
            command=self._saveSettings,
            bootstyle=PRIMARY,
            width=15,
            cursor="hand2"
        )
        saveBtn.pack(side=RIGHT)
    
    def _loadCurrentSettings(self):
        """Load current settings into UI"""
        # Path
        defaultPath = self.settings.get('default_download_path', '')
        if not defaultPath:
            defaultPath = str(Path.home() / "Downloads")
        self.pathEntry.insert(0, defaultPath)
        
        # Theme
        self.themeVar.set(self.settings.get('theme', 'dark'))
        
        # Language
        lang = self.settings.get('language', 'en')
        langName = self.languageNames.get(lang, 'English')
        self.langCombo.set(langName)
    
    def _browsePath(self):
        """Browse for download directory"""
        currentPath = self.pathEntry.get() or str(Path.home() / "Downloads")
        directory = filedialog.askdirectory(initialdir=currentPath)
        if directory:
            self.pathEntry.delete(0, tk.END)
            self.pathEntry.insert(0, directory)
    
    def _onThemeChange(self):
        """Handle theme change"""
        self.needsRestart = True
        

    def _onLanguageChange(self, selection):
        """Handle language change"""
        # Map display name back to language code
        langMap = {v: k for k, v in self.languageNames.items()}
        newLang = langMap.get(selection, 'en')
        
        if newLang != self.settings.get('language', 'en'):
            self.needsRestart = True
    
    def _resetToDefaults(self):
        """Reset all settings to defaults"""
        result = CustomMessageBox.askYesNo(
            self,
            self._t("settings.advanced.reset_title"),
            self._t("settings.advanced.reset_confirm")
        )
        
        if result:
            # Load defaults
            defaultConfig = AssetLoader.loadConfig()
            self.settings = defaultConfig['settings'].copy()
            
            # Update UI
            self.pathEntry.delete(0, tk.END)
            defaultPath = self.settings.get('default_download_path', str(Path.home() / "Downloads"))
            self.pathEntry.insert(0, defaultPath)
            
            self.qualityVar.set(self.settings.get('default_quality', 'best'))
            self.formatVar.set(self.settings.get('default_format', 'MP4'))
            self.themeVar.set(self.settings.get('theme', 'dark'))
            self.notificationsVar.set(self.settings.get('notifications_enabled', True))
            self.rememberPathVar.set(self.settings.get('remember_last_path', True))
            
            lang = self.settings.get('language', 'en')
            self.langCombo.set(self.languageNames.get(lang, 'English'))
            
            # Apply theme
            Theme.setTheme(self.settings.get('theme', 'dark'))
    
    def _saveSettings(self):
        """Save all settings"""
        # Gather settings from UI
        newSettings = {
            'default_download_path': self.pathEntry.get(),
            'default_quality': self.qualityVar.get(),
            'default_format': self.formatVar.get(),
            'theme': self.themeVar.get(),
            'notifications_enabled': self.notificationsVar.get(),
            'remember_last_path': self.rememberPathVar.get(),
        }
        
        # Handle language
        langName = self.langCombo.get()
        langMap = {v: k for k, v in self.languageNames.items()}
        newSettings['language'] = langMap.get(langName, 'en')
            
        # Save to file
        success = SettingsManager.saveSettings(newSettings)
        
        if success:
            # Apply theme immediately
            Theme.setTheme(newSettings['theme'])
            
            # Update main GUI settings
            self.mainGUI.config = AssetLoader.loadConfig()
            self.mainGUI.config['settings'] = newSettings
            self.mainGUI.currentLanguage = newSettings['language']
            
            # Update main GUI variables if needed
            if hasattr(self.mainGUI, 'outputPathVar'):
                if not newSettings['remember_last_path']:
                    self.mainGUI.outputPathVar.set(newSettings['default_download_path'])
            if hasattr(self.mainGUI, 'qualityVar'):
                self.mainGUI.qualityVar.set(newSettings['default_quality'])
            if hasattr(self.mainGUI, 'formatVar'):
                self.mainGUI.formatVar.set(newSettings['default_format'])
            
            if self.needsRestart:
                CustomMessageBox.showInfo(
                    self,
                    self._t("settings.restart_title"),
                    self._t("settings.restart_message") + "\n\nPlease close and reopen the application for the changes to take effect."
                )
                self.destroy()
            else:
                CustomMessageBox.showInfo(
                    self,
                    self._t("settings.saved_title"),
                    self._t("settings.saved_message")
                )
                self.destroy()
        else:
            CustomMessageBox.showError(
                self,
                "Error",
                self._t("settings.save_error")
            )
    
    def _onClose(self):
        """Handle window close"""
        # Check if settings changed
        currentSettings = {
            'default_download_path': self.pathEntry.get(),
            'default_quality': self.qualityVar.get(),
            'default_format': self.formatVar.get(),
            'theme': self.themeVar.get(),
            'notifications_enabled': self.notificationsVar.get(),
            'remember_last_path': self.rememberPathVar.get(),
        }
        
        langName = self.langCombo.get()
        langMap = {v: k for k, v in self.languageNames.items()}
        currentSettings['language'] = langMap.get(langName, 'en')
        
        # Compare with original
        changed = False
        for key, value in currentSettings.items():
            if self.originalSettings.get(key) != value:
                changed = True
                break
        
        if changed:
            result = CustomMessageBox.askYesNo(
                self,
                self._t("settings.unsaved_title"),
                self._t("settings.unsaved_message")
            )
            if not result:
                return
        
        self.destroy()
