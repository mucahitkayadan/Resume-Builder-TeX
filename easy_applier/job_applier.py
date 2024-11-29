from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.core.database.unit_of_work import MongoUnitOfWork
from src.core.database.models.resume import Resume

class JobApplier:
    def __init__(self, driver, unit_of_work: MongoUnitOfWork):
        self.driver = driver
        self.uow = unit_of_work

    async def apply_to_job(self, job_url: str, resume_path: str) -> bool:
        self.driver.get(job_url)
        try:
            # Wait for and click apply button
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-apply-button"))
            )
            apply_button.click()

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
