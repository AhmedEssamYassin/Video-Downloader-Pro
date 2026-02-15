import re
import unicodedata

"""
The Windows file system has a traditional maximum path length (MAX_PATH) of 260 characters. 
This limit must contain the entire file path, including the drive letter (e.g., C:\), all folder names, 
the filename itself, and the file extension (e.g., .mp4).
"""

def sanitizeFilename(filename, max_length=200):
    """
    Sanitize filename for Windows compatibility
    - Remove invalid characters
    - Remove bidirectional text markers
    - Strip emojis and special Unicode
    - Limit length
    """
    # Remove bidirectional text markers and other control characters
    filename = ''.join(char for char in filename if unicodedata.category(char)[0] != 'C')
    
    # Remove emojis and other special symbols
    filename = re.sub(r'[^\w\s\-_.]', '', filename, flags=re.UNICODE)
    
    # Replace multiple spaces/underscores with single space
    filename = re.sub(r'[\s_]+', ' ', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length (leave room for extension and path)
    if len(filename) > max_length:
        filename = filename[:max_length]
        
    # Fallback to generic name if empty
    if not filename:
        filename = "video"
        
    return filename