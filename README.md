# AI-Powered Resume Generator

## Project Overview

This project is an AI-powered resume generator that creates tailored resumes based on job descriptions. It uses OpenAI's language model to analyze job requirements and generate relevant content for each section of the resume. The system then compiles the resume into a professional LaTeX document and converts it to PDF.

## Features

- Job description analysis using AI
- Customized resume content generation
- LaTeX template-based resume formatting
- Automatic PDF compilation
- Organization of generated resumes in job-specific folders
- Parsing job descriptions from Indeed

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
├── tex_headers/
│   └── (LaTeX header files)
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

3. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

4. Ensure you have LaTeX installed on your system (for PDF compilation).

## Usage

1. Place your job description in `files/job_description.txt`.

2. Update your personal information in `files/information.json`.

3. Run the main script:
   ```bash
   python main.py
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
- LaTeX project for the document preparation system
