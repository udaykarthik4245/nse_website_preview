import streamlit as st
import os
import time
import zipfile
import shutil
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from mail import send_email_report

# Constants
BASE_DOWNLOAD_FOLDER = "downloads"
LOG_FILE_PATH = "download_logs.txt"
CHROME_DRIVER_PATH = "C:\\Users\\udayk\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# Configure logging
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# App Header and Title
st.set_page_config(page_title="NSE Report Downloader", layout="wide", initial_sidebar_state="expanded")

# Centered title and description
st.markdown("<div style='text-align: center;'><h1>📈 NSE Downloader</h1></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'>Automate downloading and processing reports from NSE</div>", unsafe_allow_html=True)

# Theme Options
st.sidebar.header("Settings")
Theme = st.sidebar.selectbox("Choose a theme", ["Default", "Dark", "Light"])

# CSS for Themes
light_css = """
<style>
    .stApp { background-color: white; color: black; }
    h1, h3, h4, h5, h6 { color: black; }
    h2 { color: red; }
</style>
"""
dark_css = """
<style>
    .stApp { background-color: #1e1e1e; color: white; }
    h1, h2, h3, h4, h5, h6 { color: white; }
</style>
"""

# Apply Theme
if Theme == "Light":
    st.markdown(light_css, unsafe_allow_html=True)
else:
    st.markdown(dark_css, unsafe_allow_html=True)
# ----------------------------------------------------------------------------------------------------------------------------




# Functions for Core Functionality
def setup_driver(download_directory):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent = your user agent")
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return driver

def is_download_complete(file_name, download_dir):
    file_path = os.path.join(download_dir, file_name)
    return os.path.exists(file_path) and not file_name.endswith(".crdownload")

def download_report(driver, data_link, file_name, download_dir):
    retry_count = 0
    while retry_count < 3:
        try:
            driver.get(data_link)
            time.sleep(5)
            if is_download_complete(file_name, download_dir):
                logging.info(f"Download completed: {file_name}")
                break
            else:
                retry_count += 1
                time.sleep(2)
        except WebDriverException as e:
            logging.error(f"Failed to download {file_name}: {e}")
            retry_count += 1

def download_reports(download_directory):
    driver = setup_driver(download_directory)
    files_attempted = 0
    successful_downloads = 0
    failed_downloads = 0
    try:
        driver.get("https://www.nseindia.com/all-reports")
        time.sleep(10)
        report_div = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@id='cr_equity_daily_Current']")))
        report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")
        for report in report_divs:
            data_link = report.get_attribute("data-link")
            file_name = data_link.split("/")[-1]
            files_attempted += 1
            try:
                download_report(driver, data_link, file_name, download_directory)
                successful_downloads += 1
            except Exception as e:
                logging.error(f"Failed to download {file_name}: {e}")
                failed_downloads += 1
    finally:
        driver.quit()
    
    return files_attempted, successful_downloads, failed_downloads


def organize_and_zip_files(download_dir, date_folder):
    subfolders = {'csv': 'Reports(.csv)', 'dat': 'Reports(.dat)', 'others': 'Other_Files'}
    for file_name in os.listdir(download_dir):
        file_path = os.path.join(download_dir, file_name)
        if os.path.isfile(file_path):
            if file_name.endswith('.csv') or file_name.endswith('.CSV'):
                target_folder = os.path.join(date_folder, subfolders['csv'])
            elif file_name.endswith('.dat') or file_name.endswith('.DAT'):
                target_folder = os.path.join(date_folder, subfolders['dat'])
            else:
                target_folder = os.path.join(date_folder, subfolders['others'])
            os.makedirs(target_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(target_folder, file_name))
            logging.info(f"Moved {file_name} to {target_folder}.")

    zip_file_path = os.path.join(date_folder, f"nse_reports_{datetime.now().strftime('%Y-%m-%d')}.zip")
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(date_folder):
            for file in files:
                if file != zip_file_path:
                    zipf.write(os.path.join(root, file), arcname=file)
    return zip_file_path

# Logging and Retry Functionality (Second Code Block)
def log_event(event_description):
    with open("logs.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {event_description}\n"
        log_file.write(log_entry)
    print(event_description)

# Main Page - Download Section
page = st.sidebar.radio("Navigate", ["Download", "Logs"])
if page == "Download":
    st.markdown("<div style='text-align: center;'><h2>📥 Download Reports</h2></div>", unsafe_allow_html=True)
    
    # Adding a unique key to the text_input
    download_path = st.text_input("Download path", value=os.getcwd(), key="download_path_input")
    
    if st.button("Start Downloading and Organizing"):
        with st.spinner("Downloading reports..."):
            temp_download_dir = os.path.join(download_path, "temp_downloads")
            os.makedirs(temp_download_dir, exist_ok=True)

            # Track download statistics
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            files_attempted, successful_downloads, failed_downloads = download_reports(temp_download_dir)
            
            # Organize and zip files
            today_folder = os.path.join(download_path, datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(today_folder, exist_ok=True)
            zip_path = organize_and_zip_files(temp_download_dir, today_folder)
            shutil.rmtree(temp_download_dir)
            
            # Calculate time taken
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_taken = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

            # Send email after download
            recipient_email = "recipient@example.com"  # Replace with actual recipient email
            send_email_report(recipient_email, start_time, end_time, str(time_taken), files_attempted, successful_downloads, failed_downloads, LOG_FILE_PATH)

        st.success(f"Downloaded and zipped files successfully! Zip file path: {zip_path}")

# Logs Section
elif page == "Logs":
    st.markdown("<div style='text-align: center;'><h2>📄 Logs</h2></div>", unsafe_allow_html=True)
    
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as log_file:
            logs = log_file.readlines()
        st.text_area("Logs", ''.join(logs), height=300)
    else:
        st.error("No logs found.")
    
