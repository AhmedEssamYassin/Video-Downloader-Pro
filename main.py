"""
YouTube Downloader Pro - Main Entry Point

Modern Multi-Platform Video Downloader with Fancy GUI
Supports: YouTube, Facebook, Instagram, TikTok (extensible to more platforms)
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

def setupGlobalFfmpeg():
    ffmpegExe = "ffmpeg.exe"
    ffmpegPath = None

    if getattr(sys, 'frozen', False):
        # Check ROOT of _MEIPASS (if added via --add-binary)
        path1 = os.path.join(sys._MEIPASS, ffmpegExe)
        # Check ASSETS folder inside _MEIPASS (if added via --add-data)
        path2 = os.path.join(sys._MEIPASS, "assets", ffmpegExe)

        if os.path.exists(path1):
            ffmpegPath = sys._MEIPASS
        elif os.path.exists(path2):
            ffmpegPath = os.path.dirname(path2)
    else:
        # Development mode
        possiblePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", ffmpegExe)
        if os.path.exists(possiblePath):
            ffmpegPath = os.path.dirname(possiblePath)

    if ffmpegPath:
        os.environ["PATH"] += os.pathsep + ffmpegPath

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
    setupGlobalFfmpeg()
    main()