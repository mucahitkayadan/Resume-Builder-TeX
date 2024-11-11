from typing import Any, Dict, Union
import unicodedata

def ensure_string(data: Any) -> Union[str, Dict[str, Any]]:
    """
    Ensure all data is in string format, handling nested dictionaries.
    
    Args:
        data: Input data of any type
        
    Returns:
        String or dictionary with string values
    """
    if isinstance(data, dict):
        return {k: ensure_string(v) for k, v in data.items()}
    elif isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, str):
        return data
    return str(data)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Input filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    valid_chars = "-_.() %s%s" % (unicodedata.normalize('NFKD', filename), '')
    filename = ''.join(c for c in valid_chars if c.isprintable())
    
    # Replace spaces with underscores
    return filename.replace(' ', '_') 