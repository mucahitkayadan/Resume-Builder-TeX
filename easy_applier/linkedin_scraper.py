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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            logger.debug("Initializing Chrome WebDriver using WebDriver Manager...")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
            
            logger.debug("Attempting to navigate to a page...")
            self.driver.get("https://www.google.com")
            logger.info(f"Successfully navigated to Google. Page title: {self.driver.title}")
            
        except Exception as e:
            logger.error(f"Error initializing Chrome driver: {str(e)}")
            raise

        self.cookies_file = "linkedin_cookies.pkl"

    def login(self):
        if os.path.exists(self.cookies_file):
            self.load_cookies()
        else:
            self.perform_login()
            self.save_cookies()

        # Check for new device prompt
        try:
            verify_device_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-litms-control-urn='verify_pin_submit']"))
            )
            verify_device_button.click()
            
            # Handle PIN input (you might need to implement a way to get the PIN, e.g., from user input or email)
            pin_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "input__email_verification_pin"))
            )
            pin = input("Enter the PIN sent to your email: ")
            pin_input.send_keys(pin)
            
            submit_button = self.driver.find_element(By.ID, "email-pin-submit-button")
            submit_button.click()
        except TimeoutException:
            print("No new device verification required")

    def load_cookies(self):
        self.driver.get("https://www.linkedin.com")
        cookies = pickle.load(open(self.cookies_file, "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_file, "wb"))

    def perform_login(self):
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for the email field and enter the email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)
            
            # Enter the password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click the login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for the login process to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            print("Login successful")
        except Exception as e:
            print(f"Login failed: {str(e)}")

    def search_jobs(self, job_title, location):
        try:
            self.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}")
            time.sleep(5)  # Wait for the page to load
        except Exception as e:
            print(f"Job search failed: {str(e)}")

    def get_job_details(self):
        jobs = []
        try:
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
            for card in job_cards[:10]:  # Limit to first 10 jobs for this example
                title = card.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
                company = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
                link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                
                # Click on the job to load its description
                card.click()
                time.sleep(2)  # Wait for description to load
                
                description = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-view-layout"))
                ).text
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "link": link,
                    "description": description
                })
            return jobs
        except Exception as e:
            print(f"Failed to get job details: {str(e)}")
            return []

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def __del__(self):
        if hasattr(self, 'driver'):
            logger.debug("Closing Chrome WebDriver...")
            self.driver.quit()
            logger.info("Chrome WebDriver closed successfully")
