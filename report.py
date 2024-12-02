import json
import os
from datetime import datetime
from collections import Counter

# Function to load parking data
def load_parking_data(file_path):
    try:
        with open(file_path, 'r') as f:
            timestamps = json.load(f)
        return [datetime.fromisoformat(ts) for ts in timestamps]
    except Exception as e:
        print(f"Error loading parking data: {e}")
        return []

# Function to process parking data
def process_parking_data(timestamps):
    total_full_events = len(timestamps)

    # Count full events per hour
    hourly_counts = Counter()
    for timestamp in timestamps:
        try:
            hour = timestamp.strftime("%I:00 %p")
            hourly_counts[hour] += 1
        except Exception as e:
            print(f"Error parsing timestamp {timestamp}: {e}")

    # Find peak hour
    peak_hour, peak_count = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else ("00:00 AM", 0)

    return total_full_events, hourly_counts, peak_hour, peak_count

# Function to load detected plates data with error handling
def load_detected_plates(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                print("Detected plates data file is empty.")
                return []
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        print(f"Error loading detected plates data: {e}")
        return []

# Function to load daily report data
def load_daily_report(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading daily report data: {e}")
        return []

# Function to process detected plates data based on the arrival date
def process_detected_plates_data(detected_plates_data, date_str):
    plate_departure_info = {}
    report_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    for entry in detected_plates_data:
        plate_number = entry['plate_number']
        arrival_time = entry['arrival_time']
        departure_time = entry.get('departure_time')

        # Parse the arrival time and check if it matches the report date
        arrival_time_dt = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')
        if arrival_time_dt.date() == report_date:
            # Parse departure time if available
            departure_time_dt = (
                datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S') if departure_time else None
            )

            # Add the current entry (arrival and departure times) for this plate number
            if plate_number not in plate_departure_info:
                plate_departure_info[plate_number] = []
            
            plate_departure_info[plate_number].append({
                'arrival_time': arrival_time_dt.strftime('%I:%M %p'),
                'departure_time': departure_time_dt.strftime('%I:%M %p') if departure_time_dt else 'N/A'
            })

    return plate_departure_info

# Main function to generate the report
def generate_report(parking_file_path, detected_plates_file_path, daily_report_file_path, date_str):
    report = ""

    # Load and filter parking timestamps
    try:
        timestamps = load_parking_data(parking_file_path)
        filtered_timestamps = [ts for ts in timestamps if ts.date() == datetime.strptime(date_str, '%Y-%m-%d').date()]
        total_full_events, hourly_counts, peak_hour, peak_count = process_parking_data(filtered_timestamps)
    except Exception as e:
        return f"Error processing parking data: {e}"

    # Load detected plates data
    detected_plates_data = load_detected_plates(detected_plates_file_path)
    plate_departure_info = process_detected_plates_data(detected_plates_data, date_str)

    # Load daily report data
    daily_report_data = load_daily_report(daily_report_file_path)
    daily_totals = next((item for item in daily_report_data if item['date'] == date_str), None)

    # Generate report content
    if daily_totals:
        report += f"Total Parked Vehicles: {daily_totals['total_parked_vehicles']}\n"
        report += f"Reserved Vehicles: {daily_totals['reserved_vehicles']}\n"
    else:
        report += "No data available for Total Parked and Reserved Vehicles.\n"

    report += f"Total Parking Full Events: {total_full_events}, Peak Hour: {peak_hour} ({peak_count} times)\n\n"

    # Add plate number information
    report += "Arrival and Departure Information:\n"
    if plate_departure_info:
        for plate_number, info_list in plate_departure_info.items():
            for info in info_list:
                report += f"Plate Number: {plate_number}, Arrival: {info['arrival_time']}, Departure: {info['departure_time']}\n"
    else:
        report += "No arrival and departure data available for the specified date.\n"

    return report
