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

## TODO List

### Core Functionality
1. **Easy Apply Integration**
   - Integrate LinkedIn Easy Apply functionality
   - Add support for other job platforms
   - Implement automated application tracking

2. **Resume Generation Controls**
   - Add configuration for section limits:
     - Maximum number of projects (default: 4)
     - Maximum bullet points per project (default: 4)
     - Maximum bullet points per job (default: 5)
     - Skills per category limits (min: 3, max: 8)
   - Implement priority-based content selection
   - Add content scoring system

3. **API Development**
   - Create RESTful API endpoints:
     - `/api/v1/resume` - Resume generation
     - `/api/v1/cover-letter` - Cover letter generation
     - `/api/v1/portfolio` - Portfolio management
   - Add API documentation using Swagger/OpenAPI
   - Implement authentication and rate limiting

4. **UI Improvements**
   - Add real-time PDF preview
   - Implement drag-and-drop section reordering
   - Add progress indicators for generation steps
   - Improve error messaging and validation
   - Add user settings panel

5. **Database and Storage**
   - Add JSON import/export for templates
   - Support multiple storage backends:
     - MongoDB (current)
     - JSON files (for end users)
     - SQL databases
   - Add template version control
   - Implement backup/restore functionality

6. **User Experience**
   - Add warning messages about MongoDB migration
   - Improve template management interface
   - Add template preview functionality
   - Implement user preferences storage

7. **Documentation**
   - Add detailed API documentation
   - Create user guide for template customization
   - Document MongoDB schema
   - Add deployment guides

8. **Testing and Quality**
   - Add unit tests for core components
   - Implement integration tests
   - Add performance benchmarks
   - Improve error handling and logging

### Technical Debt
1. Clean up duplicate code in generators
2. Improve error handling in LaTeX compilation
3. Standardize logging format
4. Optimize database queries
5. Refactor template management

### Future Features
1. Multi-language support
2. AI-powered job matching
3. Resume version control
4. Analytics dashboard
5. Batch processing capabilities


