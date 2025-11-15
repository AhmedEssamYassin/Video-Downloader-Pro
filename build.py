"""
Build script for creating executable with assets
"""

import PyInstaller.__main__
import shutil
from pathlib import Path

# Clean previous builds
for dir in ['build', 'dist']:
    if Path(dir).exists():
        shutil.rmtree(dir)

# Build with assets
PyInstaller.__main__.run([
    'main.py',
    '--name=VideoDownloaderPro',
    '--onefile',
    '--windowed',
    '--icon=assets/images/icon.ico',
    '--add-data=assets;assets',
    '--clean',
])

print("✅ Build complete! Executable in dist/ folder")