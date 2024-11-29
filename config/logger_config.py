import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Set the log level for the logger
    logger.setLevel(level)
    
    # Create console handler with formatting
    handler = logging.StreamHandler()
    # Set the handler's level to DEBUG as well
    handler.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
