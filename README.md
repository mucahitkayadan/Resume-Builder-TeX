# AI-Powered Resume and Cover Letter Generator

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Docker Setup](#docker-setup)
- [Usage](#usage)
- [Parsing Indeed Job Descriptions](#parsing-indeed-job-descriptions)
- [Key Components](#key-components)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [TODO](#todo)

## Project Overview

The AI-Powered Resume and Cover Letter Generator is a sophisticated tool designed to automate the creation of professional resumes and cover letters. By leveraging OpenAI's and Anthropic's language models, this project analyzes job descriptions to generate tailored content for each section of a resume and cover letter. The system then compiles the resume into a LaTeX document and converts it to a PDF, ensuring a polished and professional presentation.

## Features

- **AI-Driven Content Generation**: Utilizes AI to analyze job descriptions and generate customized resume and cover letter content.
- **LaTeX Formatting**: Employs LaTeX templates for high-quality document formatting.
- **PDF Compilation**: Converts LaTeX documents into PDF format for easy sharing and printing.
- **Job-Specific Organization**: Automatically organizes generated documents into job-specific folders.
- **Indeed Job Description Parsing**: Directly parses job descriptions from Indeed to streamline the input process.
- **Docker Support**: Easily deploy and run the application using Docker.

## Project Structure

```
project_root/
│
├── main.py
├── engine/
│   └── process_section.py
├── loaders/
│   ├── tex_loader.py
│   ├── json_loader.py
│   ├── prompt_loader.py
│   └── job_description_loader.py
├── parsers/
│   └── indeed_parser.py
├── utils/
│   └── utils.py
├── tex_template/
│   └── (LaTeX template files)
├── prompts/
│   └── (System prompts for AI)
├── files/
│   ├── job_description.txt
│   └── information.json
└── created_resumes/
    └── (Output folders for generated resumes)
```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mucahitkayadan/Resume-Builder-TeX.git
   cd Resume-Builder-TeX
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     ```

4. Ensure you have LaTeX installed on your system (for PDF compilation).

## Docker Setup

1. Ensure Docker is installed on your system.

2. Build the Docker image:
   ```bash
   docker build -t resume-generator .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 8501:8501 --env-file .env resume-generator
   ```

   This command uses the environment variables from your `.env` file.

4. Access the application by opening a web browser and navigating to `http://localhost:8501`.

## Usage

1. Place your job description in `files/job_description.txt`.

2. Update your personal information in `files/information.json`.

3. Run the main script:
   ```bash
   python main_easy_applier.py
   ```
   Or, if using Docker:
   ```bash
   docker run -p 8501:8501 --env-file .env resume-generator
   ```

4. The generated resume will be saved in a new folder under `created_resumes/`, named after the company and position.

## Parsing Indeed Job Descriptions

To parse job descriptions from Indeed, use the `indeed_parser.py` script:

1. Update the URL in the script to the Indeed job listing you want to parse.
2. Run the script:
   ```bash
   python parsers/indeed_parser.py
   ```

## Key Components

### main.py

The entry point of the application. It orchestrates the entire process of resume generation.

### engine/process_section.py

Contains the `OpenAIRunner` class, which interfaces with the OpenAI API to generate content for each resume section.

### loaders/

- `tex_loader.py`: Loads LaTeX templates
- `json_loader.py`: Loads personal information from JSON
- `prompt_loader.py`: Loads system prompts for AI
- `job_description_loader.py`: Loads and processes job descriptions

### parsers/indeed_parser.py

Contains the `parse_indeed_job` function, which fetches and parses job descriptions from Indeed job listings.

### utils/utils.py

Contains utility functions for file operations, LaTeX compilation, etc.

## Customization

- Modify LaTeX templates in `tex_template/` to change the resume format.
- Update system prompts in `prompts/` to adjust AI behavior.
- Edit `files/information.json` to update your personal information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT model
- Anthropic for providing the Claude model
- LaTeX project for the document preparation system

## LaTeX Templates

LaTeX templates are now stored in the database. To modify a template:

1. Use the DatabaseManager to retrieve the template
2. Make your modifications
3. Use the DatabaseManager to update the template in the database

## TexLoader

The TexLoader class now loads LaTeX templates from the database instead of from files. It uses the DatabaseManager to retrieve templates.

## TODO

### Upcoming Features
1. **LinkedIn Easy Apply Integration**
   - Automated job application process
   - Application tracking
   - Multi-platform support

2. **Resume Generation Controls**
   - Configurable section limits
   - Smart content selection
   - Template customization

3. **API and Integration**
   - RESTful API endpoints
   - Documentation
   - Authentication

4. **UI Enhancements**
   - Real-time PDF preview
   - Better progress indicators
   - Improved user settings

5. **Storage Options**
   - JSON template support
   - Multiple database options
   - Template management

6. **Documentation**
   - API guides
   - Template customization
   - Deployment instructions

For technical details and implementation plans, see TECHNICAL.md.
