import logging
import os

# Folder and File Setup for Logs
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_FOLDER, "nse_activity_log.log")

# List to hold significant logs (warnings and errors) for potential email notifications
important_logs = []

# Logger Configuration
logger = logging.getLogger("nse_downloader")
logger.setLevel(logging.INFO)

# File handler to write logs to a file
file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setLevel(logging.INFO)

# Formatter to structure log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


# Custom Logging Functions
def info(message):
    """Log an info message."""
    logger.info(message)
    important_logs.append(("INFO", message)) 


def warning(message):
    """Log a warning message and save it for email notifications."""
    logger.warning(message)
    important_logs.append(("WARNING", message))


def error(message):
    """Log an error message and save it for email notifications."""
    logger.error(message)
    important_logs.append(("ERROR", message))
