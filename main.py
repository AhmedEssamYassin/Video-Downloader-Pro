"""
YouTube Downloader Pro - Main Entry Point

Modern Multi-Platform Video Downloader with Fancy GUI
Supports: YouTube, Facebook (extensible to more platforms)
Requires: pip install yt-dlp

Project Structure:
- main.py: Application entry point
- gui.py: Main GUI application
- controller.py: Business logic controller
- download_manager.py: Download operations facade
- base_downloader.py: Abstract base class for downloaders
- youtube_downloader.py: YouTube implementation
- facebook_downloader.py: Facebook implementation
- downloader_factory.py: Factory for creating downloaders
- models.py: Data models
- custom_widgets.py: Custom UI components
- theme.py: UI theme configuration
"""

import sys
import os
import customtkinter as ctk
from tkinter import messagebox

def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

from src.ui.gui import VideoDownloaderGUI

def main():
    """Application entry point"""
    # Create the main window using CustomTkinter
    root = ctk.CTk()

    # Set the window icon
    try:
        iconPath = resourcePath("assets/images/icon.ico")
        root.iconbitmap(iconPath)
    except ctk.TclError:
        print("Icon not found, skipping.")
    
    # Initialize the GUI
    app = VideoDownloaderGUI(root)

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()