"""
Asset loader utility for accessing application assets
"""

import json
from pathlib import Path
from typing import Dict, Any


class AssetLoader:
    """Centralized asset loading and management"""
    
    # Get assets directory (works for both development and bundled app)
    if getattr(__import__('sys'), 'frozen', False):
        # Running as compiled executable
        ASSETS_DIR = Path(__import__('sys')._MEIPASS) / "assets"
    else:
        # Running in development
        ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
    
    # Cache for loaded assets
    _config_cache = None
    _translations_cache = {}
    
    @classmethod
    def getAssetsDir(cls) -> Path:
        """Get the assets directory path"""
        return cls.ASSETS_DIR
    
    @classmethod
    def getImagePath(cls, filename: str) -> Path:
        """Get path to an image asset"""
        return cls.ASSETS_DIR / "images" / filename
    
    @classmethod
    def getDataPath(cls, filename: str) -> Path:
        """Get path to a data asset"""
        return cls.ASSETS_DIR / "data" / filename
    
    @classmethod
    def loadConfig(cls) -> Dict[str, Any]:
        """Load default configuration (cached)"""
        if cls._config_cache is None:
            config_path = cls.getDataPath("default_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._config_cache = json.load(f)
        return cls._config_cache
    
    @classmethod
    def loadTranslations(cls, language: str = "en") -> Dict[str, Any]:
        """Load translations for specified language (cached)"""
        if language not in cls._translations_cache:
            trans_path = cls.ASSETS_DIR / "data" / "translations" / f"{language}.json"
            if not trans_path.exists():
                # Fallback to English
                trans_path = cls.ASSETS_DIR / "data" / "translations" / "en.json"
            
            with open(trans_path, 'r', encoding='utf-8') as f:
                cls._translations_cache[language] = json.load(f)
        
        return cls._translations_cache[language]
    
    @classmethod
    def getTranslation(cls, key: str, language: str = "en") -> str:
        """
        Get a specific translation by dot-notation key
        
        Example:
            getTranslation("buttons.download_now", "en")
            Returns: "DOWNLOAD NOW"
        """
        translations = cls.loadTranslations(language)
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = translations.get('translations', {})
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)  # Return key if not found
            else:
                return key
        
        return value if isinstance(value, str) else key
    
    @classmethod
    def getAvailableLanguages(cls) -> list:
        """Get list of available language codes"""
        trans_dir = cls.ASSETS_DIR / "data" / "translations"
        if not trans_dir.exists():
            return ["en"]
        
        return [f.stem for f in trans_dir.glob("*.json")]
    
    @classmethod
    def getSupportedPlatforms(cls) -> list:
        """Get list of supported platforms from config"""
        config = cls.loadConfig()
        return config.get("supported_platforms", [])
    
    @classmethod
    def getQualityOptions(cls) -> list:
        """Get available quality options from config"""
        config = cls.loadConfig()
        return config.get("quality_options", ["best", "720p", "480p"])
    
    @classmethod
    def getFormatOptions(cls) -> list:
        """Get available format options from config"""
        config = cls.loadConfig()
        return config.get("format_options", ["MP4", "MP3"])
    
    @classmethod
    def getDownloadPresets(cls) -> list:
        """Get download presets from config"""
        config = cls.loadConfig()
        return config.get("download_presets", [])


# Convenience functions
def loadConfig() -> Dict[str, Any]:
    """Load default configuration"""
    return AssetLoader.loadConfig()


def loadTranslations(language: str = "en") -> Dict[str, Any]:
    """Load translations for specified language"""
    return AssetLoader.loadTranslations(language)


def getTranslation(key: str, language: str = "en") -> str:
    """Get a specific translation by key"""
    return AssetLoader.getTranslation(key, language)