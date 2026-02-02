import requests
import webbrowser
from packaging import version

class UpdateService:
    VERSION_URL = "https://gist.githubusercontent.com/AhmedEssamYassin/19fe6b989b7abf1365d81829957fcac1/raw/version.json"
    
    @staticmethod
    def checkForUpdates(currentVersion):
        """
        Returns (bool, str, str): (isUpdateAvailable, latestVersion, downloadUrl)
        """
        try:
            response = requests.get(UpdateService.VERSION_URL, timeout=3)
            if response.status_code == 200:
                data = response.json()
                latestVersion = data.get("latest_version")
                downloadUrl = data.get("download_url")
                
                if version.parse(latestVersion) > version.parse(currentVersion):
                    return True, latestVersion, downloadUrl
                    
            return False, None, None
        except Exception:
            return False, None, None

    @staticmethod
    def openDownloadPage(url):
        webbrowser.open(url)