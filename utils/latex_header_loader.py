import os
import logging
from utils.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

def load_latex_headers(db_manager):
    try:
        with open('tex_headers/preamble.tex', 'r') as file:
            content = file.read()
            db_manager.insert_preamble(content)
            logger.info("Successfully loaded and inserted preamble")
    except Exception as e:
        logger.error(f"Error loading preamble: {str(e)}")
