import os
from pathlib import Path
from typing import Optional

from .selenium_connection import SeleniumConnection


class ConnectionFactory:
    @staticmethod
    def create_selenium_connection(
        profile_name: Optional[str] = None,
        data_dir: Optional[str] = None,
        driver_path: Optional[str] = None,
        headless: bool = False,
    ) -> SeleniumConnection:
        """
        Create a SeleniumConnection with the specified configuration

        Args:
            profile_name: Name of Chrome profile to use
            data_dir: Path to Chrome user data directory
            driver_path: Path to chromedriver executable
            headless: Whether to run Chrome in headless mode
        """
        # Get default paths if not provided
        if not data_dir:
            data_dir = os.path.join(
                os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"
            )

        if not driver_path:
            driver_path = str(
                Path(__file__).parent.parent / "chromedriver-win64" / "chromedriver.exe"
            )

        return SeleniumConnection(
            chrome_profile_path=profile_name,
            chrome_data_path=data_dir,
            driver_path=driver_path,
            headless=headless,
        )
