from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv
from utils.logger_config import setup_logger
import time

logger = setup_logger(__name__)

def extract_linkedin_job_description(url: str) -> str:
    """
    Extract job description from a LinkedIn job posting URL.
    
    Args:
        url (str): LinkedIn job posting URL
        
    Returns:
        str: Extracted job description
    """
    load_dotenv()
    
    # Get LinkedIn credentials from environment variables
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        raise ValueError("LinkedIn credentials not found in environment variables")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    try:
        logger.info("Setting up Chrome WebDriver...")
        # Use ChromeDriverManager to handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info(f"Navigating to URL: {url}")
        driver.get(url)
        
        # Wait for job description to load
        logger.info("Waiting for job description to load...")
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "description__text"))
        )
        
        # Extract the job description
        job_description = description_element.text
        logger.info("Job description extracted successfully")
        
        return job_description
        
    except Exception as e:
        logger.error(f"Failed to extract job description: {str(e)}")
        raise Exception(f"Failed to extract job description: {str(e)}")
        
    finally:
        if 'driver' in locals():
            logger.info("Closing Chrome WebDriver")
            driver.quit()
