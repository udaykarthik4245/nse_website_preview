import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def wait_for_download(download_dir, timeout=60):
    seconds = 0
    download_complete = False
    while not download_complete and seconds < timeout:
        time.sleep(1)
        download_complete = not any([filename.endswith('.crdownload') for filename in os.listdir(download_dir)])
        seconds += 1
    if not download_complete:
        print("Timeout waiting for download to finish.")

def download_reports(download_dir):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Chrome/130.0.0.0")
    
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)


    service = Service("C:\\Users\\udayk\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:

        driver.get("https://www.nseindia.com/all-reports")
        time.sleep(10) 

 
        report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")
        report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")


        for report in report_divs:
            data_link = report.get_attribute("data-link")
            print(f"Downloading from: {data_link}")
            driver.get(data_link)
            wait_for_download(download_dir)
            time.sleep(2)  
    finally:
        driver.quit()

if __name__ == "__main__":
    download_dir = "downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    download_reports(download_dir)

