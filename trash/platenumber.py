import json
import os
from datetime import datetime

def load_detected_plates(filename):
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the JSON file
    file_path = 'C:/Users/Jerico/Documents/parkwatch/detected_plates.json'

    print(f"Looking for file at: {file_path}")  # Debugging output

    with open(file_path, 'r') as f:
        detected_plates_data = json.load(f)
    return detected_plates_data

filename = 'detected_plates.json'

# Load the detected plates data from the JSON file
detected_plates_data = load_detected_plates(filename)

# Dictionary to hold the latest departure times and corresponding arrival times
latest_departure_info = {}

for entry in detected_plates_data:
    plate_number = entry['plate_number']
    arrival_time = entry['arrival_time']
    departure_time = entry['departure_time']

    # Only consider valid departure times
    if departure_time:
        # Parse departure time to a datetime object for comparison
        departure_time_dt = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

        # Check if the plate number already exists in the dictionary
        if plate_number not in latest_departure_info:
            # Store both departure and arrival time
            latest_departure_info[plate_number] = {
                'departure_time': departure_time_dt,
                'arrival_time': arrival_time
            }
        else:
            # Update if the current departure time is later
            if departure_time_dt > latest_departure_info[plate_number]['departure_time']:
                latest_departure_info[plate_number] = {
                    'departure_time': departure_time_dt,
                    'arrival_time': arrival_time
                }

# Display the results with both latest departure time and its corresponding arrival time
for plate_number, info in latest_departure_info.items():
    latest_departure = info['departure_time'].strftime('%Y-%m-%d %H:%M:%S')
    corresponding_arrival = info['arrival_time']
    print(f"Plate Number: {plate_number}, Arrival Time: {corresponding_arrival}, Departure Time: {latest_departure}")
