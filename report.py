import json
from datetime import datetime
from collections import Counter

def load_parking_data(file_path):
    with open(file_path, 'r') as f:
        timestamps = json.load(f)  # Assuming the JSON is a simple list
    return [datetime.fromisoformat(ts) for ts in timestamps]

def process_parking_data(timestamps):
    total_full_events = len(timestamps)
    
    # Count full events per hour
    hourly_counts = Counter()
    for timestamp in timestamps:
        try:
            # Parse the timestamp considering the full format including timezone
            dt = datetime.fromisoformat(timestamp)
            hour = dt.strftime("%I:00 %p")  # Format to 12-hour format with AM/PM
            hourly_counts[hour] += 1
        except Exception as e:
            print(f"Error parsing timestamp {timestamp}: {e}")  # Log parsing errors

    # Find peak hour
    if hourly_counts:
        peak_hour, peak_count = max(hourly_counts.items(), key=lambda x: x[1])
    else:
        peak_hour, peak_count = "00:00 AM", 0  # Default if no data

    return total_full_events, hourly_counts, peak_hour, peak_count

def generate_report(file_path, date_str):
    try:
        with open(file_path, 'r') as file:
            timestamps = json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return "Error loading data"

    # Filter timestamps by the specified date
    filtered_timestamps = [
        ts for ts in timestamps if ts.startswith(date_str)
    ]

    print("Filtered Timestamps:", filtered_timestamps)  # Debugging line

    try:
        total_full_events, hourly_counts, peak_hour, peak_count = process_parking_data(filtered_timestamps)
    except Exception as e:
        print(f"Error processing parking data: {e}")
        return "Error processing report"

    print(f"Total Full Events: {total_full_events}, Hourly Counts: {hourly_counts}, Peak Hour: {peak_hour}, Peak Count: {peak_count}")  # Debugging line

    # Directly use peak_hour as it is already in 12-hour format
    report = (f"Total Parking Full: {total_full_events}, "
              f"Parking is full at time of: {peak_hour} ({peak_count} times)")
    return report
