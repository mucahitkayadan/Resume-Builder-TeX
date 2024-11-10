from typing import Optional, Dict
import streamlit as st
from utils.document_utils import check_clearance_requirement, get_or_create_folder_name
from loaders.prompt_loader import PromptLoader
from engine.runners import AIRunner
from engine.resume_creator import ResumeCreator
from engine.cover_letter_creator import CoverLetterCreator
from utils.logger_config import setup_logger
from utils.view_database import view_database

from engine.ai_strategies import OpenAIStrategy, ClaudeStrategy, OllamaStrategy
import traceback
from core.database.factory import get_unit_of_work

# Configure logging
logger = setup_logger(__name__)


def get_user_section_selection() -> Dict[str, str]:
    sections = [
        "personal_information", "career_summary", "skills", "work_experience",
        "education", "projects", "awards", "publications"
    ]
    options = ["Process", "Hardcode", "Skip"]
    selected_sections = {}

    st.subheader("Section Handling")

    # Create column headers
    col1, col2 = st.columns([2, 3])
    col1.write("**Section**")
    col2.write("**Action**")

    # Create rows for each section
    for section in sections:
        col1, col2 = st.columns([2, 3])
        col1.write(section.replace("_", " ").title())

        # Create radio buttons for each option
        selected_option = col2.radio(
            f"Select action for {section}",  # Provide a meaningful label
            options,
            index=0,  # Default to "Process"
            key=f"section_{section}",
            label_visibility="collapsed",
            horizontal=True
        )

        selected_sections[section] = selected_option.lower()

    return selected_sections


def main() -> None:
    """
    Main function to run the Resume and Cover Letter Generator application.

    This function sets up the Streamlit interface, handles user inputs,
    and orchestrates the generation of resumes and cover letters based on
    the user's selections.
    """
    # Initialize session state variables
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = "mujakayadan"
        
    if 'portfolio_initialized' not in st.session_state:
        st.session_state['portfolio_initialized'] = False

    logger.info("Starting Resume and Cover Letter Generator")
    st.title("Resume and Cover Letter Generator")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Resume Generator", "Database Viewer"])

    if page == "Resume Generator":
        # Initialize unit of work
        uow = get_unit_of_work()

        # Get job description from user
        job_description: str = st.text_area("Enter the job description:", height=200)

        # Check for clearance requirement
        clearance_required: bool = check_clearance_requirement(job_description)

        # Add model selection
        model_type: str = st.selectbox("Select AI model type:", ["OpenAI", "Claude", "Ollama"])
        if model_type == "OpenAI":
            model_name: str = st.selectbox("Select OpenAI model:",
                                           ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini",
                                            "gpt-4o-2024-05-13"])
        elif model_type == "Claude":
            model_name: str = st.selectbox("Select Claude model:", ["claude-3-5-sonnet-latest", "claude-3-opus-latest",
                                                                    "claude-3-5-sonnet-20241022",
                                                                    "claude-3-5-sonnet-20240620",
                                                                    "claude-3-opus-20240229",
                                                                    "claude-3-sonnet-20240229"])
        else:
            model_name: str = st.selectbox("Select Ollama model:", ["llama3.1", "llama2", "llama2-uncensored", "mistral", 
                                                                   "mixtral", "codellama", "neural-chat"])

        # Add temperature slider
        temperature: float = st.slider("Set temperature:", min_value=0.0, max_value=1.0, value=0.1, step=0.1)

        # Initialize common components
        prompt_loader: PromptLoader = PromptLoader('prompts/')
        system_prompt: str = prompt_loader.get_system_prompt()

        # Create AIRunner with the selected strategy
        if model_type == "OpenAI":
            ai_strategy = OpenAIStrategy(system_prompt)
        elif model_type == "Claude":
            ai_strategy = ClaudeStrategy(system_prompt)
        else:
            ai_strategy = OllamaStrategy(system_prompt)

        # Set the temperature using the setter
        ai_strategy.temperature = temperature
        ai_strategy.model = model_name
        ai_runner = AIRunner(ai_strategy)

        # Make sure there's no direct access to ai_runner.model
        # If found, replace it with ai_runner.get_model_name()

        resume_creator = ResumeCreator(ai_runner, prompt_loader, uow)

        selected_sections = get_user_section_selection()

        generation_option: str = st.selectbox("Choose generation option", ["Resume", "Cover Letter", "Both"])

        if st.button("Generate"):
            if clearance_required:
                st.error(
                    "This job requires a security clearance or US citizenship. Resume generation is not available for this job.")
            else:
                progress_bar = st.progress(0)
                status_area = st.empty()
                resume_id: Optional[str] = None
                generation_completed: bool = False

                # Extract company name and job title from job description
                company_name: str
                job_title: str
                company_name, job_title = get_or_create_folder_name(job_description, ai_runner, prompt_loader)

                if generation_option in ["Resume", "Both"]:
                    try:
                        for update, progress in resume_creator.generate_resume(
                                job_description,
                                company_name,
                                job_title,
                                model_type,
                                model_name,
                                temperature,
                                selected_sections,
                                st.session_state.user_id
                        ):
                            progress_bar.progress(progress * 0.5 if generation_option == "Both" else progress)
                            status_area.info(update)

                        latest_resume = uow.resumes.get_latest_resume()
                        resume_id = str(latest_resume.id) if latest_resume else None
                        generation_completed = True
                    except UnicodeEncodeError as e:
                        st.error(f"Error encoding characters: {str(e)}")
                        logger.error(f"UnicodeEncodeError in generate_resume: {str(e)}")
                        logger.error(f"Error position: {e.start}-{e.end}")
                        logger.error(f"Problematic string: {e.object[max(0, e.start - 10):e.end + 10]}")
                        logger.error(f"Full traceback: {traceback.format_exc()}")
                        resume_id = None
                    except Exception as e:
                        st.error(f"Error generating resume: {str(e)}")
                        logger.error(f"Error in generate_resume: {str(e)}")
                        logger.error(f"Full traceback: {traceback.format_exc()}")
                        resume_id = None

                if generation_option in ["Cover Letter", "Both"]:
                    if resume_id is None and generation_option == "Both":
                        st.error("Failed to generate resume. Cannot proceed with cover letter generation.")
                    elif resume_id is None:
                        st.error("Please generate a resume first.")
                    else:
                        try:
                            cover_letter_creator: CoverLetterCreator = CoverLetterCreator(ai_runner, prompt_loader, uow)
                            cover_letter_result: str = cover_letter_creator.generate_cover_letter(
                                job_description,
                                resume_id,
                                company_name,
                                job_title
                            )
                            st.write(cover_letter_result)
                            progress_bar.progress(1.0)
                            status_area.info("Cover letter generated successfully")
                            generation_completed = True
                        except Exception as e:
                            st.error(f"Error generating cover letter: {str(e)}")

                if generation_completed:
                    st.success("Generation completed!")
                else:
                    st.warning("Generation was not completed due to errors.")
    elif page == "Database Viewer":
        view_database()


if __name__ == "__main__":
    main()