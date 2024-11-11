from typing import Dict, Any
from .escaper import LatexEscaper
from .placeholder import LatexPlaceholder

class PlaceholderMixin:
    """Mixin class for handling LaTeX placeholders."""
    
    def __init__(self):
        self.escaper = LatexEscaper()
        self.placeholder = LatexPlaceholder()
    
    def replace_placeholders(self, template: str, values: Dict[str, Any]) -> str:
        """Replace and escape placeholders in template."""
        escaped_values = {
            k: self.escaper.escape_text(str(v))
            for k, v in values.items()
        }
        return self.placeholder.replace_placeholders(template, escaped_values) 