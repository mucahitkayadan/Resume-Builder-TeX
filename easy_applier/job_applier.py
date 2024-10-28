from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class JobApplier:
    def __init__(self, driver):
        self.driver = driver

    def apply_to_job(self, job_url, resume_path):
        self.driver.get(job_url)
        try:
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-apply-button"))
            )
            apply_button.click()

            # Fill out application form
            # This part will vary depending on the job application structure
            # You'll need to implement form filling logic here

            # Upload resume
            upload_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            upload_button.send_keys(resume_path)

            # Submit application
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            return True
        except Exception as e:
            print(f"Failed to apply to job: {str(e)}")
            return False
