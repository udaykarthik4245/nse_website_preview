# import os
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By


# def wait_for_download(download_dir, timeout=60):
#     seconds = 0
#     download_complete = False
#     while not download_complete and seconds < timeout:
#         time.sleep(1)
#         download_complete = not any([filename.endswith('.crdownload') for filename in os.listdir(download_dir)])
#         seconds += 1
#     if not download_complete:
#         print("Timeout waiting for download to finish.")


# def download_reports(download_dir):
#     chrome_options = Options()
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("user-agent=Chrome/130.0.0.0")

#     prefs = {
#         "download.default_directory": os.path.abspath(download_dir),
#         "download.prompt_for_download": False,
#         "download.directory_upgrade": True,
#         "safebrowsing.enabled": True
#     }
#     chrome_options.add_experimental_option("prefs", prefs)

#     service = Service("C:\\Users\\udayk\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
#     driver = webdriver.Chrome(service=service, options=chrome_options)

#     try:

#         driver.get("https://www.nseindia.com/all-reports")
#         time.sleep(10)

#         report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")
#         report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")

#         for report in report_divs:
#             data_link = report.get_attribute("data-link")
#             print(f"Downloading from: {data_link}")
#             driver.get(data_link)
#             wait_for_download(download_dir)
#             time.sleep(2)
#     finally:
#         driver.quit()


# if __name__ == "__main__":
#     download_dir = "downloads"
#     if not os.path.exists(download_dir):
#         os.makedirs(download_dir)
#     download_reports(download_dir)

# ------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
import time
# import file_utils
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
import zipfile
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from csv_handling import handle_downloaded_zip, add_to_sub_zip, is_zip_already_downloaded, get_next_zip_name
# from logger_config import logger

# Configure the download folder
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


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

    service = Service('C://chromedriver-win64//chromedriver.exe')

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except WebDriverException as e:
        print(f"Failed to initialize the Chrome WebDriver: {e}")
        # logging.error(f"Failed to initialize the Chrome WebDriver: {e}")
        raise

def fetch_nse_report():
    """Download NSE reports and save them in a ZIP file."""
    if is_zip_already_downloaded():
        print("ZIP file already exists. Skipping download.")
        return

    driver = setup_driver()
    try:
        URL = "https://www.nseindia.com/all-reports"

        zip_name = get_next_zip_name("merged_reports")
        zip_path = os.path.join(DOWNLOAD_FOLDER, zip_name)

        with zipfile.ZipFile(zip_path, "a") as zipf:
            driver.get(URL)
            time.sleep(2)

            try:
                report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")
                report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")
            except NoSuchElementException as e:
                print(f"Error fetching data from NSE: {e}")
                return

            for report in report_divs:
                file_url = report.get_attribute("data-link")
                file_name = file_url.split("/")[-1]

                driver.get(file_url)
                time.sleep(4)

                downloaded_file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                if os.path.exists(downloaded_file_path):
                    if file_name.endswith(".zip"):
                        handle_downloaded_zip(downloaded_file_path, zipf)
                    elif file_name.endswith(".csv") or file_name.endswith(".CSV"):
                        add_to_sub_zip(zipf, downloaded_file_path, 'Reports(.csv)')
                    elif file_name.endswith(".dat") or file_name.endswith(".DAT"):
                        add_to_sub_zip(zipf, downloaded_file_path, 'Reports(.dat)')
                    else:
                        add_to_sub_zip(zipf, downloaded_file_path)
                else:
                    # logging.error(f"Failed to download: {file_name}")
                    print(f"Failed to download: {file_name}")

            # Wait for any remaining downloads to complete
            while any(file.endswith('.crdownload') for file in os.listdir(DOWNLOAD_FOLDER)):
                time.sleep(1)

            print(f"Downloaded: {zip_name}")

    except WebDriverException as e:
        # logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        driver.quit()