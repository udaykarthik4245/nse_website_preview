import os
import shutil
from datetime import datetime

def organize_files(download_dir):
    date_folder_name = datetime.now().strftime("%d-%m-%Y")
    date_folder_path = os.path.join(download_dir, date_folder_name)
    os.makedirs(date_folder_path, exist_ok=True)


    csv_folder = os.path.join(date_folder_path, 'csv_folder')
    dat_folder = os.path.join(date_folder_path, 'dat_folder')
    os.makedirs(csv_folder, exist_ok=True)
    os.makedirs(dat_folder, exist_ok=True)

    for file_name in os.listdir(download_dir):
        if file_name.endswith('.csv'):
            shutil.move(os.path.join(download_dir, file_name), os.path.join(csv_folder, file_name))
        elif file_name.endswith('.DAT'):
            shutil.move(os.path.join(download_dir, file_name), os.path.join(dat_folder, file_name))
        elif file_name.endswith('.zip'):
            pass
        else:
            shutil.move(os.path.join(download_dir, file_name), os.path.join(date_folder_path, file_name))

if __name__ == "__main__":
    download_dir = "downloads"
    organize_files(download_dir)
