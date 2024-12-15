import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
from typing import Optional
from pathlib import Path
import time
import psutil

logger = logging.getLogger(__name__)

class SeleniumConnection:
    def __init__(self, 
                 chrome_profile_path: Optional[str] = None,
                 chrome_data_path: Optional[str] = None,
                 driver_path: Optional[str] = None,
                 headless: bool = False):
        """
        Initialize Selenium connection with Chrome profile and data directories
        
        Args:
            chrome_profile_path: Path to Chrome profile directory
            chrome_data_path: Path to Chrome user data directory
            driver_path: Path to chromedriver executable
            headless: Whether to run Chrome in headless mode
        """
        self.chrome_profile_path = chrome_profile_path
        self.chrome_data_path = chrome_data_path
        self.driver_path = driver_path
        self.headless = headless
        self.driver = None

    def connect(self) -> webdriver.Chrome:
        """Create and return a configured Chrome WebDriver instance"""
        try:
            # Kill any existing Chrome processes first
            self._kill_chrome_processes()
            
            options = self._configure_chrome_options()
            service = self._configure_chrome_service()
            
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver = webdriver.Chrome(
                        service=service,
                        options=options
                    )
                    logger.info("Chrome WebDriver initialized successfully")
                    return self.driver
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                        time.sleep(2)  # Wait before retrying
                        self._kill_chrome_processes()  # Kill any hanging processes
                    else:
                        raise
                
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise

    def _configure_chrome_options(self) -> Options:
        """Configure Chrome options with profile and data paths"""
        options = Options()
        
        # Add common options first
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Add remote debugging port to prevent DevTools issues
        options.add_argument("--remote-debugging-port=9222")
        
        # Disable extensions and background apps
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-component-extensions-with-background-pages")
        
        # Set Chrome profile if provided
        if self.chrome_profile_path:
            options.add_argument(f'--profile-directory={self.chrome_profile_path}')
            logger.debug(f"Using Chrome profile: {self.chrome_profile_path}")

        # Set Chrome user data directory if provided
        if self.chrome_data_path:
            # Ensure the path exists
            if not os.path.exists(self.chrome_data_path):
                logger.warning(f"Chrome user data directory does not exist: {self.chrome_data_path}")
                # Try to create the directory
                try:
                    os.makedirs(self.chrome_data_path, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create Chrome user data directory: {str(e)}")
                    # Continue without user data directory
                    return options
            
            options.add_argument(f'--user-data-dir={self.chrome_data_path}')
            logger.debug(f"Using Chrome data directory: {self.chrome_data_path}")

        if self.headless:
            options.add_argument("--headless=new")  # Use new headless mode

        return options

    def _configure_chrome_service(self) -> Service:
        """Configure Chrome service with driver path"""
        if self.driver_path:
            if not os.path.exists(self.driver_path):
                raise FileNotFoundError(f"Chrome driver not found at: {self.driver_path}")
            return Service(self.driver_path)
        else:
            # Use default chromedriver from PATH
            return Service()

    def close(self):
        """Close the WebDriver connection"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing Chrome WebDriver: {str(e)}")

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 

    def _kill_chrome_processes(self):
        """Kill any existing Chrome processes"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in ['chrome.exe', 'chromedriver.exe']:
                    try:
                        proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            time.sleep(1)  # Wait for processes to be killed
        except Exception as e:
            logger.warning(f"Failed to kill Chrome processes: {str(e)}") 