import subprocess
import sys
import importlib.metadata

def getPackageName(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    return line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()

def updateAllDeps():
    print("Reading requirements.txt...")
    
    packages = []
    try:
        with open("requirements.txt", "r") as f:
            for line in f:
                pkg = getPackageName(line)
                if pkg:
                    packages.append(pkg)
    except FileNotFoundError:
        print("requirements.txt not found!")
        return

    if not packages:
        print("No packages found in requirements.txt")
        return

    print(f"Upgrading {len(packages)} packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)
        
        newLines = []
        for pkg in packages:
            try:
                currentVersion = importlib.metadata.version(pkg)
                
                newLines.append(f"{pkg}=={currentVersion}")
                print(f"   {pkg}: {currentVersion}")
            except importlib.metadata.PackageNotFoundError:
                print(f"   Could not find installed version for {pkg}, skipping...")

        with open("requirements.txt", "w") as f:
            f.write("\n".join(newLines))
            f.write("\n")
            
        print("\nrequirements.txt updated successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to upgrade packages: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    updateAllDeps()