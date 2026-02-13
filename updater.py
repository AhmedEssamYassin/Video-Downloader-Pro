import sys
import os
import time
import shutil
import tkinter as tk
from tkinter import ttk
from threading import Thread

def performUpdate(oldExe, newExe, root, statusLabel):
    exeName = os.path.basename(oldExe)
    
    # Helper to safely update the UI from the background thread
    def updateText(text):
        root.after(0, lambda: statusLabel.config(text=text))
        
    def closeUpdater():
        root.after(0, root.destroy)

    updateText(f"Waiting for {exeName} to close...")
    
    # Wait for the main process to exit (max 15 seconds)
    for _ in range(15):
        try:
            if os.path.exists(oldExe):
                os.remove(oldExe)
            break
        except PermissionError:
            time.sleep(1)
    else:
        updateText("Timeout waiting for process to exit...")
        time.sleep(3)
        closeUpdater()
        return
        
    updateText("Installing update...")
    try:
        shutil.move(newExe, oldExe)
    except Exception as e:
        updateText(f"Failed to install: {e}")
        time.sleep(3)
        closeUpdater()
        return
        
    updateText("Starting application...")
    try:
        os.startfile(oldExe)
    except Exception:
        pass
        
    time.sleep(1)
    closeUpdater()

def main():
    if len(sys.argv) != 3:
        sys.exit(1)
        
    oldExe = sys.argv[1]
    newExe = sys.argv[2]
    
    # Setup simple UI
    root = tk.Tk()
    root.title("Updating...")
    
    # Calculate screen center
    windowWidth = 350
    windowHeight = 120
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    centerX = int(screenWidth / 2 - windowWidth / 2)
    centerY = int(screenHeight / 2 - windowHeight / 2)
    
    root.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
    root.resizable(False, False)
    root.attributes("-topmost", True) # Keep updater above other windows
    
    # UI Elements
    statusLabel = tk.Label(root, text="Initializing update...", font=("Segoe UI", 10))
    statusLabel.pack(pady=(20, 10))
    
    progressBar = ttk.Progressbar(root, mode='indeterminate', length=280)
    progressBar.pack(pady=10)
    progressBar.start(15)
    
    # Run update logic in a background thread so the UI doesn't freeze
    Thread(target=performUpdate, args=(oldExe, newExe, root, statusLabel), daemon=True).start()
    
    root.mainloop()

if __name__ == "__main__":
    main()