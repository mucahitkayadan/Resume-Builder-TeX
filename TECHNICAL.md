# Technical Documentation

## Overview

This document provides a detailed technical overview of the AI-Powered Resume and Cover Letter Generator project. It covers the architecture, key components, and the flow of data through the system.

## Architecture

The project is structured into several key components:

- **Engine**: Contains the core logic for generating resumes and cover letters.
- **Loaders**: Responsible for loading various data formats and prompts.
- **Parsers**: Includes scripts for parsing job descriptions from external sources.
- **Utils**: Utility functions for document processing, database management, and LaTeX compilation.
- **Templates and Prompts**: LaTeX templates and AI prompts used for generating content.

## Key Components

### Engine

- **resume_creator.py**: Manages the process of generating resumes, including content generation and PDF compilation.
- **cover_letter_creator.py**: Handles the creation of cover letters, integrating with the AI model to generate content.
- **runners.py**: Defines the AI model runners, including OpenAI and Claude, for processing sections of the resume and cover letter.

### Loaders

- **tex_loader.py**: Loads LaTeX templates for document formatting.
- **json_loader.py**: Loads personal information from JSON files.
- **prompt_loader.py**: Loads system prompts for AI content generation.
- **job_description_loader.py**: Processes job descriptions for input into the AI model.

### Parsers

- **indeed_parser.py**: Fetches and parses job descriptions from Indeed job listings.

### Utils

- **document_utils.py**: Provides utility functions for document management, including directory creation and file saving.
- **latex_compiler.py**: Compiles LaTeX documents into PDFs.
- **database_manager.py**: Manages database operations, including storing and retrieving resumes and cover letters.
- **latex_header_loader.py**: Loads LaTeX headers for document formatting.

## Data Flow

1. **Input**: The user provides a job description and personal information.
2. **Processing**: The system uses AI models to generate content for each section of the resume and cover letter.
3. **Compilation**: The generated content is formatted using LaTeX templates and compiled into PDF documents.
4. **Output**: The final documents are saved in job-specific folders for easy access.

## AI Model Integration

The project integrates with OpenAI's GPT models and Claude models to generate content. The `runners.py` file defines the interface for interacting with these models, allowing for flexible model selection and configuration.

## Database Management

The project uses SQLite for storing resumes and cover letters. The `database_manager.py` file handles all database operations, ensuring data integrity and efficient retrieval.

## Error Handling

The system includes robust error handling mechanisms, logging errors and warnings to assist with debugging and ensuring smooth operation.

## Future Enhancements

- **Additional AI Models**: Integration with more AI models for improved content generation.
- **Enhanced Parsing**: Support for additional job description sources.
- **User Interface**: Development of a more user-friendly interface for input and output management.
- **Section Selection**: Allow the user to select specific sections of the resume to be generated.
- **Full Section Generation**: Allow the user to generate the entire resume or cover letter.
- **Auto Job Application**: Allow the user to automatically apply to jobs with the generated cover letter and resume.
- **Cover Letter Customization**: Allow the user to customize the cover letter for each job application.
- **Resume Customization**: Allow the user to customize the resume for each job application.
- **PDF Viewer**: Allow the user to view the generated PDF documents directly within the application.
- **Database Search**: Allow the user to search the database for previous resumes and cover letters.
- **User Authentication**: Allow the user to sign up for an account and log in to the application.
- **Resume and Cover Letter Storage**: Allow the user to store their resumes and cover letters in the database.
- **Resume and Cover Letter Sharing**: Allow the user to share their resumes and cover letters with others.
- **Resume and Cover Letter Printing**: Allow the user to print their resumes and cover letters.
