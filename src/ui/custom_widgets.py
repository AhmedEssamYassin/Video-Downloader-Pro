"""
Enhanced custom UI widgets with smooth animations and modern design
"""

import customtkinter as ctk
from tkinter import font as tkfont
from .theme import Theme

class ModernButton(ctk.CTkButton):
    """Enhanced modern button with smooth hover effects and better styling"""
    
    def __init__(self, parent, text, command, bgColor="#4dabf7", hoverColor="#339af0", 
                 textColor=None, width=200, height=48, icon=None):
        
        if textColor is None:
            # If background is a theme color (tuple or named), use white
            # Otherwise, use white for colored buttons
            textColor = "white"

        # Enhanced styling with larger fonts
        super().__init__(
            parent, 
            text=text,
            command=command,
            fg_color=bgColor,
            hover_color=hoverColor,
            text_color=textColor,
            width=width,
            height=height,
            corner_radius=12,
            border_width=0,
            font=("Segoe UI", 13, "bold"),
            cursor="hand2"
        )
        
        # Add subtle shadow effect with a frame
        self._addElevation()
        
    def _addElevation(self):
        """Add subtle elevation effect"""
        # This creates a visual depth
        self.configure(border_spacing=6)
        
    def setEnabled(self, enabled):
        """Enable or disable the button with visual feedback"""
        if enabled:
            self.configure(state="normal", cursor="hand2")
        else:
            self.configure(state="disabled", cursor="arrow")


class ModernEntry(ctk.CTkFrame):
    """Enhanced modern entry with smooth focus effects and better aesthetics"""
    
    def __init__(self, parent, placeholder="", icon="🔗"):
        super().__init__(
            parent, 
            fg_color=Theme.INPUT_BG,
            corner_radius=12,
            border_width=2,
            border_color=Theme.INPUT_BORDER
        )
        
        # Container for icon and entry
        innerFrame = ctk.CTkFrame(self, fg_color="transparent")
        innerFrame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Icon with better styling
        self.iconLabel = ctk.CTkLabel(
            innerFrame, 
            text=icon, 
            font=("Segoe UI", 16),
            text_color=Theme.TEXT_SECONDARY,
            fg_color="transparent",
            width=35
        )
        self.iconLabel.pack(side="left", padx=(14, 10))
        
        # Entry with enhanced styling
        self.entry = ctk.CTkEntry(
            innerFrame, 
            placeholder_text=placeholder,
            font=("Segoe UI", 13),
            fg_color="transparent",
            border_width=0,
            text_color=Theme.INPUT_TEXT,
            placeholder_text_color=Theme.TEXT_SECONDARY
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 14))
        self.entry.configure(takefocus=True)
        self.configure(height=52)
        
        # Add focus effects
        self._addFocusEffects()
        
    def _addFocusEffects(self):
        """Add smooth focus and blur effects"""
        def onFocusIn(e):
            self.configure(border_color="#4dabf7")
            
        def onFocusOut(e):
            self.configure(border_color=Theme.INPUT_BORDER)
        
        self.entry.bind("<FocusIn>", onFocusIn)
        self.entry.bind("<FocusOut>", onFocusOut)
    
    def get(self):
        """Get entry value"""
        return self.entry.get()
    
    def set(self, text):
        """Set entry value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        
    def delete(self, first, last=None):
        """Deletes characters from the widget"""
        self.entry.delete(first, last)

    def insert(self, index, string):
        """Inserts a string at a given index"""
        self.entry.insert(index, string)


class AnimatedProgressBar(ctk.CTkProgressBar):
    """Enhanced progress bar with smooth animations"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            mode='determinate',
            progress_color="#4dabf7",
            fg_color=Theme.INPUT_BG,
            height=10,
            corner_radius=5,
            border_width=0,
            **kwargs
        )
        self._currentValue = 0
        self._targetValue = 0
        self._animating = False
        
    def animateTo(self, value):
        """Smoothly animate to target value"""
        self._targetValue = value
        if not self._animating:
            self._animateStep()
    
    def _animateStep(self):
        """Single animation step"""
        if abs(self._currentValue - self._targetValue) < 0.01:
            self._currentValue = self._targetValue
            self.set(self._currentValue)
            self._animating = False
            return
        
        self._animating = True
        # Smooth easing
        diff = self._targetValue - self._currentValue
        self._currentValue += diff * 0.2
        self.set(self._currentValue)
        
        # Schedule next frame
        self.after(16, self._animateStep)  # ~60fps


