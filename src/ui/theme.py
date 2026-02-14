"""
Modern flat theme configuration using ttkbootstrap
Provides centralized colors, fonts, and styling for the entire application
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class Theme:
    """Centralized theme configuration with modern flat design"""
    
    # Color Palette - Modern and minimal
    ACCENT_COLOR = "#ff6b6b"
    ACCENT_HOVER = "#ff5252"
    SECONDARY_COLOR = "#4599DE"
    SECONDARY_HOVER = "#339af0"
    SUCCESS_COLOR = "#51cf66"
    WARNING_COLOR = "#ffc107"
    GRADIENT_START = "#667eea"
    GRADIENT_END = "#764ba2"
    
    # Neutral Colors
    BG_COLOR_LIGHT = "#f5f5f5"
    BG_COLOR_DARK = "#1a1a1a"
    CARD_COLOR_LIGHT = "#ffffff"
    CARD_COLOR_DARK = "#2b2b2b"
    CARD_HOVER_LIGHT = "#f8f9fa"
    CARD_HOVER_DARK = "#333333"
    INFO_CARD_BG_LIGHT = "#f8f9fa"
    INFO_CARD_BG_DARK = "#262638"
    INPUT_BG_LIGHT = "#e9ecef"
    INPUT_BG_DARK = "#333333"
    INPUT_TEXT_LIGHT = "#1a1a1a"
    INPUT_TEXT_DARK = "#e9ecef"
    INPUT_BORDER_LIGHT = "#ced4da"
    INPUT_BORDER_DARK = "#495057"
    DIVIDER_LIGHT = "#dee2e6"
    DIVIDER_DARK = "#495057"
    TEXT_COLOR_LIGHT = "#1a1a1a"
    TEXT_COLOR_DARK = "#e9ecef"
    TEXT_SECONDARY_LIGHT = "#6c757d"
    TEXT_SECONDARY_DARK = "#adb5bd"
    MUTED_COLOR = "#6c757d"
    SHADOW_COLOR_LIGHT = "#e9ecef"
    SHADOW_COLOR_DARK = "#0a0a0a"
    
    # Current theme colors (will be set based on mode)
    BG_COLOR = BG_COLOR_DARK
    CARD_COLOR = CARD_COLOR_DARK
    CARD_HOVER = CARD_HOVER_DARK
    INFO_CARD_BG = INFO_CARD_BG_DARK
    INPUT_BG = INPUT_BG_DARK
    INPUT_TEXT = INPUT_TEXT_DARK
    INPUT_BORDER = INPUT_BORDER_DARK
    DIVIDER = DIVIDER_DARK
    TEXT_COLOR = TEXT_COLOR_DARK
    TEXT_SECONDARY = TEXT_SECONDARY_DARK
    SHADOW_COLOR = SHADOW_COLOR_DARK
    
    # Fonts - Clean and modern
    TITLE_FONT = ("Segoe UI", 24, "bold")
    PRO_LABEL_FONT = ("Segoe UI", 13, "bold")
    SECTION_LABEL_FONT = ("Segoe UI", 13, "bold")
    NORMAL_FONT = ("Segoe UI", 13)
    SMALL_FONT = ("Segoe UI", 12)
    TINY_FONT = ("Segoe UI", 11)
    BUTTON_FONT = ("Segoe UI", 13, "bold")
    
    # Spacing and Sizing
    BORDER_RADIUS = 8  # Flatter, less rounded
    BUTTON_RADIUS = 6
    INPUT_RADIUS = 6
    CARD_PADDING = 20
    ELEMENT_SPACING = 12
    
    # Animation Durations (ms)
    TRANSITION_FAST = 150
    TRANSITION_NORMAL = 250
    TRANSITION_SLOW = 350
    
    # Current theme mode
    current_mode = "dark"
    
    @staticmethod
    def configureStyles(root, theme="darkly"):
        """Configure ttkbootstrap theme
        
        Args:
            root: The root window
            theme: ttkbootstrap theme name (darkly, flatly, cosmo, etc.)
        """
        # The theme is set at initialization via ttk.Window
        # This method can be used for additional style configuration
        pass
    
    @staticmethod
    def setTheme(mode: str):
        """Set the application theme (dark/light)
        
        Args:
            mode: "dark" or "light"
        """
        Theme.current_mode = mode
        
        if mode == "light":
            Theme.BG_COLOR = Theme.BG_COLOR_LIGHT
            Theme.CARD_COLOR = Theme.CARD_COLOR_LIGHT
            Theme.CARD_HOVER = Theme.CARD_HOVER_LIGHT
            Theme.INFO_CARD_BG = Theme.INFO_CARD_BG_LIGHT
            Theme.INPUT_BG = Theme.INPUT_BG_LIGHT
            Theme.INPUT_TEXT = Theme.INPUT_TEXT_LIGHT
            Theme.INPUT_BORDER = Theme.INPUT_BORDER_LIGHT
            Theme.DIVIDER = Theme.DIVIDER_LIGHT
            Theme.TEXT_COLOR = Theme.TEXT_COLOR_LIGHT
            Theme.TEXT_SECONDARY = Theme.TEXT_SECONDARY_LIGHT
            Theme.SHADOW_COLOR = Theme.SHADOW_COLOR_LIGHT
        else:
            Theme.BG_COLOR = Theme.BG_COLOR_DARK
            Theme.CARD_COLOR = Theme.CARD_COLOR_DARK
            Theme.CARD_HOVER = Theme.CARD_HOVER_DARK
            Theme.INFO_CARD_BG = Theme.INFO_CARD_BG_DARK
            Theme.INPUT_BG = Theme.INPUT_BG_DARK
            Theme.INPUT_TEXT = Theme.INPUT_TEXT_DARK
            Theme.INPUT_BORDER = Theme.INPUT_BORDER_DARK
            Theme.DIVIDER = Theme.DIVIDER_DARK
            Theme.TEXT_COLOR = Theme.TEXT_COLOR_DARK
            Theme.TEXT_SECONDARY = Theme.TEXT_SECONDARY_DARK
            Theme.SHADOW_COLOR = Theme.SHADOW_COLOR_DARK
    
    @staticmethod
    def getTtkTheme(mode: str):
        """Get the appropriate ttkbootstrap theme for the mode
        
        Args:
            mode: "dark" or "light"
            
        Returns:
            str: ttkbootstrap theme name
        """
        return "darkly" if mode == "dark" else "flatly"
    
    @staticmethod
    def applyHandCursor(widget):
        """Apply hand cursor to interactive widgets"""
        widget.configure(cursor="hand2")
