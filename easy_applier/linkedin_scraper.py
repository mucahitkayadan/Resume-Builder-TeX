import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkedInScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = webdriver.Chrome()  # Ensure you have ChromeDriver installed

    def login(self):
        self.driver.get("https://www.linkedin.com/login")
        self.driver.find_element(By.ID, "username").send_keys(self.email)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)  # Wait for login to complete

    def search_jobs(self, keywords, location):
        self.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}")
        time.sleep(5)  # Wait for job results to load

    def get_job_details(self):
        job_listings = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
        jobs = []
        for job in job_listings:
            title = job.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
            company = job.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
            location = job.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-item").text
            link = job.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            jobs.append({"title": title, "company": company, "location": location, "link": link})
        return jobs

    def close(self):
        self.driver.quit()

