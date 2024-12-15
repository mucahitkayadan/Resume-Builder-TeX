import time
import pickle
import os
import logging
import subprocess
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .connections.connection_factory import ConnectionFactory

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, email, password, profile_name=None, headless=False):
        self.email = email
        self.password = password
        
        # Create Selenium connection using factory
        self.connection = ConnectionFactory.create_selenium_connection(
            profile_name=profile_name,
            headless=headless
        )
        
        try:
            self.driver = self.connection.connect()
            # Perform login immediately after connection
            self.perform_login()
            logger.info("Successfully initialized LinkedIn scraper and logged in")
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn scraper: {str(e)}")
            raise

    def perform_login(self):
        """Perform LinkedIn login with retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info("Attempting LinkedIn login...")
                self.driver.get("https://www.linkedin.com/login")
                time.sleep(2)  # Wait for page to load
                
                # Wait for the email field and enter the email
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email_field.clear()
                email_field.send_keys(self.email)
                
                # Enter the password
                password_field = self.driver.find_element(By.ID, "password")
                password_field.clear()
                password_field.send_keys(self.password)
                
                # Click the login button
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                
                # Wait for the login process to complete by checking for the feed or nav bar
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "global-nav"))
                )
                
                # Check for verification prompt
                try:
                    verify_device_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-litms-control-urn='verify_pin_submit']"))
                    )
                    logger.info("Device verification required")
                    
                    # Handle verification if needed
                    self._handle_verification()
                except TimeoutException:
                    logger.info("No verification required")
                
                logger.info("Login successful")
                return True
                
            except TimeoutException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Login attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                    time.sleep(2)
                else:
                    logger.error("Login failed after all attempts")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during login: {str(e)}")
                raise

    def _handle_verification(self):
        """Handle LinkedIn's verification process"""
        try:
            # Wait for PIN input field
            pin_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "input__email_verification_pin"))
            )
            
            # Get PIN from user
            pin = input("Enter the PIN sent to your email: ")
            pin_input.send_keys(pin)
            
            # Submit PIN
            submit_button = self.driver.find_element(By.ID, "email-pin-submit-button")
            submit_button.click()
            
            # Wait for successful verification
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            logger.info("Verification successful")
            return True
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            raise

    def search_jobs(self, job_title, location):
        """Search for jobs with retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ensure we're logged in by checking for nav bar
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "global-nav"))
                    )
                except TimeoutException:
                    logger.warning("Session may have expired, attempting to login again")
                    self.perform_login()
                
                # Navigate to jobs search
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"
                self.driver.get(search_url)
                
                # Wait longer and try multiple selectors for job listings
                selectors = [
                    ".jobs-search-results-list",
                    ".jobs-search-results__list",
                    ".jobs-search__results-list",
                    "[data-job-search-results-container]",
                    ".jobs-search__job-card"
                ]
                
                # Try each selector
                for selector in selectors:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"Found job listings with selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                else:
                    # If no selector worked, try scrolling and waiting
                    logger.warning("Job listings not immediately visible, trying to scroll...")
                    self.driver.execute_script("window.scrollTo(0, 300)")
                    time.sleep(5)  # Give more time for dynamic content to load
                    
                    # One final check for any job cards
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-container"))
                        )
                        logger.info("Found job cards after scrolling")
                    except TimeoutException:
                        if attempt == max_retries - 1:
                            raise TimeoutException("Could not find any job listings")
                        continue
                
                logger.info(f"Successfully loaded job search for {job_title} in {location}")
                return True
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Search attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                    time.sleep(2)
                else:
                    logger.error(f"Job search failed after all attempts: {str(e)}")
                    raise

    def load_cookies(self):
        self.driver.get("https://www.linkedin.com")
        cookies = pickle.load(open(self.cookies_file, "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_file, "wb"))

    def get_job_details(self):
        """Get details of visible job listings"""
        jobs = []
        try:
            # Wait for job cards with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    job_cards = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-container"))
                    )
                    break
                except TimeoutException:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} to find job cards failed, retrying...")
                    time.sleep(2)

            for i, card in enumerate(job_cards[:10]):  # Limit to first 10 jobs
                try:
                    # Scroll card into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    time.sleep(1)  # Brief pause after scrolling
                    
                    # Extract basic info
                    title = card.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
                    company = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    # Click and wait for description
                    card.click()
                    time.sleep(2)
                    
                    # Try multiple selectors for job description
                    description = None
                    description_selectors = [
                        ".job-view-layout",
                        ".jobs-description",
                        ".jobs-description__content",
                        "[data-job-description]"
                    ]
                    
                    for selector in description_selectors:
                        try:
                            description = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            ).text
                            break
                        except TimeoutException:
                            continue
                    
                    if description:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "link": link,
                            "description": description
                        })
                        logger.info(f"Successfully extracted job {i+1}/10")
                    
                except Exception as e:
                    logger.error(f"Failed to extract job {i+1}: {str(e)}")
                    continue
                
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get job details: {str(e)}")
            return []

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def __del__(self):
        self.connection.close()
