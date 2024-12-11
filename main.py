from src.ui.streamlit_app import StreamlitApp
from config.logger_config import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Starting Streamlit application")
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()

