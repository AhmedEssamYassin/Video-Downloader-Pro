"""
Custom message boxes with modern styling matching the app theme
"""

import customtkinter as ctk
from .theme import Theme


class CustomMessageBox:
    """Custom message box dialogs with modern styling"""
    
    @staticmethod
    def showInfo(parent, title, message):
        """Show information dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="ℹ️",
            buttons=[("OK", True)],
            defaultButton=0
        )
    
    @staticmethod
    def showWarning(parent, title, message):
        """Show warning dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="⚠️",
            buttons=[("OK", True)],
            defaultButton=0,
            iconColor=Theme.WARNING_COLOR
        )
    
    @staticmethod
    def showError(parent, title, message):
        """Show error dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="❌",
            buttons=[("OK", True)],
            defaultButton=0,
            iconColor=Theme.ACCENT_COLOR
        )
    
    @staticmethod
    def askYesNo(parent, title, message):
        """Show yes/no confirmation dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="❓",
            buttons=[("Yes", True), ("No", False)],
            defaultButton=0
        )
    
    @staticmethod
    def askOkCancel(parent, title, message):
        """Show OK/Cancel dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="❓",
            buttons=[("OK", True), ("Cancel", False)],
            defaultButton=0
        )
    
    @staticmethod
    def askYesNoCancel(parent, title, message):
        """Show Yes/No/Cancel dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="❓",
            buttons=[("Yes", True), ("No", False), ("Cancel", None)],
            defaultButton=0
        )
    @staticmethod
    def askRetryCancel(parent, title, message):
        """Show Retry/Cancel dialog"""
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon="🔄",
            buttons=[("Retry", True), ("Cancel", False)],
            defaultButton=1
        )

    @staticmethod
    def showCustom(parent, title, message, icon="ℹ️", buttons=None):
        """Show custom dialog with specified buttons"""
        if buttons is None:
            buttons = [("OK", True)]
        
        return CustomMessageBox._showDialog(
            parent=parent,
            title=title,
            message=message,
            icon=icon,
            buttons=buttons,
            defaultButton=0
        )

    @staticmethod
    def _showDialog(parent, title, message, icon, buttons, defaultButton=0, iconColor=None):
        """Internal method to create and show dialog"""
        
        # Create dialog
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        
        # Calculate size based on message length
        messageLines = message.count('\n') + 1
        messageLength = max(len(line) for line in message.split('\n'))
        
        # Dynamic sizing
        width = min(max(400, messageLength * 8), 600)
        height = min(max(200, 120 + messageLines * 25 + len(buttons) * 20), 400)
        
        dialog.geometry(f"{width}x{height}")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog on parent window
        dialog.update_idletasks()
        if parent.winfo_exists():
            x = parent.winfo_x() + (parent.winfo_width() - width) // 2
            y = parent.winfo_y() + (parent.winfo_height() - height) // 2
            dialog.geometry(f"+{x}+{y}")
        
        # Configure dialog
        dialog.configure(fg_color=Theme.CARD_COLOR)
        
        # Content frame
        contentFrame = ctk.CTkFrame(dialog, fg_color="transparent")
        contentFrame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon
        iconLabel = ctk.CTkLabel(
            contentFrame,
            text=icon,
            font=("Segoe UI", 36),
            text_color=iconColor if iconColor else Theme.TEXT_COLOR
        )
        iconLabel.pack(pady=(0, 10))
        
        # Message
        messageLabel = ctk.CTkLabel(
            contentFrame,
            text=message,
            font=("Segoe UI", 14),
            text_color=Theme.TEXT_COLOR,
            justify="center",
            wraplength=width - 80
        )
        messageLabel.pack(pady=(0, 20))
        
        # Store result
        result = [None]
        
        def makeCallback(value):
            def callback():
                result[0] = value
                dialog.destroy()
            return callback
        
        # Button frame
        buttonFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        buttonFrame.pack()
        
        # Create buttons
        buttonWidgets = []
        for i, (buttonText, buttonValue) in enumerate(buttons):
            # Determine button colors based on action type
            if buttonValue is True and buttonText in ["Yes", "OK", "Clear All"]:
                # Affirmative/destructive action
                if "Clear" in buttonText or "Delete" in buttonText or "Remove" in buttonText:
                    bgColor = Theme.ACCENT_COLOR
                    hoverColor = Theme.ACCENT_HOVER
                else:
                    bgColor = Theme.SECONDARY_COLOR
                    hoverColor = Theme.SECONDARY_HOVER
            elif buttonValue is False or buttonValue is None:
                # Negative/safe action
                bgColor = "#6c757d"
                hoverColor = "#5c636a"
            else:
                bgColor = Theme.SECONDARY_COLOR
                hoverColor = Theme.SECONDARY_HOVER
            
            btn = ctk.CTkButton(
                buttonFrame,
                text=buttonText,
                command=makeCallback(buttonValue),
                fg_color=bgColor,
                hover_color=hoverColor,
                width=130,
                height=44,
                corner_radius=10,
                font=("Segoe UI", 13, "bold")
            )
            btn.pack(side="left", padx=5)
            buttonWidgets.append(btn)
        
        # Bind keyboard shortcuts
        dialog.bind('<Escape>', lambda e: makeCallback(buttons[defaultButton][1])())
        dialog.bind('<Return>', lambda e: makeCallback(buttons[-1][1])())
        
        # Focus on default button
        if buttonWidgets:
            buttonWidgets[defaultButton].focus_set()
        
        # Wait for dialog to close
        parent.wait_window(dialog)
        
        # Return result
        return result[0]


# Convenience functions for backward compatibility
def showInfo(parent, title, message):
    """Show information dialog"""
    return CustomMessageBox.showInfo(parent, title, message)


def showWarning(parent, title, message):
    """Show warning dialog"""
    return CustomMessageBox.showWarning(parent, title, message)


def showError(parent, title, message):
    """Show error dialog"""
    return CustomMessageBox.showError(parent, title, message)


def askYesNo(parent, title, message):
    """Show yes/no confirmation dialog"""
    return CustomMessageBox.askYesNo(parent, title, message)


def askOkCancel(parent, title, message):
    """Show OK/Cancel dialog"""
    return CustomMessageBox.askOkCancel(parent, title, message)