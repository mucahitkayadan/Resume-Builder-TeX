import sqlite3
import json
import logging
from typing import Dict, Optional, Union, Any, List, Tuple
import os
from utils.logger_config import setup_logger
from pathlib import Path

logger = setup_logger(__name__)
class DatabaseManager:
    """
    A class to manage database operations for resume and cover letter storage.

    This class handles all database interactions including creating tables,
    inserting and retrieving resumes and cover letters, and managing preambles.

    Attributes:
        logger (logging.Logger): Logger for the DatabaseManager.
        resumes_conn (sqlite3.Connection): SQLite database connection for resumes.
        preambles_conn (sqlite3.Connection): SQLite database connection for preambles.
        user_conn (sqlite3.Connection): SQLite database connection for user information.
    """

    def __init__(self, 
                 resumes_db_path=None, 
                 preambles_db_path=None,
                 user_db_path=None):
        """
        Initialize database connections.
        
        Args:
            resumes_db_path (str, optional): Path to the resumes database
            preambles_db_path (str, optional): Path to the preambles database
            user_db_path (str, optional): Path to the user database
        """
        self.logger = logging.getLogger(__name__)
        
        # Get default paths if not provided
        project_root = Path(__file__).parent.parent
        db_dir = project_root / "db"
        
        # Use existing databases in db/
        self.resumes_conn = sqlite3.connect(str(db_dir / "resumes.db"))
        self.preambles_conn = sqlite3.connect(str(db_dir / "preambles.db"))
        self.user_conn = sqlite3.connect(str(db_dir / "user.db"))
        
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables in each database."""
        # Preambles database tables
        preambles_cursor = self.preambles_conn.cursor()
        preambles_cursor.execute('''
            CREATE TABLE IF NOT EXISTS preambles (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                content TEXT
            )
        ''')
        preambles_cursor.execute('''
            CREATE TABLE IF NOT EXISTS tex_headers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                content TEXT
            )
        ''')
        self.preambles_conn.commit()
        
        # Resumes database tables
        resumes_cursor = self.resumes_conn.cursor()
        resumes_cursor.execute('''
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
                model_type TEXT,
                model_name TEXT,
                temperature REAL,
                cover_letter TEXT,
                cover_letter_pdf BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.resumes_conn.commit()

    def insert_resume(self, company_name: str, job_title: str, job_description: str,
                     content_dict: Dict[str, str], pdf_content: bytes,
                     model_type: str, model_name: str, temperature: float,
                     cover_letter: Optional[str] = None,
                     cover_letter_pdf: Optional[bytes] = None) -> int:
        """
        Insert a new resume into the database.
        
        Args:
            company_name (str): Name of the company
            job_title (str): Title of the job
            job_description (str): Description of the job
            content_dict (Dict[str, str]): Dictionary containing resume sections
            pdf_content (bytes): Generated PDF content
            model_type (str): Type of AI model used
            model_name (str): Name of AI model used
            temperature (float): Temperature setting used for generation
            cover_letter (Optional[str]): Cover letter content
            cover_letter_pdf (Optional[bytes]): Generated cover letter PDF
        
        Returns:
            int: ID of the newly inserted resume
        """
        cursor = self.resumes_conn.cursor()
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
                model_type, model_name, temperature,
                cover_letter,
                cover_letter_pdf
            ))
            self.resumes_conn.commit()
            
            # Get the ID of the inserted resume
            resume_id = cursor.lastrowid
            self.logger.info(f"Resume inserted successfully with ID: {resume_id}")
            return resume_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting resume: {e}")
            self.resumes_conn.rollback()
            raise

    def update_cover_letter(self, resume_id, latex_content, pdf_content):
        try:
            with self.resumes_conn:
                self.resumes_conn.execute(
                    "UPDATE resumes SET cover_letter = ?, cover_letter_pdf = ? WHERE id = ?",
                    (latex_content.encode('utf-8'), pdf_content, resume_id)
                )
        except Exception as e:
            logger.error(f"Error updating cover letter: {str(e)}")
            raise

    def get_resume(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific resume from the database, excluding large binary data.

        Args:
            resume_id (int): The ID of the resume to retrieve.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the resume information if found,
                                      None otherwise. Excludes PDF content and other large binary data.

        Raises:
            sqlite3.Error: If there's an error executing the SQL query.
        """
        try:
            with self.resumes_conn:
                cursor: sqlite3.Cursor = self.resumes_conn.cursor()
                cursor.execute("""
                    SELECT id, company_name, job_title, job_description, 
                           personal_information, career_summary, skills, 
                           work_experience, education, projects, 
                           awards, publications, model_type, model_name, 
                           temperature, created_at, last_updated
                    FROM resumes WHERE id = ?
                """, (resume_id,))
                columns: List[str] = [column[0] for column in cursor.description]
                values: Optional[Tuple] = cursor.fetchone()
                if values:
                    result = dict(zip(columns, values))
                    # Decode UTF-8 encoded text fields
                    for key, value in result.items():
                        if isinstance(value, bytes):
                            result[key] = value.decode('utf-8')
                    return result
                return None
        except sqlite3.Error as e:
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
            with self.resumes_conn:
                cursor: sqlite3.Cursor = self.resumes_conn.cursor()
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
        cursor: sqlite3.Cursor = self.preambles_conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO preambles (id, content) VALUES (1, ?)', (content,))
            self.preambles_conn.commit()
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
            with self.preambles_conn:
                cursor: sqlite3.Cursor = self.preambles_conn.cursor()
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

    def update_preamble(self, new_content: str, template_id: int = 1) -> None:
        """Update preamble in preambles database."""
        cursor = self.preambles_conn.cursor()
        try:
            cursor.execute('UPDATE preambles SET content = ? WHERE id = ?', 
                         (new_content, template_id))
            self.preambles_conn.commit()
            self.logger.info("Preamble updated successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating preamble: {e}")
            raise

    def insert_tex_header(self, name: str, content: str) -> None:
        """Insert or update a TeX header in preambles database."""
        cursor = self.preambles_conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO tex_headers (name, content)
            VALUES (?, ?)
            ''', (name, content))
            self.preambles_conn.commit()
            self.logger.info(f"TeX header '{name}' inserted/updated successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting TeX header: {e}")
            raise

    def get_latest_resume_id(self) -> Optional[int]:
        """Get the ID of the most recently inserted resume."""
        cursor = self.resumes_conn.cursor()
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
        cursor: sqlite3.Cursor = self.resumes_conn.cursor()
        query = "UPDATE users SET signature_image = ? WHERE id = ?"
        cursor.execute(query, (image_data, user_id))
        self.resumes_conn.commit()

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
        cursor: sqlite3.Cursor = self.resumes_conn.cursor()
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
            with self.resumes_conn:
                cursor: sqlite3.Cursor = self.resumes_conn.cursor()
                cursor.execute('SELECT personal_information FROM resumes WHERE id = ?', (resume_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            self.logger.error(f"Error retrieving personal information: {str(e)}")
            raise

    def __del__(self):
        """Close all database connections when the object is destroyed."""
        self.resumes_conn.close()
        self.preambles_conn.close()
        self.user_conn.close()

    def get_all_resumes(self) -> List[Tuple[Any, ...]]:
        """Get all resumes from the database."""
        cursor = self.resumes_conn.cursor()
        try:
            cursor.execute('''
                SELECT id, company_name, job_title, created_at 
                FROM resumes 
                ORDER BY id DESC
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error getting all resumes: {e}")
            return []

    def update_resume(self, resume_id: int, updated_data: Dict[str, Any]) -> None:
        """Update resume data in resumes database."""
        cursor = self.resumes_conn.cursor()
        try:
            set_clause = ", ".join([f"{key} = ?" for key in updated_data.keys()])
            query = f"UPDATE resumes SET {set_clause}, last_updated = CURRENT_TIMESTAMP WHERE id = ?"
            values = list(updated_data.values()) + [resume_id]
            cursor.execute(query, values)
            self.resumes_conn.commit()
            self.logger.info(f"Resume with ID {resume_id} updated successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating resume: {e}")
            self.resumes_conn.rollback()
            raise

    def get_latest_resume(self) -> Optional[Dict[str, Any]]:
        """Get the most recently created resume."""
        try:
            cursor = self.resumes_conn.cursor()
            cursor.execute("SELECT * FROM resumes ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, result))
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving latest resume: {str(e)}")
            raise

    def get_resume_full(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a full resume from the database, including all fields.

        Args:
            resume_id (int): The ID of the resume to retrieve.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing all resume information if found,
                                      None otherwise. Includes PDF content.

        Raises:
            sqlite3.Error: If there's an error executing the SQL query.
        """
        try:
            with self.resumes_conn:
                cursor: sqlite3.Cursor = self.resumes_conn.cursor()
                cursor.execute("""
                    SELECT id, company_name, job_title, job_description, 
                           personal_information, career_summary, skills, 
                           work_experience, education, projects, 
                           awards, publications, pdf_content, model_type, model_name, 
                           temperature, created_at, last_updated
                    FROM resumes WHERE id = ?
                """, (resume_id,))
                columns: List[str] = [column[0] for column in cursor.description]
                values: Optional[Tuple] = cursor.fetchone()
                if values:
                    result = dict(zip(columns, values))
                    # Decode UTF-8 encoded text fields, skip pdf_content
                    for key, value in result.items():
                        if isinstance(value, bytes) and key != 'pdf_content':
                            result[key] = value.decode('utf-8')
                    return result
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving full resume: {str(e)}")
            raise

    def get_resume_for_cover_letter(self, resume_id: int) -> Optional[Dict[str, str]]:
        """
        Retrieve specific resume sections needed for cover letter generation.

        Args:
            resume_id (int): The ID of the resume to retrieve.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing specific resume sections if found,
                                      None otherwise.

        Raises:
            sqlite3.Error: If there's an error executing the SQL query.
        """
        try:
            with self.resumes_conn:
                cursor: sqlite3.Cursor = self.resumes_conn.cursor()
                cursor.execute("""
                    SELECT personal_information, career_summary, skills, 
                           work_experience, education, projects, 
                           awards, publications
                    FROM resumes WHERE id = ?
                """, (resume_id,))
                columns: List[str] = [column[0] for column in cursor.description]
                values: Optional[Tuple] = cursor.fetchone()
                if values:
                    result = dict(zip(columns, values))
                    # Decode UTF-8 encoded text fields
                    for key, value in result.items():
                        if isinstance(value, bytes):
                            result[key] = value.decode('utf-8')
                    return result
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving resume for cover letter: {str(e)}")
            raise

    def get_tex_header(self, name: str) -> Optional[str]:
        """
        Get a TeX header template from the preambles database.
        
        Args:
            name (str): Name of the TeX header template
            
        Returns:
            Optional[str]: The template content if found, None otherwise
        """
        cursor = self.preambles_conn.cursor()
        try:
            cursor.execute('SELECT content FROM tex_headers WHERE name = ?', (name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting TeX header '{name}': {e}")
            return None
