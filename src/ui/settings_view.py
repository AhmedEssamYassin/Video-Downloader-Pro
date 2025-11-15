"""
Settings dialog window with theme switcher, language selector, and preferences
"""

import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from pathlib import Path

from .theme import Theme
from .custom_widgets import ModernButton
from .custom_messagebox import CustomMessageBox
from .custom_widgets import CustomDropdown
from ..utils import AssetLoader, getTranslation, SettingsManager


class SettingsDialog(ctk.CTkToplevel):
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
        
        self.configure(fg_color=Theme.BG_COLOR)
        
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
        mainContainer = ctk.CTkFrame(self, fg_color="transparent")
        mainContainer.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._createHeader(mainContainer)
        
        # Settings card
        settingsCard = ctk.CTkFrame(
            mainContainer,
            fg_color=Theme.CARD_COLOR,
            corner_radius=Theme.BORDER_RADIUS
        )
        settingsCard.pack(fill="both", expand=True, pady=(0, 16))
        
        # Scrollable frame for settings
        scrollFrame = ctk.CTkScrollableFrame(
            settingsCard,
            fg_color="transparent",
            scrollbar_button_color=Theme.SECONDARY_COLOR,
            scrollbar_button_hover_color=Theme.SECONDARY_HOVER
        )
        scrollFrame.pack(fill="both", expand=True, padx=20, pady=20)
        
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
        headerFrame = ctk.CTkFrame(parent, fg_color="transparent")
        headerFrame.pack(fill="x", pady=(0, 16))
        
        # Icon and title
        titleContainer = ctk.CTkFrame(headerFrame, fg_color="transparent")
        titleContainer.pack(side="left")
        
        iconLabel = ctk.CTkLabel(
            titleContainer,
            text="⚙️",
            font=("Segoe UI", 28)
        )
        iconLabel.pack(side="left", padx=(0, 12))
        
        titleStack = ctk.CTkFrame(titleContainer, fg_color="transparent")
        titleStack.pack(side="left")
        
        titleLabel = ctk.CTkLabel(
            titleStack,
            text=self._t("settings.title"),
            font=("Segoe UI", 24, "bold"),
            text_color=Theme.TEXT_COLOR
        )
        titleLabel.pack(anchor="w")
        
        subtitleLabel = ctk.CTkLabel(
            titleStack,
            text=self._t("settings.subtitle"),
            font=Theme.SMALL_FONT,
            text_color=Theme.TEXT_SECONDARY
        )
        subtitleLabel.pack(anchor="w")
    
    def _createSectionHeader(self, parent, icon, title):
        """Create a section header"""
        headerFrame = ctk.CTkFrame(parent, fg_color="transparent")
        headerFrame.pack(fill="x", pady=(16, 12))
        
        headerLabel = ctk.CTkLabel(
            headerFrame,
            text=f"{icon} {title}",
            font=("Segoe UI", 16, "bold"),
            text_color=Theme.TEXT_COLOR
        )
        headerLabel.pack(side="left")
        
        # Divider line
        divider = ctk.CTkFrame(headerFrame, fg_color=Theme.DIVIDER, height=2)
        divider.pack(side="left", fill="x", expand=True, padx=(12, 0))
    
    def _createAppearanceSection(self, parent):
        """Create appearance settings section"""
        self._createSectionHeader(parent, "🎨", self._t("settings.appearance.title"))
        
        sectionFrame = ctk.CTkFrame(parent, fg_color=Theme.INFO_CARD_BG, corner_radius=12)
        sectionFrame.pack(fill="x", pady=(0, 8))
        
        contentFrame = ctk.CTkFrame(sectionFrame, fg_color="transparent")
        contentFrame.pack(fill="x", padx=20, pady=16)
        
        # Theme selector
        themeFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        themeFrame.pack(fill="x", pady=(0, 12))
        
        themeLabel = ctk.CTkLabel(
            themeFrame,
            text=self._t("settings.appearance.theme"),
            font=Theme.NORMAL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        themeLabel.pack(side="left")
        
        self.themeVar = tk.StringVar(value=self.settings.get('theme', 'dark'))
        
        themeToggleFrame = ctk.CTkFrame(themeFrame, fg_color=Theme.INPUT_BG, corner_radius=10)
        themeToggleFrame.pack(side="right")
        
        darkBtn = ctk.CTkRadioButton(
            themeToggleFrame,
            text="🌙 Dark",
            variable=self.themeVar,
            value="dark",
            font=Theme.SMALL_FONT,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.INPUT_TEXT,
            command=self._onThemeChange,
            radiobutton_width=18,
            radiobutton_height=18
        )
        darkBtn.pack(side="left", padx=12, pady=8)
        
        lightBtn = ctk.CTkRadioButton(
            themeToggleFrame,
            text="☀️ Light",
            variable=self.themeVar,
            value="light",
            font=Theme.SMALL_FONT,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.INPUT_TEXT,
            command=self._onThemeChange,
            radiobutton_width=18,
            radiobutton_height=18
        )
        lightBtn.pack(side="left", padx=12, pady=8)
        
        # Theme description
        themeDesc = ctk.CTkLabel(
            contentFrame,
            text=self._t("settings.appearance.theme_desc"),
            font=Theme.TINY_FONT,
            text_color=Theme.MUTED_COLOR,
            wraplength=550,
            justify="left"
        )
        themeDesc.pack(fill="x")
    
    def _createLanguageSection(self, parent):
        """Create language settings section"""
        self._createSectionHeader(parent, "🌐", self._t("settings.language.title"))
        
        sectionFrame = ctk.CTkFrame(parent, fg_color=Theme.INFO_CARD_BG, corner_radius=12)
        sectionFrame.pack(fill="x", pady=(0, 8))
        
        contentFrame = ctk.CTkFrame(sectionFrame, fg_color="transparent")
        contentFrame.pack(fill="x", padx=20, pady=16)
        
        # Language selector
        langFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        langFrame.pack(fill="x", pady=(0, 12))
        
        langLabel = ctk.CTkLabel(
            langFrame,
            text=self._t("settings.language.select"),
            font=Theme.NORMAL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        langLabel.pack(side="left")
        
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
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_COLOR,
            width=200,
            height=40,
            corner_radius=10,
            font=Theme.SMALL_FONT
        )
        self.langCombo.pack(side="right")
        
        # Set current value
        currentLang = self.languageNames.get(self.settings.get('language', 'en'), 'English')
        self.langCombo.set(currentLang)
        
        # Language description
        langDesc = ctk.CTkLabel(
            contentFrame,
            text=self._t("settings.language.restart_required"),
            font=Theme.TINY_FONT,
            text_color=Theme.WARNING_COLOR,
            wraplength=550,
            justify="left"
        )
        langDesc.pack(fill="x")
    
    def _createDownloadSection(self, parent):
        """Create download settings section"""
        self._createSectionHeader(parent, "⬇️", self._t("settings.downloads.title"))
        
        sectionFrame = ctk.CTkFrame(parent, fg_color=Theme.INFO_CARD_BG, corner_radius=12)
        sectionFrame.pack(fill="x", pady=(0, 8))
        
        contentFrame = ctk.CTkFrame(sectionFrame, fg_color="transparent")
        contentFrame.pack(fill="x", padx=20, pady=16)
        
        # Default download path
        pathFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        pathFrame.pack(fill="x", pady=(0, 12))
        
        pathLabel = ctk.CTkLabel(
            pathFrame,
            text=self._t("settings.downloads.default_path"),
            font=Theme.NORMAL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        pathLabel.pack(anchor="w", pady=(0, 8))
        
        pathInputFrame = ctk.CTkFrame(pathFrame, fg_color=Theme.INPUT_BG, corner_radius=10)
        pathInputFrame.pack(fill="x")
        
        self.pathEntry = ctk.CTkEntry(
            pathInputFrame,
            font=Theme.SMALL_FONT,
            border_width=0,
            fg_color="transparent",
            text_color=Theme.TEXT_COLOR
        )
        self.pathEntry.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        
        browseBtn = ctk.CTkButton(
            pathInputFrame,
            text="📁",
            width=40,
            height=32,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            font=("Segoe UI", 14),
            corner_radius=8,
            command=self._browsePath
        )
        browseBtn.pack(side="right", padx=8, pady=8)
        
        # Default quality
        qualityFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        qualityFrame.pack(fill="x", pady=(0, 12))
        
        qualityLabel = ctk.CTkLabel(
            qualityFrame,
            text=self._t("settings.downloads.default_quality"),
            font=Theme.NORMAL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        qualityLabel.pack(side="left")
        
        self.qualityVar = tk.StringVar(value=self.settings.get('default_quality', 'best'))
        
        qualityCombo = CustomDropdown(
            qualityFrame,
            variable=self.qualityVar,
            values=AssetLoader.getQualityOptions(),
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_COLOR,
            height=40,
            corner_radius=10,
            font=Theme.SMALL_FONT
        )
        qualityCombo.pack(side="right")
        
        # Default format
        formatFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        formatFrame.pack(fill="x", pady=(0, 12))
        
        formatLabel = ctk.CTkLabel(
            formatFrame,
            text=self._t("settings.downloads.default_format"),
            font=Theme.NORMAL_FONT,
            text_color=Theme.TEXT_COLOR
        )
        formatLabel.pack(side="left")
        
        self.formatVar = tk.StringVar(value=self.settings.get('default_format', 'MP4'))
        
        formatCombo = CustomDropdown(
            formatFrame,
            variable=self.formatVar,
            values=AssetLoader.getFormatOptions(),
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_COLOR,
            height=40,
            corner_radius=10,
            font=Theme.SMALL_FONT
        )
        formatCombo.pack(side="right")
    
    def _createNotificationSection(self, parent):
        """Create notification settings section"""
        self._createSectionHeader(parent, "🔔", self._t("settings.notifications.title"))
        
        sectionFrame = ctk.CTkFrame(parent, fg_color=Theme.INFO_CARD_BG, corner_radius=12)
        sectionFrame.pack(fill="x", pady=(0, 8))
        
        contentFrame = ctk.CTkFrame(sectionFrame, fg_color="transparent")
        contentFrame.pack(fill="x", padx=20, pady=16)
        
        # Enable notifications
        self.notificationsVar = tk.BooleanVar(value=self.settings.get('notifications_enabled', True))
        
        notifCheckbox = ctk.CTkCheckBox(
            contentFrame,
            text=self._t("settings.notifications.enable"),
            variable=self.notificationsVar,
            font=Theme.NORMAL_FONT,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.TEXT_COLOR,
            checkbox_width=24,
            checkbox_height=24
        )
        notifCheckbox.pack(anchor="w", pady=(0, 8))
        
        notifDesc = ctk.CTkLabel(
            contentFrame,
            text=self._t("settings.notifications.desc"),
            font=Theme.TINY_FONT,
            text_color=Theme.MUTED_COLOR,
            wraplength=550,
            justify="left"
        )
        notifDesc.pack(fill="x")
    
    def _createAdvancedSection(self, parent):
        """Create advanced settings section"""
        self._createSectionHeader(parent, "🔧", self._t("settings.advanced.title"))
        
        sectionFrame = ctk.CTkFrame(parent, fg_color=Theme.INFO_CARD_BG, corner_radius=12)
        sectionFrame.pack(fill="x", pady=(0, 8))
        
        contentFrame = ctk.CTkFrame(sectionFrame, fg_color="transparent")
        contentFrame.pack(fill="x", padx=20, pady=16)
        
        # Remember last path
        self.rememberPathVar = tk.BooleanVar(value=self.settings.get('remember_last_path', True))
        
        rememberCheckbox = ctk.CTkCheckBox(
            contentFrame,
            text=self._t("settings.advanced.remember_path"),
            variable=self.rememberPathVar,
            font=Theme.NORMAL_FONT,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.TEXT_COLOR,
            checkbox_width=24,
            checkbox_height=24
        )
        rememberCheckbox.pack(anchor="w", pady=(0, 12))
        
        # Reset button
        resetBtn = ctk.CTkButton(
            contentFrame,
            text="🔄 " + self._t("settings.advanced.reset_defaults"),
            command=self._resetToDefaults,
            fg_color="#6c757d",
            hover_color="#5c636a",
            width=200,
            height=40,
            corner_radius=10,
            font=Theme.SMALL_FONT
        )
        resetBtn.pack(anchor="w")
    
    def _createActionButtons(self, parent):
        """Create action buttons at bottom"""
        buttonFrame = ctk.CTkFrame(parent, fg_color="transparent")
        buttonFrame.pack(fill="x")
        
        # Cancel button
        cancelBtn = ctk.CTkButton(
            buttonFrame,
            text=self._t("buttons.cancel"),
            command=self._onClose,
            fg_color="#6c757d",
            hover_color="#5c636a",
            width=140,
            height=46,
            corner_radius=12,
            font=("Segoe UI", 13, "bold")
        )
        cancelBtn.pack(side="left", padx=(0, 12))
        
        # Save button
        saveBtn = ctk.CTkButton(
            buttonFrame,
            text="💾 " + self._t("buttons.save"),
            command=self._saveSettings,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            width=140,
            height=46,
            corner_radius=12,
            font=("Segoe UI", 13, "bold")
        )
        saveBtn.pack(side="right")
    
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
        pass

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
            try:
                ctk.set_appearance_mode(self.settings.get('theme', 'dark'))
            except Exception as e:
                print(f"Error applying theme: {e}")
    
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
            # Apply theme immediately using CustomTkinter's built-in system
            try:
                ctk.set_appearance_mode(newSettings['theme'])
            except Exception as e:
                print(f"Error applying theme: {e}")
            
            # Update main GUI settings
            self.mainGUI.config = AssetLoader.loadConfig()
            self.mainGUI.config['settings'] = newSettings
            self.mainGUI.currentLanguage = newSettings['language']
            
            # Update main GUI variables if needed
            if hasattr(self.mainGUI, 'outputPathVar'):
                # Only update if remember_last_path is False
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
                    self._t("settings.restart_message")
                )
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