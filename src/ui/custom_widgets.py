"""
Modern custom UI widgets using ttkbootstrap
Provides enhanced widgets with clean, flat design
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .theme import Theme


class ModernButton(ttk.Button):
    """Enhanced modern button with clean styling"""
    
    def __init__(self, parent, text, command, bgColor="#4dabf7", hoverColor="#339af0", 
                 textColor="white", width=200, height=48, icon=None):
        
        # Map background color to bootstyle
        bootstyle = self._getBootstyle(bgColor)
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bootstyle=bootstyle,
            width=int(width/8),  # ttkbootstrap uses character width
            cursor="hand2"
        )
        
        # Store original command and state
        self._command = command
        self._enabled = True
        
    def _getBootstyle(self, bgColor):
        """Map color to ttkbootstrap style"""
        if bgColor in [Theme.SECONDARY_COLOR, "#4dabf7"]:
            return PRIMARY
        elif bgColor in [Theme.ACCENT_COLOR, "#ff6b6b"]:
            return DANGER
        elif bgColor in [Theme.SUCCESS_COLOR, "#51cf66"]:
            return SUCCESS
        else:
            return INFO
    
    def setEnabled(self, enabled):
        """Enable or disable the button"""
        self._enabled = enabled
        if enabled:
            self.configure(state=NORMAL, cursor="hand2")
        else:
            self.configure(state=DISABLED, cursor="arrow")


class ModernEntry(ttk.Frame):
    """Enhanced modern entry with icon and clean design"""
    
    def __init__(self, parent, placeholder="", icon="🔗"):
        super().__init__(parent)
        
        # Configure frame background
        self.configure(bootstyle="secondary")
        
        # Icon label
        self.iconLabel = ttk.Label(
            self,
            text=icon,
            font=("Segoe UI", 16),
            foreground=Theme.TEXT_SECONDARY
        )
        self.iconLabel.pack(side=LEFT, padx=(12, 8))
        
        # Entry widget
        self.entry = ttk.Entry(
            self,
            font=Theme.NORMAL_FONT
        )
        self.entry.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12), pady=8)
        
        # Set placeholder
        self._placeholder = placeholder
        self._placeholderActive = False
        
        if placeholder:
            self._showPlaceholder()
            self.entry.bind("<FocusIn>", self._onFocusIn)
            self.entry.bind("<FocusOut>", self._onFocusOut)
    
    def _showPlaceholder(self):
        """Show placeholder text"""
        if not self.entry.get():
            self.entry.insert(0, self._placeholder)
            self.entry.configure(foreground=Theme.TEXT_SECONDARY)
            self._placeholderActive = True
    
    def _hidePlaceholder(self):
        """Hide placeholder text"""
        if self._placeholderActive:
            self.entry.delete(0, tk.END)
            self.entry.configure(foreground=Theme.INPUT_TEXT)
            self._placeholderActive = False
    
    def _onFocusIn(self, event):
        """Handle focus in"""
        self._hidePlaceholder()
    
    def _onFocusOut(self, event):
        """Handle focus out"""
        if not self.entry.get():
            self._showPlaceholder()
    
    def get(self):
        """Get entry value"""
        if self._placeholderActive:
            return ""
        return self.entry.get()
    
    def set(self, text):
        """Set entry value"""
        self._hidePlaceholder()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
    
    def delete(self, first, last=None):
        """Delete characters from the widget"""
        self._hidePlaceholder()
        self.entry.delete(first, last)
    
    def insert(self, index, string):
        """Insert a string at a given index"""
        self._hidePlaceholder()
        self.entry.insert(index, string)


class AnimatedProgressBar(ttk.Progressbar):
    """Enhanced progress bar with smooth animations"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            mode='determinate',
            bootstyle="info-striped",
            **kwargs
        )
        self._currentValue = 0
        self._targetValue = 0
        self._animating = False
    
    def animateTo(self, value):
        """Smoothly animate to target value (0.0 to 1.0)"""
        self._targetValue = value * 100  # Convert to percentage
        if not self._animating:
            self._animateStep()
    
    def _animateStep(self):
        """Single animation step"""
        if abs(self._currentValue - self._targetValue) < 1:
            self._currentValue = self._targetValue
            self.configure(value=self._currentValue)
            self._animating = False
            return
        
        self._animating = True
        # Smooth easing
        diff = self._targetValue - self._currentValue
        self._currentValue += diff * 0.2
        self.configure(value=self._currentValue)
        
        # Schedule next frame
        self.after(16, self._animateStep)  # ~60fps
    
    def set(self, value):
        """Set progress value directly (0.0 to 1.0)"""
        self._currentValue = value * 100
        self._targetValue = value * 100
        self.configure(value=self._currentValue)
    
    def start(self):
        """Start indeterminate mode"""
        self.configure(mode='indeterminate')
        super().start()
    
    def stop(self):
        """Stop indeterminate mode"""
        super().stop()
        self.configure(mode='determinate')


class InfoCard(ttk.Frame):
    """Modern info card with clean border"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bootstyle="secondary", relief=FLAT, borderwidth=1)


class CustomDropdown(ttk.Frame):
    """Custom dropdown using ttkbootstrap Combobox"""
    
    def __init__(self, parent, variable, values, **kwargs):
        super().__init__(parent)
        
        self.variable = variable
        self.values = values
        self.command = kwargs.get('command', None)
        
        # Create combobox
        self.combobox = ttk.Combobox(
            self,
            textvariable=variable,
            values=values,
            state="readonly",
            font=kwargs.get('font', Theme.SMALL_FONT),
            bootstyle=INFO
        )
        self.combobox.pack(fill=BOTH, expand=True, padx=0, pady=0)
        
        # Force hand cursor on hover - this is the key fix
        self.combobox.bind("<Enter>", lambda e: self.combobox.configure(cursor="hand2"))
        self.combobox.bind("<Leave>", lambda e: self.combobox.configure(cursor="hand2"))
        
        # Set initial cursor
        self.combobox.configure(cursor="hand2")
        
        # Also try to set cursor on children after widget is fully initialized
        self.after(200, self._forceHandCursor)
        
        # Bind selection event
        if self.command:
            self.combobox.bind('<<ComboboxSelected>>', lambda e: self.command(self.combobox.get()))
    
    def _forceHandCursor(self):
        """Force hand cursor on the combobox and all its children"""
        try:
            self.combobox.configure(cursor="hand2")
            # Try to access and configure internal widgets
            for child in self.combobox.winfo_children():
                try:
                    child.configure(cursor="hand2")
                    child.bind("<Enter>", lambda e: child.configure(cursor="hand2"))
                except:
                    pass
        except:
            pass
    
    def configure(self, **kwargs):
        """Configure the dropdown"""
        if 'values' in kwargs:
            self.values = kwargs['values']
            self.combobox.configure(values=self.values)
        if 'state' in kwargs:
            self.combobox.configure(state=kwargs['state'])
    
    def set(self, value):
        """Set the current value"""
        self.variable.set(value)
    
    def get(self):
        """Get the current value"""
        return self.variable.get()
