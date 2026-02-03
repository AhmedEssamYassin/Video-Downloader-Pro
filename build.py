import PyInstaller.__main__
import os
import shutil
import json
import sys
from pathlib import Path
import update_deps

try:
    import customtkinter
    import yt_dlp
    from yt_dlp.extractor import extractors
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Please install: pip install customtkinter yt-dlp")
    sys.exit(1)

update_deps.updateAllDeps()    

def getProjectVersion():
    try:
        config_path = PROJECT_ROOT / "assets" / "data" / "default_config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("version", "2.0.0")
    except Exception:
        return "2.0.0"

# --- Project Configuration ---
APP_NAME = "VideoDownloaderPro"
VERSION_NUMBER = getProjectVersion()
AUTHOR_NAME = "Ahmed Yassin"
APP_DESCRIPTION = "Professional Video Downloader"

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Logic to find dynamic asset paths
CTK_PATH = Path(customtkinter.__file__).parent / "assets"

# --- Helper Functions ---

def getYtDlpExtractors():
    """Dynamically find yt-dlp extractors to avoid missing module errors"""
    try:
        from yt_dlp.extractor.extractors import _ALL_CLASSES
        extractorNames = [f"yt_dlp.extractor.{ie.IE_NAME}" for ie in _ALL_CLASSES if hasattr(ie, 'IE_NAME')]
        return extractorNames
    except Exception:
        return ['yt_dlp.extractor', 'yt_dlp.extractor.common', 'yt_dlp.extractor.generic']

def getPlyerHooks():
    """Check for plyer windows notification support"""
    try:
        import plyer.platforms.win.notification
        return ['plyer.platforms.win.notification']
    except ImportError:
        return []

def cleanBuildDirs():
    """Clean previous build directories"""
    print("Cleaning previous builds...")
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
    # Clean spec file
    specFile = PROJECT_ROOT / f"{APP_NAME}.spec"
    if specFile.exists():
        specFile.unlink() # Deletes the file
        print(f"Deleted spec file: {APP_NAME}.spec")

    print("Build directories cleaned")

# --- Build Logic ---

def createSpecFile():
    """Create PyInstaller spec file with dynamic yt-dlp hooks"""
    ytHooks = getYtDlpExtractors()
    plyerHooks = getPlyerHooks()
    
    hiddenImports = [
        'PIL._tkinter_finder',
        'customtkinter',
        'yt_dlp',
        'requests',
        'packaging',
        'certifi',   
        'brotli',    
        'mutagen',
    ] + ytHooks + plyerHooks

    specContent = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (r'{CTK_PATH}', 'customtkinter/assets'),
    ],
    hiddenimports={hiddenImports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/icon.ico' if os.path.exists('assets/images/icon.ico') else None,
)
'''
    specFile = PROJECT_ROOT / f"{APP_NAME}.spec"
    with open(specFile, 'w', encoding='utf-8') as f:
        f.write(specContent)
    
    print(f"Created spec file: {specFile}")
    return specFile

def getBaseArgs():
    """Common arguments for OneFile and OneDir"""
    ytHooks = getYtDlpExtractors()
    plyerHooks = getPlyerHooks()
    
    args = [
        'main.py',
        '--name', APP_NAME,
        '--windowed',
        '--clean',
        '--noconfirm',
        f'--distpath={DIST_DIR}',
        f'--workpath={BUILD_DIR}',
        '--add-data', f'assets{os.pathsep}assets',
        '--add-data', f'{CTK_PATH}{os.pathsep}customtkinter/assets',
        '--collect-all', 'yt_dlp',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'requests',
        '--hidden-import', 'packaging',
        '--hidden-import', 'certifi',  
        '--hidden-import', 'brotli',   
        '--hidden-import', 'mutagen',  
    ]

    for hook in (ytHooks + plyerHooks):
        args.extend(['--hidden-import', hook])

    ffmpegPath = ASSETS_DIR / "ffmpeg.exe"
    if ffmpegPath.exists():
        print(f"Bundling FFmpeg from: {ffmpegPath}")
        # Syntax is "source;dest" (Windows)
        args.append(f'--add-binary={ffmpegPath};.') 
    else:
        print("WARNING: FFmpeg not found in assets. High-quality merges won't work.")

    iconPath = ASSETS_DIR / "images" / "icon.ico"
    if iconPath.exists():
        args.extend(['--icon', str(iconPath)])
    
    return args

def buildOnefile():
    """Build as single file executable"""
    print(f"\nBuilding {APP_NAME} (One File) v{VERSION_NUMBER}...")
    buildArgs = getBaseArgs()
    buildArgs.append('--onefile')
    # PyInstaller uses UPX by default if found in PATH, so no extra arg needed here
    PyInstaller.__main__.run(buildArgs)
    print(f"\nBuild complete! Location: {DIST_DIR / f'{APP_NAME}.exe'}")

def buildOnedir():
    """Build as directory with executable and dependencies"""
    print(f"\nBuilding {APP_NAME} (One Directory) v{VERSION_NUMBER}...")
    buildArgs = getBaseArgs()
    buildArgs.append('--onedir')
    PyInstaller.__main__.run(buildArgs)
    print(f"\nBuild complete! Location: {DIST_DIR / APP_NAME}")

# --- User Interface ---

def showMenu():
    """Show build options menu"""
    print("=" * 60)
    print(f"   {APP_NAME} v{VERSION_NUMBER} - Build Script")
    print("=" * 60)
    print("\nBuild Options:")
    print("   1. One File (single .exe, slower startup)")
    print("   2. One Directory (folder with .exe, faster startup)")
    print("   3. Custom spec file (uses specific yt-dlp hooks & UPX)")
    print("   4. Clean build directories only")
    print("   0. Exit")
    print()
    return input("Select option [1-4, 0]: ").strip()

def main():
    """Main build process"""
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    try:
        while(True):
            userChoice = showMenu()
            
            if userChoice == "0":
                sys.exit(0)
            
            if userChoice == "4":
                cleanBuildDirs()
                continue

            if userChoice in ["1", "2", "3"]:
                cleanBuildDirs()
                if not ASSETS_DIR.exists():
                    print(f"Warning: {ASSETS_DIR} not found. Creating empty folder.")
                    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

                if userChoice == "1":
                    buildOnefile()
                elif userChoice == "2":
                    buildOnedir()
                elif userChoice == "3":
                    specFile = createSpecFile()
                    PyInstaller.__main__.run([str(specFile), '--clean', '--noconfirm'])

                print("\n" + "=" * 60)
                print("🎉 Build process completed successfully!")
                print("=" * 60)
                break
            else:
                print("Invalid option")
            
    except KeyboardInterrupt:
        print("\n[EXIT] Build cancelled by user.")
        sys.exit(0)
    except Exception as buildError:
        print(f"\nBuild failed: {buildError}")
        sys.exit(1)

if __name__ == "__main__":
    main()