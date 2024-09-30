import json
import os
from datetime import datetime
from collections import Counter

# Function to load parking data
def load_parking_data(file_path):
    with open(file_path, 'r') as f:
        timestamps = json.load(f)
    return [datetime.fromisoformat(ts) for ts in timestamps]

# Function to process parking data
def process_parking_data(timestamps):
    total_full_events = len(timestamps)
    
    # Count full events per hour
    hourly_counts = Counter()
    for timestamp in timestamps:
        try:
            dt = datetime.fromisoformat(timestamp)
            hour = dt.strftime("%I:00 %p")
            hourly_counts[hour] += 1
        except Exception as e:
            print(f"Error parsing timestamp {timestamp}: {e}")
    
    # Find peak hour
    peak_hour, peak_count = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else ("00:00 AM", 0)
    
    return total_full_events, hourly_counts, peak_hour, peak_count

# New function to load detected plates data with error handling
def load_detected_plates():
    file_path = os.path.join('C:/Users/Jerico/Documents/parkwatch/detected_plates.json')

    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()  # Read and strip whitespace
            if not content:  # Check if the content is empty
                print("Detected plates data file is empty.")
                return []  # Return an empty list if file is empty
            return json.loads(content)  # Load JSON data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []  # Return an empty list in case of JSON decoding error
    except Exception as e:
        print(f"Error loading detected plates data: {e}")
        return []  # Handle any other exceptions

# New function to process the detected plates data (arrival and departure times)
def process_detected_plates_data(detected_plates_data):
    latest_departure_info = {}

    for entry in detected_plates_data:
        plate_number = entry['plate_number']
        arrival_time = entry['arrival_time']
        departure_time = entry.get('departure_time')

        if departure_time:
            departure_time_dt = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

            if plate_number not in latest_departure_info:
                latest_departure_info[plate_number] = {
                    'departure_time': departure_time_dt,
                    'arrival_time': arrival_time
                }
            else:
                if departure_time_dt > latest_departure_info[plate_number]['departure_time']:
                    latest_departure_info[plate_number] = {
                        'departure_time': departure_time_dt,
                        'arrival_time': arrival_time
                    }

    return latest_departure_info

# Main report generation function (modified to include the new data)
def generate_report(file_path, date_str):
    # Load and filter parking timestamps
    try:
        with open(file_path, 'r') as file:
            timestamps = json.load(file)
    except Exception as e:
        return f"Error loading parking data: {e}"

    filtered_timestamps = [ts for ts in timestamps if ts.startswith(date_str)]
    
    try:
        total_full_events, hourly_counts, peak_hour, peak_count = process_parking_data(filtered_timestamps)
    except Exception as e:
        return f"Error processing parking data: {e}"

    # Load detected plates data
    try:
        detected_plates_data = load_detected_plates()  # Corrected: no argument here
    except Exception as e:
        return f"Error loading detected plates data: {e}"

    # Process detected plates data to get arrival and departure times
    try:
        latest_departure_info = process_detected_plates_data(detected_plates_data)
    except Exception as e:
        return f"Error processing detected plates data: {e}"

    # Generate the report
    report = f"Parking Report for {date_str}\nTotal Parking Full: {total_full_events}, Peak Hour: {peak_hour} ({peak_count} times)\n\n"
    
    # Add the plate number report for arrival and departure times
    report += "Arrival and Departure Information:\n"
    for plate_number, info in latest_departure_info.items():
        latest_departure = info['departure_time'].strftime('%I:%M %p')  # 12-hour format
        corresponding_arrival = datetime.strptime(info['arrival_time'], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')  # 12-hour format
        report += f"Plate Number: {plate_number}, Arrival Time: {corresponding_arrival}, Departure Time: {latest_departure}\n"

    return report
