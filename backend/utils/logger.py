import logging
import os
from datetime import datetime

def setup_logger(name="outreach_logger", log_file="outreach.log"):
    """
    Sets up a logger that writes to console and a file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # File Handler
    # Ensure logs directory exists if we put it in a subdir, but here just root or backend root
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger

# Singleton instance
logger = setup_logger()
