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
    latest_departure_info = {}
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

            # Update the latest departure info
            if plate_number not in latest_departure_info:
                latest_departure_info[plate_number] = {
                    'departure_time': departure_time_dt,
                    'arrival_time': arrival_time
                }
            else:
                if (departure_time_dt and 
                    (latest_departure_info[plate_number]['departure_time'] is None or 
                     departure_time_dt > latest_departure_info[plate_number]['departure_time'])):
                    latest_departure_info[plate_number] = {
                        'departure_time': departure_time_dt,
                        'arrival_time': arrival_time
                    }

    return latest_departure_info

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
    latest_departure_info = process_detected_plates_data(detected_plates_data, date_str)

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
    if latest_departure_info:
        for plate_number, info in latest_departure_info.items():
            latest_departure = info['departure_time'].strftime('%I:%M %p') if info['departure_time'] else 'N/A'
            corresponding_arrival = datetime.strptime(info['arrival_time'], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            report += f"Plate Number: {plate_number}, Arrival: {corresponding_arrival}, Departure: {latest_departure}\n"
    else:
        report += "No arrival and departure data available for the specified date.\n"

    return report


