import requests
import sys
import os
import subprocess
import time
from packaging import version
from threading import Thread

class UpdateService:
    VERSION_URL = "https://gist.githubusercontent.com/AhmedEssamYassin/19fe6b989b7abf1365d81829957fcac1/raw/version.json"
    
    @staticmethod
    def checkForUpdates(currentVersion):
        """Checks if a new version exists. Returns (bool, version, url)"""
        try:
            # Add a random number to avoid caching the JSON file
            response = requests.get(f"{UpdateService.VERSION_URL}?t={int(time.time())}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                latestVersion = data.get("latest_version")
                downloadUrl = data.get("download_url")
                
                if latestVersion and version.parse(latestVersion) > version.parse(currentVersion):
                    return True, latestVersion, downloadUrl
            return False, None, None
        except Exception:
            return False, None, None

    @staticmethod
    def downloadAndInstall(downloadUrl, progressCallback=None, completedCallback=None):
        """
        Downloads the update and triggers the restart/install process.
        Run this in a separate thread to avoid freezing the UI.
        """
        try:
            # 1. Determine paths
            if getattr(sys, 'frozen', False):
                currentExePath = sys.executable
                currentDir = os.path.dirname(currentExePath)
            else:
                print("Cannot self-update in dev environment")
                return

            newExePath = currentExePath + ".new"

            # 2. Download the file
            response = requests.get(downloadUrl, stream=True)
            totalSize = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(newExePath, 'wb') as file:
                for data in response.iter_content(chunk_size=4096):
                    file.write(data)
                    downloaded += len(data)
                    if progressCallback and totalSize > 0:
                        progressCallback(downloaded / totalSize)

            # 3. Download finished
            if completedCallback:
                completedCallback()
            
            # 4. Trigger the swap script
            UpdateService._restartAndSwap(currentExePath, newExePath)

        except Exception as e:
            print(f"Update failed: {e}")
            # Clean up partial download
            if os.path.exists(newExePath):
                os.remove(newExePath)

    @staticmethod
    def _restartAndSwap(oldExe, newExe):
        """
        Creates a temporary batch file to:
        1. Wait for this app to close
        2. Replace old EXE with new EXE
        3. Start new EXE
        4. Delete itself
        """
        batchScriptPath = "updater.bat"
        exeName = os.path.basename(oldExe)
        
        # Batch script content
        batchCommands = f"""
@echo off
echo Updating {exeName}...
timeout /t 2 /nobreak > NUL
del "{oldExe}"
move "{newExe}" "{oldExe}"
start "" "{oldExe}"
del "%~f0"
        """
        
        with open(batchScriptPath, "w") as f:
            f.write(batchCommands)

        # Run the batch script invisible
        subprocess.Popen(batchScriptPath, shell=True)
        
        # Close the current app immediately so the script can delete it
        os._exit(0)