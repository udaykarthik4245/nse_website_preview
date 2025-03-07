from flask import Flask, render_template, send_file, request, jsonify
import os
from datetime import datetime, time
import time as time_module
from nse_report_downloader.main import run_scheduler
from threading import Thread
from nse_report_downloader.logger_config import info, warning, error

app = Flask(__name__)

# Configure paths and ensure directories exist
BASE_DIR = os.getcwd()
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
STATUS_FILE_PATH = os.path.join(DOWNLOAD_FOLDER, "download_status.txt")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('main.html')


@app.route('/download', methods=['POST'])
def download_report():

    try:
        info("Download report requested.")

        # Validate content type
        if request.content_type != 'application/json':
            return jsonify({"status": "error", "message": "Content-type must be JSON."}), 400

        # Get JSON data and validate fields
        data = request.get_json()
        selected_date = data.get('Date')
        file_format = data.get('format')

        if not selected_date or file_format != 'zip':
            return jsonify({"status": "error", "message": "Invalid request. Provide 'Date' and 'format' fields correctly."}), 400

        # Determine date status (today, past, future)
        today = datetime.now().date()
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        is_today = selected_date_obj == today
        is_past_date = selected_date_obj < today

        # Construct expected file path
        zip_filename = f"merged_reports_{selected_date}.zip" 
        report_path = os.path.join(DOWNLOAD_FOLDER,zip_filename) 
        
        # Handling Previous's report download status
        if is_past_date: 
            if os.path.exists(report_path): 
                info("Downloading...") 
                time_module.sleep(2) 
                info("Reports downloaded successfully!") 
                return send_file(report_path, as_attachment=True, mimetype='application/zip') 
            else:
                warning(f"No report available for {selected_date}.")
                return jsonify({"status": "error", "message": f"No report available for {selected_date}."}), 404


        # Handling today's report download status
        if is_today:
            if os.path.exists(report_path):

                if os.path.exists(STATUS_FILE_PATH):
                    with open(STATUS_FILE_PATH, 'r') as status_file:
                        status_content = status_file.read().strip()

                    if status_content == f"completed_{today}":
                        info("Downloading...")
                        time_module.sleep(2)
                        info("Reports downloaded successfully!")
                        return send_file(report_path, as_attachment=True, mimetype='application/zip')
                    
                    elif status_content == f"in-progress_{today}":
                        warning("Today's report is still downloading.")
                        return jsonify({"status": "error", "message": "Today's report is still being downloaded. Please check back soon."}), 202
                else:
                    print("Download status file not found.")


        if not is_today:
            warning("Report for future dates cannot be downloaded.")
            return jsonify({"status": "error", "message": "Invalid request. Cannot download reports for future dates."}), 400

        # Check if it's past the report generation time (6:10 PM)
        current_time = datetime.now().time()
        cutoff_time = time(18, 10)
        if current_time < cutoff_time:
            warning("Report for today is not available yet.")
            return jsonify({"status": "error", "message": "Today's report is not yet available. Please try after 6:10 PM."}), 404

    except Exception as e:
        error(f"Error in download: {str(e)}")
        return jsonify({"status": "error", "message": f"Failed to download report. Error: {str(e)}"}), 500


@app.route('/logs')
def view_logs():
    log_entries = []
    try:
        with open("logs/nse_activity_log.log", 'r') as log_file:  # Use the path defined in log_config.py
            logs = log_file.read().splitlines()
            for log in logs:
                parts = log.split(' - ')
                if len(parts) == 3:
                    timestamp, level, action = parts
                    status = "Error" if "ERROR" in level else "Warning" if "WARNING" in level else "Success" if "success" in action.lower() else "Info"
                    log_entries.append({
                        "timestamp": timestamp,
                        "level": level,
                        "action": action,
                        "status": status
                    })
    except FileNotFoundError:
        return render_template('logs.html', logs=["Log file not found."])

    return render_template('logs.html', logs=log_entries)


def start_scheduler():
    """Start the scheduler in a separate thread."""
    try:
        scheduler_thread = Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
    except Exception as e:
        error(f"Error starting scheduler: {str(e)}")


if __name__ == '__main__':
    start_scheduler()
    app.run(host='127.0.0.1', port=5000, debug=False)
