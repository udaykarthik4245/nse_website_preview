import logging
from datetime import datetime

def log_event(event_description):
    with open("logs.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {event_description}\n"
        log_file.write(log_entry)
    print(event_description)

