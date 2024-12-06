
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import shutil
import schedule
# Set up logging function
from utils import log_event
# Chrome options setup
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent = your user agent")

# Download directory setup
download_dir = "downloads"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Chrome preferences for download
prefs = {
    "download.default_directory": os.path.abspath(download_dir),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service("C:\\Users\\udayk\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to check if the download
# is complete


def is_download_complete(file_name):
    """Check if a file is completely downloaded."""
    file_path = os.path.join(download_dir, file_name)
    return os.path.exists(file_path) and not file_name.endswith(".crdownload")

# Function to download the report with retry mechanism
def download_report(data_link, file_name):
    """Attempt to download the report until the file is fully downloaded."""
    retry_count = 0
    while retry_count < 3:  # Retry up to 3 times if incomplete
        try:
            driver.get(data_link)
            log_event(f"Accessing download link: {data_link}")
            time.sleep(3)  # Wait for the download to start

            # Check if download is complete
            if is_download_complete(file_name):
                log_event(f"Download completed: {file_name}")
                break
            else:
                log_event(f"Incomplete download detected for {file_name}. Retrying ({retry_count + 1}/3)...")
                retry_count += 1
                time.sleep(2)  # Wait a bit before retrying
        except WebDriverException as e:
            log_event(f"Failed to download from {data_link}: {e}")
            retry_count += 1

# Main script execution with logging
def main_script_downloading():
    try:
        log_event("Starting download process.")
        driver.get("https://www.nseindia.com/all-reports")
        time.sleep(10)  # Allow time for the page to load

        # Locate the report div
        try:
            report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")
            log_event("Found report div on the page.")
        except NoSuchElementException:
            raise Exception("Report div not found on the page.")

        # Locate report download links
        try:
            report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")
            if not report_divs:
                raise Exception("No report download elements found.")
            log_event(f"Found {len(report_divs)} report download elements.")
        except NoSuchElementException:
            raise Exception("No report download elements found in the report div.")

        for report in report_divs:
            data_link = report.get_attribute("data-link")
            file_name = data_link.split('/')[-1]  # Extract the file name from the URL
            log_event(f"Starting download for: {file_name}")

            # Attempt to download the report with redownload check
            download_report(data_link, file_name)

        log_event("All downloads completed.")

    except TimeoutException:
        log_event("The request to the website timed out.")
    except Exception as e:
        log_event(f"An error occurred: {e}")
    finally:
        log_event("Closing the driver.")
        driver.quit()

from csv_handling import sort_downloaded_files,create_zip_in_date_folder
sort_downloaded_files()

create_zip_in_date_folder()
# -----------------------------------------------------------------------------------


