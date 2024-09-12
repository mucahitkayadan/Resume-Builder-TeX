import os

class JobDescriptionLoader:
    def __init__(self, file_path):
        """
        Initialize the JobDescriptionLoader with the path to the job description file.

        Args:
            file_path (str): Path to the job description file.
        """
        self.file_path = file_path
        self._job_description = None

    def load(self):
        """
        Load the job description from the file.

        Returns:
            str: The job description text.

        Raises:
            FileNotFoundError: If the job description file is not found.
            IOError: If there's an error reading the file.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Job description file not found: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self._job_description = file.read().strip()
        except IOError as e:
            raise IOError(f"Error reading job description file: {e}")

        return self._job_description

    def get_job_description(self):
        """
        Get the loaded job description. If not loaded, load it first.

        Returns:
            str: The job description text.
        """
        if self._job_description is None:
            return self.load()
        return self._job_description

    def update_job_description(self, new_description):
        """
        Update the job description and save it to the file.

        Args:
            new_description (str): The new job description text.

        Raises:
            IOError: If there's an error writing to the file.
        """
        self._job_description = new_description.strip()
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(self._job_description)
        except IOError as e:
            raise IOError(f"Error writing to job description file: {e}")
