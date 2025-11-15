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
    import yt_dlp
except ImportError:
    print("ERROR: yt_dlp not found. Install it with: pip install yt-dlp")
    sys.exit(1)

# Clean previous builds
for dirName in ['build', 'dist']:
    if Path(dirName).exists():
        print(f"Cleaning {dirName}...")
        shutil.rmtree(dirName)

# Get the path to customtkinter's internal assets
ctkAssetsPath = Path(customtkinter.__file__).parent / "assets"
print(f"CustomTkinter assets path: {ctkAssetsPath}")

# Check if icon exists
iconPath = Path("assets/images/icon.ico")
if not iconPath.exists():
    print(f"WARNING: Icon not found at {iconPath}. Build will continue without icon.")
    iconArg = []
else:
    iconArg = [f'--icon={iconPath}']
    print(f"Using icon: {iconPath}")

# Generate hooks for yt_dlp extractors 
# yt_dlp dynamically loads all these, so PyInstaller misses them.
ytDlpHooks = []
try:
    # Updated approach: collect all extractor modules
    from yt_dlp.extractor import extractors
    
    # Get all extractor names from the lazy_extractors or gen_extractors
    extractorNames = []
    try:
        # Try to import the list of extractors
        from yt_dlp.extractor.extractors import _ALL_CLASSES
        extractorNames = [ie.IE_NAME for ie in _ALL_CLASSES if hasattr(ie, 'IE_NAME')]
    except (ImportError, AttributeError):
        # Fallback: use a broader hidden-import approach
        print("Using fallback method for yt_dlp extractors")
        ytDlpHooks = [
            '--hidden-import=yt_dlp.extractor.extractors',
            '--hidden-import=yt_dlp.extractor.common',
            '--hidden-import=yt_dlp.extractor.generic',
        ]
    
    if extractorNames:
        ytDlpHooks = [f'--hidden-import=yt_dlp.extractor.{name}' for name in extractorNames]
        print(f"Found {len(ytDlpHooks)} yt_dlp extractors.")
    elif not ytDlpHooks:
        # Final fallback
        ytDlpHooks = ['--hidden-import=yt_dlp.extractor']
        print("Using generic yt_dlp extractor import")
        
except Exception as e:
    print(f"WARNING: Could not generate yt_dlp hooks: {e}")
    # Fallback to basic imports
    ytDlpHooks = [
        '--hidden-import=yt_dlp.extractor',
        '--hidden-import=yt_dlp.extractor.common',
        '--hidden-import=yt_dlp.extractor.generic',
    ]

# Generate hooks for plyer backends (optional - for notifications)
plyerHooks = []
try:
    import plyer.platforms.win.notification
    plyerHooks = ['--hidden-import=plyer.platforms.win.notification']
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
    f'--add-data={ctkAssetsPath};customtkinter/assets',
    '--collect-all=yt_dlp',  # This ensures all yt_dlp modules are included
    '--clean',
    '--noconfirm',
]

# Add icon if it exists
buildCommand.extend(iconArg)

# Add hooks
buildCommand.extend(ytDlpHooks)
buildCommand.extend(plyerHooks)

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