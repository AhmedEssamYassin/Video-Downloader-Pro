import subprocess
import sys
import pkg_resources
import importlib

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
        
        importlib.reload(pkg_resources)
        
        newLines = []
        for pkg in packages:
            try:
                version = pkg_resources.get_distribution(pkg).version
                newLines.append(f"{pkg}=={version}")
                print(f"   {pkg}: {version}")
            except pkg_resources.DistributionNotFound:
                print(f"   Could not find version for {pkg}, skipping...")

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