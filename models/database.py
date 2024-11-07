from sqlalchemy import create_engine, Column, Integer, String, BLOB, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(Text)
    personal_information = Column(Text)
    career_summary = Column(Text)
    skills = Column(Text)
    work_experience = Column(Text)
    education = Column(Text)
    projects = Column(Text)
    awards = Column(Text)
    publications = Column(Text)
    pdf_content = Column(BLOB)
    model_type = Column(String)
    model_name = Column(String)
    temperature = Column(Float)
    cover_letter = Column(Text)
    cover_letter_pdf = Column(BLOB)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Preamble(Base):
    __tablename__ = 'preambles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    content = Column(Text)

class TexHeader(Base):
    __tablename__ = 'tex_headers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    content = Column(Text)

def init_db():
    project_root = Path(__file__).parent.parent
    db_dir = project_root / "db"
    db_dir.mkdir(exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_dir}/resumes.db')
    Base.metadata.create_all(engine)
    return engine

Session = sessionmaker(bind=init_db())
