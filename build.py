"""
Build script for creating executable with assets
"""

import PyInstaller.__main__
import shutil
from pathlib import Path
import customtkinter
import yt_dlp.extractor
from yt_dlp.extractor import _ALL_CLASSES
import plyer.platforms.win.notification

# Clean previous builds
for dir in ['build', 'dist']:
    if Path(dir).exists():
        shutil.rmtree(dir)

# Get the path to customtkinter's internal assets
ctk_assets_path = Path(customtkinter.__file__).parent / "assets"

# Generate hooks for yt_dlp extractors 
# yt_dlp dynamically loads all these, so PyInstaller misses them.
yt_dlp_hooks = [f'--hidden-import=yt_dlp.extractor.{ie.IE_NAME}' for ie in _ALL_CLASSES]
print(f"Found {len(yt_dlp_hooks)} yt_dlp extractors.")

# Generate hooks for plyer backends 
# plyer dynamically loads platform-specific backends.
plyer_hooks = [
    '--hidden-import=plyer.platforms.win.notification'
]
print("Added plyer Windows backend.")

# Build with assets
buildCommand = [
    'main.py',
    '--name=VideoDownloaderPro',
    '--onefile',
    '--windowed',
    '--icon=assets/images/icon.ico',
    '--add-data=assets;assets',
    f'--add-data={ctk_assets_path};customtkinter/assets',
    '--clean',
]

buildCommand.extend(yt_dlp_hooks)
buildCommand.extend(plyer_hooks)

print("\n--- Running PyInstaller ---")
PyInstaller.__main__.run(buildCommand)
print("---------------------------\n")

print("✅ Build complete! Executable in dist/ folder")