import logging
from src.ui.streamlit_app import StreamlitApp
from src.loaders.prompt_loader import PromptLoader

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )

def main():

    app = StreamlitApp()
    app.run()
    # from config.settings import PROMPTS_FOLDER
    # prompt_loader = PromptLoader()
    # print(f"Resolved PROMPTS_FOLDER: {PROMPTS_FOLDER}")
    # print(prompt_loader.get_section_prompt('career_summary'))

if __name__ == "__main__":
    main()

