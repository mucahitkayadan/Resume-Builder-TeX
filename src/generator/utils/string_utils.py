from typing import Any, Dict, Union, Tuple
import unicodedata
import logging

logger = logging.getLogger(__name__)

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
    # Convert to lowercase and normalize unicode characters
    filename = filename.lower()
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove all special characters except alphanumeric and spaces
    filename = ''.join(c for c in filename if c.isalnum() or c.isspace())
    
    # Replace spaces with underscores and remove multiple underscores
    filename = filename.replace(' ', '_')
    filename = '_'.join(filter(None, filename.split('_')))
    
    return filename

def get_company_name_and_job_title(folder_name: str) -> Tuple[str, str]:
    """
    Extract company name and job title from folder name.
    """
    try:
        company_name, job_title = folder_name.split('|')
        company_name = sanitize_filename(company_name.strip())
        job_title = sanitize_filename(job_title.strip())
        return company_name, job_title
    except ValueError:
        return "Unknown_Company", "Unknown_Job_Title"