class InfoCard(ctk.CTkFrame):
    """Modern info card with gradient border effect"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Theme.INFO_CARD_BG,
            corner_radius=14,
            border_width=2,
            border_color=Theme.INPUT_BORDER,
            **kwargs
        )
        
        # Add subtle glow effect on hover
        self.bind("<Enter>", self._onEnter)
        self.bind("<Leave>", self._onLeave)
        
    def _onEnter(self, e):
        """Hover effect"""
        self.configure(border_color="#4dabf7")
        
    def _onLeave(self, e):
        """Leave effect"""
        self.configure(border_color=Theme.INPUT_BORDER)

class CustomDropdown(ctk.CTkFrame):
    """Custom dropdown menu with chevron indicator and clean design"""
    
    def __init__(self, parent, variable, values, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.variable = variable
        self.values = values
        self.command = kwargs.get('command', None)
        
        # Extract styling parameters
        self.fg_color = kwargs.get('fg_color', Theme.INPUT_BG)
        self.text_color = kwargs.get('text_color', Theme.TEXT_COLOR)
        self.hover_color = kwargs.get('hover_color', Theme.CARD_HOVER)
        self.font = kwargs.get('font', Theme.SMALL_FONT)
        self.height = kwargs.get('height', 48)
        self.corner_radius = kwargs.get('corner_radius', 12)
        
        # Main container with border
        self.container = ctk.CTkFrame(
            self,
            fg_color=self.fg_color,
            corner_radius=self.corner_radius,
            border_width=0,
            border_color=Theme.INPUT_BORDER
        )
        self.container.pack(fill="both", expand=True)
        
        # Create clickable button
        self.mainBtn = ctk.CTkButton(
            self.container,
            textvariable=self.variable,
            command=self._toggleDropdown,
            fg_color="transparent",
            hover_color=self.hover_color,
            text_color=self.text_color,
            font=self.font,
            height=self.height - 4,
            corner_radius=self.corner_radius,
            anchor="w",
            border_width=0
        )
        self.mainBtn.pack(side="left", fill="both", expand=True, padx=12)
        
        # Modern dropdown indicator (arrow down)
        self.indicator = ctk.CTkLabel(
            self.container,
            text="⮟",
            font=("Segoe UI", 16),
            text_color=self.text_color,
            width=20,
            cursor="hand2"
        )
        self.indicator.pack(side="right", padx=(4, 12))

        # Make indicator clickable too
        self.indicator.bind("<Button-1>", lambda e: self._toggleDropdown())

        # Dropdown menu (initially hidden)
        self.dropdownMenu = None
        self.isOpen = False
        self.clickOutsideBindId = None
    
    def _toggleDropdown(self):
        """Toggle dropdown menu visibility"""
        if self.isOpen:
            self._closeDropdown()
        else:
            self._openDropdown()
    
    def _openDropdown(self):
        """Open the dropdown menu"""
        if self.dropdownMenu:
            return
        
        self.isOpen = True
        self.indicator.configure(text="⮝")  # Arrow up when open
        
        # Create dropdown as toplevel window
        self.dropdownMenu = ctk.CTkToplevel(self)
        self.dropdownMenu.withdraw()  # Hide initially
        self.dropdownMenu.overrideredirect(True)  # Remove window decorations

        # Make it a child of the main window
        mainWindow = self.winfo_toplevel()
        self.dropdownMenu.transient(mainWindow)

        # Bind to window movement/minimize
        mainWindow.bind("<Configure>", self._onWindowMove, add="+")
        mainWindow.bind("<Unmap>", self._onWindowMinimize, add="+")
        
        # Configure dropdown with border
        outerFrame = ctk.CTkFrame(
            self.dropdownMenu,
            fg_color=Theme.INPUT_BORDER,
            corner_radius=self.corner_radius
        )
        outerFrame.pack(fill="both", expand=True)
        
        innerFrame = ctk.CTkFrame(
            outerFrame,
            fg_color=Theme.CARD_COLOR,
            corner_radius=self.corner_radius
        )
        innerFrame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Create scrollable frame for options
        scrollFrame = ctk.CTkScrollableFrame(
            innerFrame,
            fg_color=Theme.CARD_COLOR,
            scrollbar_button_color=Theme.SECONDARY_COLOR,
            scrollbar_button_hover_color=Theme.SECONDARY_HOVER,
            corner_radius=self.corner_radius - 2
        )
        scrollFrame.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Add options
        for value in self.values:
            isSelected = (value == self.variable.get())
            
            btn = ctk.CTkButton(
                scrollFrame,
                text=value,
                command=lambda v=value: self._selectValue(v),
                fg_color=Theme.SECONDARY_COLOR if isSelected else "transparent",
                hover_color=Theme.SECONDARY_HOVER,
                text_color="white" if isSelected else self.text_color,
                font=self.font,
                height=40,
                corner_radius=8,
                anchor="w"
            )
            btn.pack(fill="x", padx=2, pady=2)
        
        # Update to get correct positions
        self.update_idletasks()
        self.dropdownMenu.update_idletasks()
        
        # Calculate position
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        width = self.winfo_width()
        
        # Calculate height (max 6 items visible)
        itemHeight = 44  # 40 height + 4 padding
        maxHeight = min(len(self.values) * itemHeight + 16, 6 * itemHeight + 16)
        
        self.dropdownMenu.geometry(f"{width}x{maxHeight}+{x}+{y}")
        self.dropdownMenu.deiconify()  # Show window
        self.dropdownMenu.lift()
        self.dropdownMenu.focus_force()  # Force focus
        
        # Bind events to close dropdown - delayed to prevent immediate close
        self.dropdownMenu.bind("<Escape>", lambda e: self._closeDropdown())

        # Use a delayed focus check instead of immediate FocusOut
        self.after(100, self._setupFocusCheck)

        # Bind click detection with delay to avoid closing immediately
        self.after(150, self._bindClickOutside)
        
    def _setupFocusCheck(self):
        """Setup focus checking after dropdown is fully opened"""
        if self.dropdownMenu and self.isOpen:
            self.dropdownMenu.bind("<FocusOut>", self._onFocusOut)

    def _bindClickOutside(self):
        """Bind click outside detection"""
        if self.dropdownMenu and self.isOpen:
            self.clickOutsideBindId = self.winfo_toplevel().bind("<Button-1>", self._onClickOutside, add="+")

    def _onClickOutside(self, event):
        """Handle clicks outside dropdown"""
        if not self.dropdownMenu or not self.isOpen:
            return
        
        try:
            # Get click coordinates
            x, y = event.x_root, event.y_root
            
            # Get dropdown window bounds
            dropX = self.dropdownMenu.winfo_rootx()
            dropY = self.dropdownMenu.winfo_rooty()
            dropW = self.dropdownMenu.winfo_width()
            dropH = self.dropdownMenu.winfo_height()
            
            # Get main widget bounds
            mainX = self.winfo_rootx()
            mainY = self.winfo_rooty()
            mainW = self.winfo_width()
            mainH = self.winfo_height()
            
            # Check if click is outside both dropdown and main widget
            outsideDropdown = not (dropX <= x <= dropX + dropW and dropY <= y <= dropY + dropH)
            outsideMain = not (mainX <= x <= mainX + mainW and mainY <= y <= mainY + mainH)
            
            if outsideDropdown and outsideMain:
                self._closeDropdown()
        except:
            pass

    def _onWindowMove(self, event):
        """Handle main window movement"""
        if self.dropdownMenu and self.isOpen:
            # Update dropdown position
            try:
                x = self.winfo_rootx()
                y = self.winfo_rooty() + self.winfo_height() + 4
                width = self.winfo_width()
                currentGeometry = self.dropdownMenu.geometry()
                height = currentGeometry.split('x')[1].split('+')[0]
                self.dropdownMenu.geometry(f"{width}x{height}+{x}+{y}")
            except:
                self._closeDropdown()

    def _onWindowMinimize(self, event):
        """Handle main window minimize/hide"""
        if self.dropdownMenu and self.isOpen:
            self._closeDropdown()

    def _onFocusOut(self, event):
        """Handle focus out with validation"""
        if not self.dropdownMenu or not self.isOpen:
            return
        
        # Check if focus went to a child of dropdown
        try:
            focusWidget = self.focus_get()
            if focusWidget:
                parent = focusWidget
                while parent:
                    if parent == self.dropdownMenu:
                        return  # Focus is still in dropdown
                    try:
                        parent = parent.master
                    except:
                        break
        except:
            pass
        
        # Focus truly left, close dropdown
        self._closeDropdown()

    def _closeDropdown(self):
        """Close the dropdown menu"""
        if self.dropdownMenu:
            # Unbind window events
            try:
                mainWindow = self.winfo_toplevel()
                mainWindow.unbind("<Configure>", self._onWindowMove)
                mainWindow.unbind("<Unmap>", self._onWindowMinimize)
                if self.clickOutsideBindId:
                    mainWindow.unbind("<Button-1>", self.clickOutsideBindId)
                    self.clickOutsideBindId = None
            except:
                pass
            
            self.dropdownMenu.destroy()
            self.dropdownMenu = None
        self.isOpen = False
        self.indicator.configure(text="⮟")  # Reset to arrow down
    
    def _selectValue(self, value):
        """Select a value from dropdown"""
        self.variable.set(value)
        self._closeDropdown()
        
        # Call command if provided
        if self.command:
            self.command(value)
    
    def configure(self, **kwargs):
        """Configure the dropdown"""
        if 'values' in kwargs:
            self.values = kwargs['values']
        if 'state' in kwargs:
            state = kwargs['state']
            self.mainBtn.configure(state=state)
            if state == 'disabled':
                self.indicator.configure(text_color=Theme.MUTED_COLOR)
            else:
                self.indicator.configure(text_color=self.text_color)
    
    def set(self, value):
        """Set the current value"""
        self.variable.set(value)
    
    def get(self):
        """Get the current value"""
        return self.variable.get()