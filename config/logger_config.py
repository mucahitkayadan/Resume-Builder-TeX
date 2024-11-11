import logging
from config.settings import LOGGING_CONFIG

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def setup_logger(name):
    logger = logging.getLogger(name)
    
    if LOGGING_CONFIG['enabled']:
        logger.setLevel(LOGGING_CONFIG['level'])
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(LOGGING_CONFIG['format'])
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    else:
        logger.addHandler(NullHandler())
        logger.propagate = False
    
    return logger
