class LatexEscaper:
    """Handles escaping of special characters for LaTeX."""

    @staticmethod
    def escape_text(text: str) -> str:
        """
        Escape special characters for LaTeX, preserving existing LaTeX commands.

        Args:
            text: Text to escape

        Returns:
            Escaped text safe for LaTeX
        """
        if not isinstance(text, str):
            text = str(text)

        # Don't escape existing LaTeX commands
        if text.startswith("\\"):
            return text

        # Special characters to escape
        special_chars = {
            "&": "\\&",
            "%": "\\%",
            "$": "\\$",
            "#": "\\#",
            "_": "\\_",
            "{": "\\{",
            "}": "\\}",
            "~": "\\textasciitilde{}",
            "^": "\\textasciicircum{}",
            # '\\': '\\textbackslash{}',
            "<": "\\textless{}",
            ">": "\\textgreater{}",
        }

        # Replace special characters
        for char, replacement in special_chars.items():
            # Skip if it looks like a LaTeX command
            if not text.startswith("\\"):
                text = text.replace(char, replacement)

        return text

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
            k: cls.escape_text(v) if isinstance(v, str) else v for k, v in data.items()
        }
