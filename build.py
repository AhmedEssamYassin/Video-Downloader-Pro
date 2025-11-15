"""
Build script for creating executable with assets
"""

import sys
import shutil
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    print("ERROR: PyInstaller not found. Install it with: pip install pyinstaller")
    sys.exit(1)

try:
    import customtkinter
except ImportError:
    print("ERROR: customtkinter not found. Install it with: pip install customtkinter")
    sys.exit(1)

try:
    import yt_dlp.extractor
    from yt_dlp.extractor import _ALL_CLASSES
except ImportError:
    print("ERROR: yt_dlp not found. Install it with: pip install yt-dlp")
    sys.exit(1)

# Clean previous builds
for dir in ['build', 'dist']:
    if Path(dir).exists():
        print(f"Cleaning {dir}...")
        shutil.rmtree(dir)

# Get the path to customtkinter's internal assets
ctk_assets_path = Path(customtkinter.__file__).parent / "assets"
print(f"CustomTkinter assets path: {ctk_assets_path}")

# Check if icon exists
icon_path = Path("assets/images/icon.ico")
if not icon_path.exists():
    print(f"WARNING: Icon not found at {icon_path}. Build will continue without icon.")
    icon_arg = []
else:
    icon_arg = [f'--icon={icon_path}']
    print(f"Using icon: {icon_path}")

# Generate hooks for yt_dlp extractors 
# yt_dlp dynamically loads all these, so PyInstaller misses them.
yt_dlp_hooks = []
try:
    yt_dlp_hooks = [f'--hidden-import=yt_dlp.extractor.{ie.IE_NAME}' for ie in _ALL_CLASSES]
    print(f"Found {len(yt_dlp_hooks)} yt_dlp extractors.")
except Exception as e:
    print(f"WARNING: Could not generate yt_dlp hooks: {e}")

# Generate hooks for plyer backends (optional - for notifications)
plyer_hooks = []
try:
    import plyer.platforms.win.notification
    plyer_hooks = ['--hidden-import=plyer.platforms.win.notification']
    print("Added plyer Windows backend.")
except ImportError:
    print("WARNING: plyer not found. Notifications may not work.")

# Build with assets
buildCommand = [
    'main.py',
    '--name=VideoDownloaderPro',
    '--onefile',
    '--windowed',
    '--add-data=assets;assets',
    f'--add-data={ctk_assets_path};customtkinter/assets',
    '--clean',
    '--noconfirm',
]

# Add icon if it exists
buildCommand.extend(icon_arg)

# Add hooks
buildCommand.extend(yt_dlp_hooks)
buildCommand.extend(plyer_hooks)

print("\n" + "="*50)
print("Running PyInstaller with command:")
print(" ".join(buildCommand[:10]) + "...")
print("="*50 + "\n")

try:
    PyInstaller.__main__.run(buildCommand)
    print("\n" + "="*50)
    print("✅ Build complete! Executable in dist/ folder")
    print("="*50)
except Exception as e:
    print(f"\n❌ Build failed: {e}")
    sys.exit(1)