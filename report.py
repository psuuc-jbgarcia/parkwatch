import json
from datetime import datetime
from collections import Counter

def load_parking_data(file_path):
    with open(file_path, 'r') as f:
        timestamps = json.load(f)  # Assuming the JSON is a simple list
    return [datetime.fromisoformat(ts) for ts in timestamps]

def process_parking_data(filtered_timestamps):
    if not filtered_timestamps:
        return 0, {}, None, 0  # Default values if no timestamps

    # Your processing logic goes here
    # For example:
    total_full_events = len(filtered_timestamps)  # Example counting
    hourly_counts = {}  # Example dictionary to hold counts per hour
    peak_hour = None
    peak_count = 0

    # Example logic to populate hourly_counts, peak_hour, and peak_count
    for ts in filtered_timestamps:
        hour = ts[11:13]  # Extract hour from timestamp
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

        if hourly_counts[hour] > peak_count:
            peak_count = hourly_counts[hour]
            peak_hour = hour

    return total_full_events, hourly_counts, peak_hour, peak_count

def generate_report(file_path, date_str):
    with open(file_path, 'r') as file:
        timestamps = json.load(file)

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

    # Generate the report
    report = f"Total Events: {total_full_events}, Peak Hour: {peak_hour} ({peak_count} events)"
    return report
