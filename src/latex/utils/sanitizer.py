import unicodedata
from typing import Union


def sanitize_text(text: Union[str, bytes]) -> str:
    """
    Sanitize text by removing problematic characters and handling different input types.

    Args:
        text: Input text as string or bytes

    Returns:
        Sanitized string
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    elif not isinstance(text, str):
        text = str(text)

    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if unicodedata.category(char)[0] != "C"
    )
