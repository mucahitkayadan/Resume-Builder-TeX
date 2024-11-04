import sqlite3
import os
from pathlib import Path

def get_project_root() -> Path:
    """Get the project root directory."""
    current_dir = Path(__file__).parent
    return current_dir.parent

def initialize_resume_database(db_path: str) -> None:
    """Initialize the resume database with necessary tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop the existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS resumes')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
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
    
    # Create an index on id
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resumes_id ON resumes(id)')
    
    conn.commit()
    conn.close()

def initialize_user_database(db_path: str) -> None:
    """Initialize the user database with necessary tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            linkedin TEXT,
            github TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def initialize_databases():
    """Initialize all necessary databases."""
    # Get project root directory
    project_root = get_project_root()
    
    # Create db directory in project root if it doesn't exist
    db_dir = project_root / "db"
    db_dir.mkdir(exist_ok=True)
    
    # Initialize resume database
    resume_db_path = db_dir / "resumes.db"
    initialize_resume_database(str(resume_db_path))
    print(f"Resume database initialized at {resume_db_path}")
    
    # Initialize user database
    user_db_path = db_dir / "user.db"
    initialize_user_database(str(user_db_path))
    print(f"User database initialized at {user_db_path}")

if __name__ == "__main__":
    initialize_databases()
