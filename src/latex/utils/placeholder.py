from typing import Any, Dict


class LatexPlaceholder:
    """Utility class for handling LaTeX template placeholders."""

    @staticmethod
    def replace_placeholders(template: str, values: Dict[str, Any]) -> str:
        """
        Replace placeholders in LaTeX template with provided values.

        Args:
            template: LaTeX template with {{PLACEHOLDER}} style placeholders
            values: Dictionary of placeholder values

        Returns:
            Template with replaced values
        """
        result = template
        for key, value in values.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    @staticmethod
    def create_personal_info_dict(personal_info: dict) -> Dict[str, str]:
        """
        Create a dictionary of personal information placeholders.

        Args:
            personal_info: Dictionary containing personal information

        Returns:
            Dictionary with formatted placeholder keys
        """
        return {
            "NAME": personal_info.get("name", ""),
            "PHONE": personal_info.get("phone", ""),
            "EMAIL": personal_info.get("email", ""),
            "LINKEDIN": personal_info.get("linkedin", ""),
            "GITHUB": personal_info.get("github", ""),
            "ADDRESS": personal_info.get("address", ""),
        }
