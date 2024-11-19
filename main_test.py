import logging
from src.ui.streamlit_app import StreamlitApp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():

    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()

