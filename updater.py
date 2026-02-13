import sys
import os
import time
import shutil

def main():
    if len(sys.argv) != 3:
        print("Usage: updater.exe <old_exe_path> <new_exe_path>")
        sys.exit(1)
    
    old_exe = sys.argv[1]
    new_exe = sys.argv[2]
    
    exe_name = os.path.basename(old_exe)
    
    # Wait for the main process to exit (max 10 seconds)
    print(f"Waiting for {exe_name} to close...")
    for _ in range(10):
        try:
            # Try to delete - if it fails, process is still running
            if os.path.exists(old_exe):
                os.remove(old_exe)
                break
        except PermissionError:
            time.sleep(1)
    else:
        print("Timeout waiting for process to exit")
        sys.exit(1)
    
    # Move new exe to old location
    print(f"Installing update...")
    try:
        shutil.move(new_exe, old_exe)
    except Exception as e:
        print(f"Failed to install: {e}")
        sys.exit(1)
    
    # Launch the updated app
    print(f"Starting {exe_name}...")
    os.startfile(old_exe)
    
    print("Update complete!")

if __name__ == "__main__":
    main()