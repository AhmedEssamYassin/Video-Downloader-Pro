"""
Build script for creating executable with assets
"""

import PyInstaller.__main__
import shutil
from pathlib import Path
import customtkinter

# Clean previous builds
for dir in ['build', 'dist']:
    if Path(dir).exists():
        shutil.rmtree(dir)

# Get the path to customtkinter's internal assets
ctk_assets_path = Path(customtkinter.__file__).parent / "assets"

# Build with assets
PyInstaller.__main__.run([
    'main.py',
    '--name=VideoDownloaderPro',
    '--onefile',
    '--windowed',
    '--icon=assets/images/icon.ico',
    '--add-data=assets;assets',
    f'--add-data={ctk_assets_path};customtkinter/assets',
    '--clean',
])

print("✅ Build complete! Executable in dist/ folder")