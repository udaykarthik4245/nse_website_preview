import time
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import zipfile
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from nse_report_downloader.email_notifier import send_email_with_logs
from nse_report_downloader.file_utils import handle_downloaded_zip, add_to_sub_zip, is_zip_already_downloaded, get_next_zip_name
from nse_report_downloader.logger_config import important_logs, info, warning, error

# Configure the download folder
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
STATUS_FILE_PATH = os.path.join(DOWNLOAD_FOLDER, "download_status.txt")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
today = datetime.now().strftime("%Y-%m-%d")
RETRY_COUNT = 3
RETRY_DELAY = 5



def setup_driver():
    """Initialize and configure the Chrome WebDriver."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent = Chrome/130.0.0.0")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True  
    })

    service = Service('"C:\\Users\\udayk\\Downloads\\chromedriver-win64_main\\chromedriver-win64\\chromedriver.exe"')

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except WebDriverException as e:
        print(f"Failed to initialize the Chrome WebDriver: {e}")
        error(f"Failed to initialize the Chrome WebDriver: {e}")
        raise

def fetch_with_retry(driver, url):
    """Retry fetching the NSE page if network issues occur."""
    for attempt in range(RETRY_COUNT):
        try:
            driver.get(url)
            time.sleep(2)
            return
        except WebDriverException as e:
            warning(f"Network failed. Retrying... ({attempt + 1}/{RETRY_COUNT})")
            time.sleep(RETRY_DELAY)
    error(f"Failed to connect to {url} after {RETRY_COUNT} attempts.")
    raise WebDriverException("Network error. Unable to load the website.")

def download_file_with_retry(driver, file_url):
    """Retry downloading the file if it fails."""
    for attempt in range(RETRY_COUNT):
        try:
            driver.get(file_url)
            time.sleep(4)  # Allow the download to start
            return True
        except WebDriverException as e:
            warning(f"Download failed. Retrying... ({attempt + 1}/{RETRY_COUNT})")
            time.sleep(RETRY_DELAY)
    error(f"Failed to download {file_url} after {RETRY_COUNT} attempts.")
    return False

def fetch_nse_report():
    """Download NSE reports and save them in a ZIP file."""
    if is_zip_already_downloaded():
        print("ZIP file already exists. Skipping download.")
        return
    
    # Start time for the report
    start_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    success_count = 0
    failure_count = 0

    driver = setup_driver()
    # //*[@id="cr_equity_daily_Current"]/div/div[1]
    try:
        URL = "https://www.nseindia.com/all-reports"
        zip_name = get_next_zip_name("merged_reports")
        zip_path = os.path.join(DOWNLOAD_FOLDER, zip_name)

        with zipfile.ZipFile(zip_path, "a") as zipf:
            fetch_with_retry(driver, URL)

            try:
                report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")
                report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")
            except NoSuchElementException as e:
                error(f"Error fetching data from NSE: {e}")
                return

            for report in report_divs:
                file_url = report.get_attribute("data-link")
                file_name = file_url.split("/")[-1]

                if download_file_with_retry(driver, file_url):
                    success_count += 1
                    downloaded_file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

                    if os.path.exists(downloaded_file_path):
                        
                        with open(STATUS_FILE_PATH, 'w') as status_file:
                            status_file.write(f"in-progress_{today}")

                        if file_name.endswith(".zip"):
                            handle_downloaded_zip(downloaded_file_path, zipf)
                        elif file_name.lower().endswith(".csv"):
                            add_to_sub_zip(zipf, downloaded_file_path, 'Reports(.csv)')
                        elif file_name.lower().endswith(".dat"):
                            add_to_sub_zip(zipf, downloaded_file_path, 'Reports(.dat)')
                        else:
                            add_to_sub_zip(zipf, downloaded_file_path)
                    else:
                        error(f"Failed to download: {file_name}")
                        failure_count += 1
                else:
                    error(f"Download failed: {file_name}")
                    failure_count += 1

            while any(file.endswith('.crdownload') for file in os.listdir(DOWNLOAD_FOLDER)):
                time.sleep(1)

            with open(STATUS_FILE_PATH, 'w') as status_file:
                status_file.write(f"completed_{today}")

            print(f"Downloaded: {zip_name}")
            info(f"Downloaded and Created Zip: {zip_name} Successfully!")


            # Send success email with log details
            send_email_with_logs(
                logs=important_logs,  # Defined in logger_config
                start_time=start_time,
                success_count=success_count,
                failure_count=failure_count,
                status="Success" if failure_count == 0 else "Partial Success"
            )

    except WebDriverException as e:
        error(f"An error occurred: {e}")
    finally:
        driver.quit()
