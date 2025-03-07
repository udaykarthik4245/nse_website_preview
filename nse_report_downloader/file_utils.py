import os
import zipfile
import shutil
from datetime import datetime


DOWNLOAD_FOLDER = "downloads"

def get_next_zip_name(base_name):
    """Generate a unique ZIP name if a file with the same name exists."""
    today = datetime.now().strftime("%Y-%m-%d")
    zip_name = f"{base_name}_{today}.zip"
    counter = 1

    while os.path.exists(os.path.join(DOWNLOAD_FOLDER, zip_name)):
        zip_name = f"{base_name}_{today}_{counter}.zip"
        counter += 1

    return zip_name

def is_zip_already_downloaded():
    """Check if a ZIP file already exists."""
    today = datetime.now().strftime("%Y-%m-%d")
    return any(file.startswith(f'merged_reports_{today}') for file in os.listdir(DOWNLOAD_FOLDER))

def handle_downloaded_zip(zip_file_path, zipf):
    """Extract the contents of a downloaded ZIP file and add them to the merged ZIP."""
    temp_dir = os.path.join(DOWNLOAD_FOLDER, "temp_extracted")

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith('.csv'):
                    add_to_sub_zip(zipf, file_path, 'Reports(.csv)')
                elif file.lower().endswith('.dat'):
                    add_to_sub_zip(zipf, file_path, 'Reports(.dat)')
                else:
                    add_to_sub_zip(zipf, file_path)
    except zipfile.BadZipFile:
        print(f"Failed to unzip {zip_file_path}. The file may be corrupted.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.remove(zip_file_path)

def add_to_sub_zip(zipf, file_path, folder_name=None):
    """Add a file to the ZIP, renaming it if a duplicate exists."""
    original_arcname = os.path.basename(file_path)
    arcname = os.path.join(folder_name, original_arcname) if folder_name else original_arcname

    # Check for duplicate names in the ZIP
    counter = 1
    while arcname in zipf.namelist():
        # If duplicate, append a counter to the filename
        name, ext = os.path.splitext(original_arcname)
        arcname = os.path.join(folder_name, f"{name}_{counter}{ext}") if folder_name else f"{name}_{counter}{ext}"
        counter += 1

    zipf.write(file_path, arcname)
    os.remove(file_path)
