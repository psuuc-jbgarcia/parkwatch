import json
from datetime import datetime

# Assuming your JSON data is stored in a variable called `detected_plates_data`
detected_plates_data = [
    {"plate_number": "R 183 JF", "arrival_time": "2024-09-29 17:57:40", "departure_time": None},
    {"plate_number": "R 183 JF", "arrival_time": "2024-09-29 17:57:40", "departure_time": "2024-09-29 17:57:40"},
    {"plate_number": "R 183 JF", "arrival_time": "2024-09-29 17:57:40", "departure_time": "2024-09-29 17:57:41"},
    {"plate_number": "H 644 LX", "arrival_time": "2024-09-29 17:57:52", "departure_time": None},
    {"plate_number": "H 644 LX", "arrival_time": "2024-09-29 17:57:52", "departure_time": "2024-09-29 17:57:52"},
    {"plate_number": "H 644 LX", "arrival_time": "2024-09-29 17:57:52", "departure_time": "2024-09-29 17:57:53"},
    {"plate_number": "66 HH 07", "arrival_time": "2024-09-29 17:57:59", "departure_time": None},
    {"plate_number": "66 HH 07", "arrival_time": "2024-09-29 17:57:59", "departure_time": "2024-09-29 17:57:59"},
    {"plate_number": "66 HH 07", "arrival_time": "2024-09-29 17:57:59", "departure_time": "2024-09-29 17:58:00"},
    {"plate_number": "66 HH 07", "arrival_time": "2024-09-29 17:57:59", "departure_time": "2024-09-29 17:58:01"},
]

# Dictionary to hold the latest departure times
latest_departure_times = {}

for entry in detected_plates_data:
    plate_number = entry['plate_number']
    departure_time = entry['departure_time']

    # Only consider valid departure times
    if departure_time:
        # Parse departure time to a datetime object for comparison
        departure_time_dt = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

        # Check if the plate number already exists in the dictionary
        if plate_number not in latest_departure_times:
            latest_departure_times[plate_number] = departure_time_dt
        else:
            # Update if the current departure time is later
            if departure_time_dt > latest_departure_times[plate_number]:
                latest_departure_times[plate_number] = departure_time_dt

# Display the results
for plate_number, latest_departure in latest_departure_times.items():
    print(f"Plate Number: {plate_number}, Latest Departure Time: {latest_departure.strftime('%Y-%m-%d %H:%M:%S')}")
