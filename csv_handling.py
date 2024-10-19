import os
import shutil


def organize_downloads(download_dir):
    downloaded_files = [f for f in os.listdir(
        download_dir) if os.path.isfile(os.path.join(download_dir, f))]

    date_str = ""
    for file_name in downloaded_files:
        base_name, _ = os.path.splitext(file_name)
        parts = base_name.split('_')
        if parts and len(parts[-1]) == 8 and parts[-1].isdigit():
            date_str = parts[-1]
            break

    if date_str:
        formatted_date = f"{date_str[0:2]}-{date_str[2:4]}-{date_str[4:]}"
        date_folder = os.path.join(download_dir, formatted_date)
        csv_folder = os.path.join(date_folder, "csv_folder")
        dat_folder = os.path.join(date_folder, "dat_folder")
        os.makedirs(csv_folder, exist_ok=True)
        os.makedirs(dat_folder, exist_ok=True)

        for file_name in downloaded_files:
            src_path = os.path.join(download_dir, file_name)
            if file_name.endswith(".csv"):
                shutil.move(src_path, os.path.join(csv_folder, file_name))
            elif file_name.endswith(".DAT"):
                shutil.move(src_path, os.path.join(dat_folder, file_name))
            else:
                shutil.move(src_path, os.path.join(date_folder, file_name))

        print(f"Files organized in {formatted_date} folder.")
    else:
        print("No valid date found in file names to create folders.")


if __name__ == "__main__":
    download_dir = "downloads"
    organize_downloads(download_dir)
