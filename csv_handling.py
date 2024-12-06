

import os
import zipfile
import shutil
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Base download folder
BASE_DOWNLOAD_FOLDER = "C:\\Users\\udayk\\Downloads\\project_nse_inf\\downloads"

# Get the current date and time
now = datetime.now()
# Determine if it’s past 7 AM; if yes, use today's date; otherwise, use yesterday's date
today_date = (now - timedelta(days=1)).strftime("%Y-%m-%d") if now.hour < 7 else now.strftime("%Y-%m-%d")
date_folder = os.path.join(BASE_DOWNLOAD_FOLDER, today_date)

# Create the date-based folder if it does not exist
os.makedirs(date_folder, exist_ok=True)


def file_exists_in_subfolder(file_name):
    """Check if a file already exists in the respective subfolders."""
    subfolders = ['Reports(.csv)', 'Reports(.dat)', 'Other_Files']
    for folder in subfolders:
        target_folder = os.path.join(date_folder, folder)
        if os.path.exists(os.path.join(target_folder, file_name)):
            return True
    return False


def move_file_to_folder(file_path):
    """Move files to respective folders based on their file type."""
    file_name = os.path.basename(file_path)

    # Check if the file already exists in the subfolders
    if file_exists_in_subfolder(file_name):
        logging.info(f"Skipping moving for: {file_name} (already exists in subfolder)")
        try:
            os.remove(file_path)  # Remove the file from downloads folder
            logging.info(f"Removed duplicate file: {file_name} from downloads.")
        except OSError as e:
            logging.error(f"Error removing file {file_name}: {e}")
        return

    # Determine the target folder based on file extension
    if file_path.endswith('.csv') or file_path.endswith('.CSV'):
        target_folder = os.path.join(date_folder, 'Reports(.csv)')
    elif file_path.endswith('.dat') or file_path.endswith('.DAT'):
        target_folder = os.path.join(date_folder, 'Reports(.dat)')
    else:
        target_folder = os.path.join(date_folder, 'Other_Files')

    # Ensure the target folder exists
    os.makedirs(target_folder, exist_ok=True)

    # Move the file to the target folder
    try:
        shutil.move(file_path, os.path.join(target_folder, file_name))
        logging.info(f"Moved file: {file_name} to {target_folder}.")
    except (shutil.Error, OSError) as e:
        logging.error(f"Error moving file {file_name} to {target_folder}: {e}")


def sort_downloaded_files():
    """Sort files in the BASE_DOWNLOAD_FOLDER into respective type folders within today's folder."""
    if datetime.now().weekday() in [5, 6]:  # Check if today is Saturday (5) or Sunday (6)
        logging.info("Today is a non-working day (Saturday or Sunday). No files to download.")
        return

    try:
        for file_name in os.listdir(BASE_DOWNLOAD_FOLDER):
            file_path = os.path.join(BASE_DOWNLOAD_FOLDER, file_name)

            # Skip directories and the date folder itself
            if os.path.isfile(file_path):
                move_file_to_folder(file_path)
    except Exception as e:
        logging.error(f"Error sorting downloaded files: {e}")


def create_zip_in_date_folder():
    """Create a ZIP file within the date folder, containing its organized subfolders."""
    zip_name = f"merged_reports_{today_date}.zip"
    zip_path = os.path.join(date_folder, zip_name)  # Save ZIP in the date folder

    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(date_folder):
                for file in files:
                    # Skip adding the ZIP file itself to avoid nesting
                    if file == zip_name:
                        continue

                    file_path = os.path.join(root, file)

                    # Ensure ZIP structure only includes relative paths from the date folder
                    arcname = os.path.relpath(file_path, date_folder)
                    zipf.write(file_path, arcname)
        logging.info(f"Created ZIP file: {zip_path}.")
    except Exception as e:
        logging.error(f"Error creating ZIP file: {e}")


# Run the sorting function after downloading files
sort_downloaded_files()

# Create the ZIP archive inside the date folder
create_zip_in_date_folder()
