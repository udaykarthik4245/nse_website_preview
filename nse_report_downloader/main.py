import schedule
import time
from datetime import timedelta, datetime
from nse_report_downloader.downloader import fetch_nse_report
from nse_report_downloader.file_utils import is_zip_already_downloaded
from nse_report_downloader.logger_config import info, warning, error

# Configuration
SCHEDULED_TIME = "17:40"  

CHECK_INTERVAL = 60  

MISSED_THRESHOLD = timedelta(minutes=10)  

RETRY_COUNT = 3 

RETRY_DELAY = 4

CHECK_ZIP_INTERVAL = 600

# Track the last download date to avoid duplicate fetches
last_download_date = None

is_downloading = False  # Track if download is in progress

def retry_on_failure(func):
    """Retry to handle exceptions and retry the operation."""
    def wrapper(*args, **kwargs):
        for attempt in range(RETRY_COUNT):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error(f"Attempt {attempt + 1} failed with error: {e}")
                if attempt < RETRY_COUNT - 1:
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    warning("Max retries reached. Failed to complete the operation.")
    return wrapper

@retry_on_failure
def conditional_fetch_report():
    """Fetch NSE report only if today's report doesn't exist."""
    global last_download_date, is_downloading
    
    if is_zip_already_downloaded():
        print("Today's report already exists. No need to fetch.")
    else:
        is_downloading = True
        print("Fetching NSE report...")
        time.sleep(1)
        fetch_nse_report()
        last_download_date = datetime.now().date()
        is_downloading = False

def handle_missed_schedule():
    """Check if the scheduled task was missed and handle it."""
    global last_download_date

    today = datetime.now().date()
    now = datetime.now()

    if last_download_date == today:
        print("Today's report is already downloaded. No missed schedule to handle.")
        return

    # Calculate the target time for today’s scheduled task
    scheduled_time = datetime.strptime(SCHEDULED_TIME, "%H:%M").time()
    scheduled_datetime = datetime.combine(today, scheduled_time)

    # If the scheduled time has passed and it's still before midnight (11:59 PM)
    if now > scheduled_datetime and now.time() < datetime.max.time():
        print("Scheduled time has passed. Checking if download is needed...")

        # Trigger download if within the threshold or before midnight
        if (now - scheduled_datetime) <= MISSED_THRESHOLD or now.date() == today:
            conditional_fetch_report()
        else:
            warning("Missed the threshold. Waiting for the next day's download.")
    else:
        print("No missed download detected.")

def check_for_zip_availability():
    """Periodically check if today's zip file is available, re-download if missing."""
    global is_downloading
    today = datetime.now().date()

    if last_download_date == today and not is_zip_already_downloaded():
        print("Today's report is missing. Re-downloading...")
        if not is_downloading:
            is_downloading = True
            conditional_fetch_report()
            is_downloading = False

def run_scheduler():
    """Run the scheduled tasks continuously."""
    handle_missed_schedule()

    schedule.every().day.at(SCHEDULED_TIME).do(conditional_fetch_report)

    schedule.every(CHECK_ZIP_INTERVAL // 60).minutes.do(check_for_zip_availability)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            error(f"Scheduler error: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_scheduler()
