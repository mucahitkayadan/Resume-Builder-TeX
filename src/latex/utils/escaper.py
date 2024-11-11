class LatexEscaper:
    """Utility class for escaping LaTeX special characters."""
    
    SPECIAL_CHARS = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    
    @classmethod
    def escape_text(cls, text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Input text to escape
            
        Returns:
            Escaped text safe for LaTeX
        """
        return ''.join(cls.SPECIAL_CHARS.get(c, c) for c in text)
    
    @classmethod
    def escape_dict(cls, data: dict) -> dict:
        """
        Escape all string values in a dictionary.
        
        Args:
            data: Dictionary with string values
            
        Returns:
            Dictionary with escaped string values
        """
        return {
            k: cls.escape_text(v) if isinstance(v, str) else v 
            for k, v in data.items()
        } 