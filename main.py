from config.logger_config import setup_logger
from src.ui.streamlit_app import StreamlitApp

# Set up root logger
logger = setup_logger(__name__)

def main():
    logger.info("Starting application")
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()