[![](https://mermaid.ink/img/pako:eNq9WFtv2zYU_isC9-I1dhA7cRILQYAuBXZBug1tn1YbAi0dO0ok0iCpNl6W_75DSbZJipKdtogfJIr8yHO_0E8k5gmQkMQZlfJdSpeC5lMW4K-cCT6ALHK4EUAVF8FTtaR_A1EwBiIM3rK1MXsvOYsyThO99Ad-3JZjA7ESPF-pLebv8rOBSuZRThldasg7quicSnhfTRiojC9LxG35NhYUPG4pfILHxvF3VCRaclz-rR5-hFilnMkd6mgJKCFVEIlSC717Po8SkLFIVxoaBlKJfhCjAJStI0ZzqKc0UKUq23zneH4WqfXKnjB2KMhXmlYhcGaBrKt-ICFDniCJZM0aqiKN1edyAz5mPwdh8GvFIxefPxWrDKrF8oBZP_iTM6ieM0P4WFsTIl6oVaGiJBV4PBfr3l5BND18efS4YbFXv_fB6VccyV4HYlXMszSmpdw27nnKTA-94V9A3IJSIF7fTVsd8CD_3TlYrIWIslKKFjerfDBKkzBImTrA7bqU9guy86HUjKmsqys6xx00VtfXu9mfSmd1NHiE-olByq3hK33VjCQoscGTK0zD7NvTMAbQGDSLUrbgIqfNoy2EGRDI3uyl5GIqAPWOis0pBoBFyF77XkryIc0yaVOo5syTb1NZjmYvPv8rFw8RPKJ2UmAx2IScxbCiYwv0YoqQFLHHPtvpH0MF3_foYY7mNrPfR6POgwueYVCXcWRT2XuKE1R_rYC9_b0ZVj8uVtzUl9EigVck6NZKK9Puz6l7qvLRt1YTb9bowDth31XWqrDtQLiB1wHdRUyXLBuHf53q6dQmy6AxZ6j6G3xWZrAKl0JOgebzDHq6d8l0JNW1qRlpKZMg1KaNOqBhauu0mAKmW5ZYub0QJoVkEdWIMJivFchva7w0-yiFI23Nu12FNdROPsauYpU0SnuziO8Wd8xXOa4hjqamezmvIXcBZ9mwCvZWHks7tkVP5y5PDHXijUjy1TsH7YsqX6p3ttkRdsAGK9oOwBuRd8jpbhS273Gsabablj2rTN64CRxg0qja2swaHnN2YytTdmMcA3aDt2brhm2M1Y2qTLTnJMMwe_RiBqgP6RhuW9bsKDzoNiDpQncj2l7RJqfukquRs968eUAhl9LPiH1lHwyujW6_DeGW6yaieQFqYryiNWFO6W8C_Fdyz0XPJ1wLzJWwBdYUswXoldW4Vl39NxhYHaEfYbZwFaLRY_m494Icve5c0cMv6ZMc0NPShISkdNUpUXeQw5SEOEyoeJiSKXtGHC0U_7hmMQmVKKBPBC-WdyRc0EziV1Xl6n-ONhBIUtTT-_qvJf3qEyz5_3C-heAnCZ_IIwnH4-PR-eXkYngyOhsNLy9O-2RNwuFkeDw8HZ2dDUeX56ej88nouU_-LQ84OZ5cTs5PLsajs_HFGe4cP_8P7DU5ww?type=png)](https://mermaid.live/edit#pako:eNq9WFtv2zYU_isC9-I1dhA7cRILQYAuBXZBug1tn1YbAi0dO0ok0iCpNl6W_75DSbZJipKdtogfJIr8yHO_0E8k5gmQkMQZlfJdSpeC5lMW4K-cCT6ALHK4EUAVF8FTtaR_A1EwBiIM3rK1MXsvOYsyThO99Ad-3JZjA7ESPF-pLebv8rOBSuZRThldasg7quicSnhfTRiojC9LxG35NhYUPG4pfILHxvF3VCRaclz-rR5-hFilnMkd6mgJKCFVEIlSC717Po8SkLFIVxoaBlKJfhCjAJStI0ZzqKc0UKUq23zneH4WqfXKnjB2KMhXmlYhcGaBrKt-ICFDniCJZM0aqiKN1edyAz5mPwdh8GvFIxefPxWrDKrF8oBZP_iTM6ieM0P4WFsTIl6oVaGiJBV4PBfr3l5BND18efS4YbFXv_fB6VccyV4HYlXMszSmpdw27nnKTA-94V9A3IJSIF7fTVsd8CD_3TlYrIWIslKKFjerfDBKkzBImTrA7bqU9guy86HUjKmsqys6xx00VtfXu9mfSmd1NHiE-olByq3hK33VjCQoscGTK0zD7NvTMAbQGDSLUrbgIqfNoy2EGRDI3uyl5GIqAPWOis0pBoBFyF77XkryIc0yaVOo5syTb1NZjmYvPv8rFw8RPKJ2UmAx2IScxbCiYwv0YoqQFLHHPtvpH0MF3_foYY7mNrPfR6POgwueYVCXcWRT2XuKE1R_rYC9_b0ZVj8uVtzUl9EigVck6NZKK9Puz6l7qvLRt1YTb9bowDth31XWqrDtQLiB1wHdRUyXLBuHf53q6dQmy6AxZ6j6G3xWZrAKl0JOgebzDHq6d8l0JNW1qRlpKZMg1KaNOqBhauu0mAKmW5ZYub0QJoVkEdWIMJivFchva7w0-yiFI23Nu12FNdROPsauYpU0SnuziO8Wd8xXOa4hjqamezmvIXcBZ9mwCvZWHks7tkVP5y5PDHXijUjy1TsH7YsqX6p3ttkRdsAGK9oOwBuRd8jpbhS273Gsabablj2rTN64CRxg0qja2swaHnN2YytTdmMcA3aDt2brhm2M1Y2qTLTnJMMwe_RiBqgP6RhuW9bsKDzoNiDpQncj2l7RJqfukquRs968eUAhl9LPiH1lHwyujW6_DeGW6yaieQFqYryiNWFO6W8C_Fdyz0XPJ1wLzJWwBdYUswXoldW4Vl39NxhYHaEfYbZwFaLRY_m494Icve5c0cMv6ZMc0NPShISkdNUpUXeQw5SEOEyoeJiSKXtGHC0U_7hmMQmVKKBPBC-WdyRc0EziV1Xl6n-ONhBIUtTT-_qvJf3qEyz5_3C-heAnCZ_IIwnH4-PR-eXkYngyOhsNLy9O-2RNwuFkeDw8HZ2dDUeX56ej88nouU_-LQ84OZ5cTs5PLsajs_HFGe4cP_8P7DU5ww)

[![](https://mermaid.ink/img/pako:eNp1lG9v2jAQxr-K5de0AgYh5MUmyp-WjnaUMGmbqSo3uZZsiR3ZzjYKfPddbAep3cYLlLN_d_f48SV7msgUaESfcvkr2XJlyHqyEQR_IxYbjO_J2dl7csE-a1AkE2VlNPkuH0kKOlFZaTIp7l3ChSXHbC4yk_E8ewGyAl0VMFbAjVQeG1tswhaSp6QEpaXgOVZ-kqrgdTnCBW4oWZRG-5yJzZnuL0GA4gaIsoWJhqTO0EeHTS12mElFgCfbZvtAZvvYPRKzK-GDx2cOv-IqrV04kMv6lKSJfUqjwdNLJRPQ-kCuLDyak1UlUJWnLi01Z6M0JUaSRAoDwpA0s7W42nnuynEumNvgej_K89ORagfqRpA2cq-dgFt5INNXK18B5Xxk1mYgsjJ4SdhRYSV5avjRsgt2snDB1_ClEeihhYVu2BjNz_KGwXMsJzOP3FjklsX85-kaEEi54Y9cg6duLfWJTUWKK25NV4_Pipdb9OzBefbgzXT7S7ZUUHIF_vJ9qTsWg7BmotcF3kvuN1bMp9cbqKRE15r-S9v_zv6v3BIWaZQ48_8h443Qt5PwWm_sRthfmHXAd1-zmR1mu4ajjdqtk347tu3Xf8lys_O_prRFC8CqWYqv677O2FCzhQI2NMLHlKsfG7oRR-R4ZWS8EwmNjKqgRZWsnrc0euK5xqgqURZMMo6HLBoE0gyH5cZ9DOw3oUVLLr5JeUIwpNGe_qZRPzhvB52w3RkOgmF_0O626I5G3fbwvNfr9zphbxD2gqAdHlv0xRZonw87QW_4rtsNB2E37Ab94x-skmsZ?type=png)](https://mermaid.live/edit#pako:eNp1lG9v2jAQxr-K5de0AgYh5MUmyp-WjnaUMGmbqSo3uZZsiR3ZzjYKfPddbAep3cYLlLN_d_f48SV7msgUaESfcvkr2XJlyHqyEQR_IxYbjO_J2dl7csE-a1AkE2VlNPkuH0kKOlFZaTIp7l3ChSXHbC4yk_E8ewGyAl0VMFbAjVQeG1tswhaSp6QEpaXgOVZ-kqrgdTnCBW4oWZRG-5yJzZnuL0GA4gaIsoWJhqTO0EeHTS12mElFgCfbZvtAZvvYPRKzK-GDx2cOv-IqrV04kMv6lKSJfUqjwdNLJRPQ-kCuLDyak1UlUJWnLi01Z6M0JUaSRAoDwpA0s7W42nnuynEumNvgej_K89ORagfqRpA2cq-dgFt5INNXK18B5Xxk1mYgsjJ4SdhRYSV5avjRsgt2snDB1_ClEeihhYVu2BjNz_KGwXMsJzOP3FjklsX85-kaEEi54Y9cg6duLfWJTUWKK25NV4_Pipdb9OzBefbgzXT7S7ZUUHIF_vJ9qTsWg7BmotcF3kvuN1bMp9cbqKRE15r-S9v_zv6v3BIWaZQ48_8h443Qt5PwWm_sRthfmHXAd1-zmR1mu4ajjdqtk347tu3Xf8lys_O_prRFC8CqWYqv677O2FCzhQI2NMLHlKsfG7oRR-R4ZWS8EwmNjKqgRZWsnrc0euK5xqgqURZMMo6HLBoE0gyH5cZ9DOw3oUVLLr5JeUIwpNGe_qZRPzhvB52w3RkOgmF_0O626I5G3fbwvNfr9zphbxD2gqAdHlv0xRZonw87QW_4rtsNB2E37Ab94x-skmsZ)