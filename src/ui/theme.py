"""
Enhanced theme with modern design principles and smooth animations
CustomTkinter handles light/dark switching automatically
"""

import customtkinter as ctk

class Theme:
    """Enhanced application color scheme with modern aesthetics"""
    
    # Common Colors (work well in both light and dark modes)
    ACCENT_COLOR = "#ff6b6b"
    ACCENT_HOVER = "#ff5252"
    SECONDARY_COLOR = "#4599DE"
    SECONDARY_HOVER = "#339af0"
    SUCCESS_COLOR = "#51cf66"
    WARNING_COLOR = "#a3850e"
    GRADIENT_START = "#667eea"
    GRADIENT_END = "#764ba2"
    
    # Dynamic colors that adapt to light/dark mode
    # CustomTkinter color tokens: https://customtkinter.tomschimansky.com/documentation/color
    BG_COLOR = ("gray95", "gray14")  # (light_mode, dark_mode)
    CARD_COLOR = ("gray98", "gray17")
    CARD_HOVER = ("gray92", "gray20")
    INFO_CARD_BG = ("gray96", "gray16")
    INPUT_BG = ("gray90", "gray20")
    INPUT_TEXT = ("gray10", "gray90")
    INPUT_BORDER = ("gray75", "gray30")
    DIVIDER = ("gray80", "gray25")
    TEXT_COLOR = ("gray10", "gray90")
    TEXT_SECONDARY = ("gray30", "gray70")
    MUTED_COLOR = ("gray50", "gray50")
    SHADOW_COLOR = ("gray85", "gray10")
    
    # Fonts
    TITLE_FONT = ("Segoe UI", 32, "bold")
    PRO_LABEL_FONT = ("Segoe UI", 13, "bold")
    SECTION_LABEL_FONT = ("Segoe UI", 13, "bold")
    NORMAL_FONT = ("Segoe UI", 13)
    SMALL_FONT = ("Segoe UI", 12)
    TINY_FONT = ("Segoe UI", 11)
    BUTTON_FONT = ("Segoe UI", 13, "bold")
    
    # Spacing and Sizing
    BORDER_RADIUS = 14
    BUTTON_RADIUS = 12
    INPUT_RADIUS = 12
    CARD_PADDING = 24
    ELEMENT_SPACING = 16
    
    # Animation Durations (ms)
    TRANSITION_FAST = 150
    TRANSITION_NORMAL = 250
    TRANSITION_SLOW = 350
    
    @staticmethod
    def configureStyles():
        """Configure CustomTkinter with enhanced appearance"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    @staticmethod
    def setTheme(theme: str):
        """Set the application theme (dark/light)"""
        ctk.set_appearance_mode(theme)
        
    @staticmethod
    def applyHoverEffect(widget, enter_color, leave_color):
        """Apply smooth hover effect to any widget"""
        def on_enter(e):
            widget.configure(fg_color=enter_color)
        
        def on_leave(e):
            widget.configure(fg_color=leave_color)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)