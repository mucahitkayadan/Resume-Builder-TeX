import logging
from config import LOG_LEVEL, LOGGING_ENABLED

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def setup_logger(name):
    logger = logging.getLogger(name)
    
    if LOGGING_ENABLED:
        logger.setLevel(LOG_LEVEL)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    else:
        logger.addHandler(NullHandler())
        logger.propagate = False
    
    return logger
