"""
Custom message boxes with modern styling
Uses ttkbootstrap's Messagebox for consistent theming
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from .theme import Theme


class CustomMessageBox:
    """Custom message box dialogs with modern styling"""
    
    @staticmethod
    def showInfo(parent, title, message):
        """Show information dialog"""
        return Messagebox.ok(
            message=message,
            title=title,
            parent=parent,
            alert=False
        )
    
    @staticmethod
    def showWarning(parent, title, message):
        """Show warning dialog"""
        return Messagebox.show_warning(
            message=message,
            title=title,
            parent=parent,
            alert=True
        )
    
    @staticmethod
    def showError(parent, title, message):
        """Show error dialog"""
        return Messagebox.show_error(
            message=message,
            title=title,
            parent=parent,
            alert=True
        )
    
    @staticmethod
    def askYesNo(parent, title, message):
        """Show yes/no confirmation dialog"""
        result = Messagebox.yesno(
            message=message,
            title=title,
            parent=parent,
            alert=False
        )
        return result == "Yes"
    
    @staticmethod
    def askOkCancel(parent, title, message):
        """Show OK/Cancel dialog"""
        result = Messagebox.okcancel(
            message=message,
            title=title,
            parent=parent,
            alert=False
        )
        return result == "OK"
    
    @staticmethod
    def askYesNoCancel(parent, title, message):
        """Show Yes/No/Cancel dialog"""
        result = Messagebox.show_question(
            message=message,
            title=title,
            parent=parent,
            buttons=["Yes:primary", "No:secondary", "Cancel:secondary"],
            alert=False
        )
        if result == "Yes":
            return True
        elif result == "No":
            return False
        else:
            return None
    
    @staticmethod
    def askRetryCancel(parent, title, message):
        """Show Retry/Cancel dialog"""
        result = Messagebox.retrycancel(
            message=message,
            title=title,
            parent=parent,
            alert=False
        )
        return result == "Retry"
    
    @staticmethod
    def showCustom(parent, title, message, icon="ℹ️", buttons=None):
        """Show custom dialog with specified buttons"""
        if buttons is None:
            buttons = ["OK:primary"]
        else:
            # Convert button tuples to ttkbootstrap format
            formatted_buttons = []
            for btn_text, btn_value in buttons:
                # Determine button style based on text
                if btn_value is True and btn_text in ["Yes", "OK"]:
                    formatted_buttons.append(f"{btn_text}:primary")
                elif btn_value is False:
                    formatted_buttons.append(f"{btn_text}:secondary")
                else:
                    formatted_buttons.append(f"{btn_text}:info")
            buttons = formatted_buttons
        
        return Messagebox.show_question(
            message=message,
            title=title,
            parent=parent,
            buttons=buttons,
            alert=False
        )


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
