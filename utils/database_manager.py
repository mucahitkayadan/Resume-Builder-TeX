import sqlite3
import json
import logging
from typing import Dict, Optional, Union, Any

class DatabaseManager:
    """
    A class to manage database operations for resume and cover letter storage.

    This class handles all database interactions including creating tables,
    inserting and retrieving resumes and cover letters, and managing preambles.

    Attributes:
        logger (logging.Logger): Logger for the DatabaseManager.
        conn (sqlite3.Connection): SQLite database connection.
    """

    def __init__(self):
        """
        Initialize the DatabaseManager with a connection to the SQLite database.
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.conn: sqlite3.Connection = sqlite3.connect('resumes.db')
        self.create_tables()

    def create_tables(self) -> None:
        """
        Create necessary tables in the database if they don't exist.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                job_title TEXT,
                job_description TEXT,
                personal_information TEXT,
                career_summary TEXT,
                skills TEXT,
                work_experience TEXT,
                education TEXT,
                projects TEXT,
                awards TEXT,
                publications TEXT,
                pdf_content BLOB,
                cover_letter TEXT,
                cover_letter_pdf BLOB,
                model_type TEXT,
                model_name TEXT,
                temperature REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preambles (
                id INTEGER PRIMARY KEY,
                content TEXT
            )
        ''')
        
        self.conn.commit()
        self.logger.info("Tables created/updated successfully")

    def insert_resume(self, company_name: str, job_title: str, job_description: str, 
                      content_dict: Dict[str, str], pdf_content: bytes, model_type: str, 
                      model_name: str, temperature: float, cover_letter: Optional[str] = None, 
                      cover_letter_pdf: Optional[bytes] = None) -> int:
        """
        Insert a new resume into the database.

        Args:
            company_name (str): Name of the company.
            job_title (str): Title of the job.
            job_description (str): Description of the job.
            content_dict (Dict[str, str]): Dictionary containing resume content sections.
            pdf_content (bytes): PDF content of the resume.
            model_type (str): Type of the AI model used.
            model_name (str): Name of the AI model used.
            temperature (float): Temperature setting used for AI generation.
            cover_letter (Optional[str]): Cover letter text, if available.
            cover_letter_pdf (Optional[bytes]): PDF content of the cover letter, if available.

        Returns:
            int: ID of the inserted resume.

        Raises:
            sqlite3.Error: If there's an error inserting the resume.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO resumes (
                    company_name, job_title, job_description, 
                    personal_information, career_summary, skills, 
                    work_experience, education, projects, 
                    awards, publications, pdf_content,
                    model_type, model_name, temperature,
                    cover_letter, cover_letter_pdf
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name, job_title, job_description,
                content_dict.get('personal_information', ''),
                content_dict.get('career_summary', ''),
                content_dict.get('skills', ''),
                content_dict.get('work_experience', ''),
                content_dict.get('education', ''),
                content_dict.get('projects', ''),
                content_dict.get('awards', ''),
                content_dict.get('publications', ''),
                pdf_content,
                model_type,
                model_name,
                temperature,
                cover_letter,
                cover_letter_pdf
            ))
            self.conn.commit()
            resume_id: int = cursor.lastrowid
            self.logger.info(f"Resume inserted successfully with ID: {resume_id}")
            return resume_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting resume: {e}")
            self.conn.rollback()
            raise

    def update_cover_letter(self, resume_id: int, cover_letter_latex: str, cover_letter_pdf: Optional[bytes] = None) -> None:
        """
        Update the cover letter for a specific resume.

        Args:
            resume_id (int): ID of the resume to update.
            cover_letter_latex (str): LaTeX content of the cover letter.
            cover_letter_pdf (Optional[bytes]): PDF content of the cover letter, if available.

        Raises:
            sqlite3.Error: If there's an error updating the cover letter.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        try:
            if cover_letter_pdf is not None:
                cursor.execute('''
                    UPDATE resumes
                    SET cover_letter = ?, cover_letter_pdf = ?
                    WHERE id = ?
                ''', (cover_letter_latex, cover_letter_pdf, resume_id))
            else:
                cursor.execute('''
                    UPDATE resumes
                    SET cover_letter = ?
                    WHERE id = ?
                ''', (cover_letter_latex, resume_id))
            self.conn.commit()
            self.logger.info(f"Cover letter updated for resume ID: {resume_id}")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating cover letter: {e}")
            self.conn.rollback()
            raise

    def get_resume(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a resume from the database by its ID.

        Args:
            resume_id (int): ID of the resume to retrieve.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing resume data if found, None otherwise.

        Raises:
            Exception: If there's an error retrieving the resume.
        """
        try:
            with self.conn:
                cursor: sqlite3.Cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT id, company_name, job_title, job_description, 
                           personal_information, career_summary, skills, 
                           work_experience, education, projects, 
                           awards, publications
                    FROM resumes WHERE id = ?
                ''', (resume_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'company_name': row[1],
                        'job_title': row[2],
                        'job_description': row[3],
                        'personal_information': row[4],
                        'career_summary': row[5],
                        'skills': row[6],
                        'work_experience': row[7],
                        'education': row[8],
                        'projects': row[9],
                        'awards': row[10],
                        'publications': row[11]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving resume: {str(e)}")
            raise

    def update_section(self, company_name: str, job_title: str, section_name: str, content: str) -> None:
        """
        Update a specific section of a resume.

        Args:
            company_name (str): Name of the company.
            job_title (str): Title of the job.
            section_name (str): Name of the section to update.
            content (str): New content for the section.

        Raises:
            Exception: If there's an error updating the section.
        """
        try:
            with self.conn:
                cursor: sqlite3.Cursor = self.conn.cursor()
                # First, check if the resume exists
                cursor.execute('''
                    SELECT content FROM resumes
                    WHERE company_name = ? AND job_title = ?
                ''', (company_name, job_title))
                result = cursor.fetchone()
                if result:
                    existing_content = json.loads(result[0]) if result[0] else {}
                else:
                    existing_content = {}
                
                # Update the specific section
                existing_content[section_name] = content
                
                # Update the entire content JSON
                cursor.execute('''
                    UPDATE resumes
                    SET content = ?
                    WHERE company_name = ? AND job_title = ?
                ''', (json.dumps(existing_content), company_name, job_title))
                
                if cursor.rowcount == 0:
                    # If no rows were updated, insert a new record
                    cursor.execute('''
                        INSERT INTO resumes (company_name, job_title, content)
                        VALUES (?, ?, ?)
                    ''', (company_name, job_title, json.dumps({section_name: content})))
                
            self.logger.info(f"Updated {section_name} section for {company_name} - {job_title}")
        except Exception as e:
            self.logger.error(f"Error updating {section_name} section: {str(e)}")
            raise

    def insert_preamble(self, content: str) -> None:
        """
        Insert or replace the preamble content in the database.

        Args:
            content (str): The preamble content to insert.

        Raises:
            sqlite3.Error: If there's an error inserting the preamble.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO preambles (id, content) VALUES (1, ?)', (content,))
            self.conn.commit()
            self.logger.info("Preamble inserted successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting preamble: {e}")
            raise

    def get_preamble(self, preamble_id: int = 1) -> Optional[str]:
        """
        Retrieve the preamble content from the database.

        Args:
            preamble_id (int): ID of the preamble to retrieve (default is 1).

        Returns:
            Optional[str]: The preamble content if found, None otherwise.

        Raises:
            Exception: If there's an error retrieving the preamble.
        """
        try:
            with self.conn:
                cursor: sqlite3.Cursor = self.conn.cursor()
                cursor.execute('SELECT content FROM preambles WHERE id = ?', (preamble_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    self.logger.error(f"Preamble with ID {preamble_id} not found")
                    return None
        except Exception as e:
            self.logger.error(f"Error retrieving preamble: {str(e)}")
            raise

    def update_preamble(self, new_content: str) -> None:
        """
        Update the preamble content in the database.

        Args:
            new_content (str): The new preamble content.

        Raises:
            sqlite3.Error: If there's an error updating the preamble.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        try:
            cursor.execute('UPDATE preambles SET content = ? WHERE id = 1', (new_content,))
            self.conn.commit()
            self.logger.info("Preamble updated successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating preamble: {e}")
            raise

    def get_latest_resume_id(self) -> Optional[int]:
        """
        Get the ID of the most recently inserted resume.

        Returns:
            Optional[int]: The ID of the latest resume, or None if no resumes exist.

        Raises:
            sqlite3.Error: If there's an error retrieving the latest resume ID.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT MAX(id) FROM resumes')
            result = cursor.fetchone()
            return result[0] if result[0] is not None else None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting latest resume ID: {e}")
            return None

    def store_signature_image(self, user_id: int, image_data: bytes) -> None:
        """
        Store a user's signature image in the database.

        Args:
            user_id (int): ID of the user.
            image_data (bytes): Binary data of the signature image.

        Raises:
            sqlite3.Error: If there's an error storing the signature image.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        query = "UPDATE users SET signature_image = ? WHERE id = ?"
        cursor.execute(query, (image_data, user_id))
        self.conn.commit()

    def get_signature_image(self, user_id: int) -> Optional[bytes]:
        """
        Retrieve a user's signature image from the database.

        Args:
            user_id (int): ID of the user.

        Returns:
            Optional[bytes]: Binary data of the signature image if found, None otherwise.

        Raises:
            sqlite3.Error: If there's an error retrieving the signature image.
        """
        cursor: sqlite3.Cursor = self.conn.cursor()
        query = "SELECT signature_image FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_personal_information(self, resume_id: int) -> Optional[str]:
        """
        Retrieve the personal information for a specific resume.

        Args:
            resume_id (int): ID of the resume.

        Returns:
            Optional[str]: Personal information if found, None otherwise.

        Raises:
            Exception: If there's an error retrieving the personal information.
        """
        try:
            with self.conn:
                cursor: sqlite3.Cursor = self.conn.cursor()
                cursor.execute('SELECT personal_information FROM resumes WHERE id = ?', (resume_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            self.logger.error(f"Error retrieving personal information: {str(e)}")
            raise

    def __del__(self) -> None:
        """
        Close the database connection when the object is destroyed.
        """
        self.conn.close()