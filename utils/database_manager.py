import sqlite3
import json
import logging

class DatabaseManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conn = sqlite3.connect('resumes.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
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
                model_type TEXT,
                runner_type TEXT,
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

    def insert_resume(self, company_name, job_title, job_description, content_dict, pdf_content, model_type, runner_type, temperature):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO resumes (
                    company_name, job_title, job_description, 
                    personal_information, career_summary, skills, 
                    work_experience, education, projects, 
                    awards, publications, pdf_content,
                    model_type, runner_type, temperature
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                runner_type,
                temperature
            ))
            self.conn.commit()
            self.logger.info("Resume inserted successfully")
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting resume: {e}")
            raise

    def get_resume(self, resume_id):
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT id, company_name, job_title, job_description, 
                           personal_information, career_summary, skills, 
                           work_experience, education, projects, 
                           awards, publications, pdf_content
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
                        'publications': row[11],
                        'pdf_content': row[12]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving resume: {str(e)}")
            raise

    def get_all_latex_headers(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT name, content FROM latex_headers')
            headers = {row[0]: row[1] for row in cursor.fetchall()}
            return headers
        except Exception as e:
            self.logger.error(f"Error retrieving LaTeX headers: {str(e)}")
            return {}

    def insert_latex_header(self, name, content):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO latex_headers (name, content)
                VALUES (?, ?)
            ''', (name, content))
            self.conn.commit()
            self.logger.info(f"LaTeX header '{name}' inserted successfully")
        except Exception as e:
            self.logger.error(f"Error inserting LaTeX header: {str(e)}")
            self.conn.rollback()

    def update_section(self, company_name, job_title, section_name, content):
        try:
            with self.conn:
                cursor = self.conn.cursor()
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

    def insert_preamble(self, content):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO preambles (id, content) VALUES (1, ?)', (content,))
            self.conn.commit()
            self.logger.info("Preamble inserted successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting preamble: {e}")
            raise

    def get_preamble(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT content FROM preambles WHERE id = 1')
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                self.logger.warning("Preamble not found in database")
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving preamble: {e}")
            return None

    def update_preamble(self, new_content):
        cursor = self.conn.cursor()
        try:
            cursor.execute('UPDATE preambles SET content = ? WHERE id = 1', (new_content,))
            self.conn.commit()
            self.logger.info("Preamble updated successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating preamble: {e}")
            raise

    def __del__(self):
        self.conn.close()
