import json
from datetime import datetime
from collections import Counter
from firebase.firebase_config import db  # Assuming you're using db for Firestore

# Function to load parking data
def load_parking_data(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            print("File Content: ", content)  # Debugging line to check file content
            timestamps = json.loads(content) if content else []  # Handle empty content
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

# Function to load daily report data
def load_daily_report(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading daily report data: {e}")
        return []

def fetch_detected_plates(start_date, end_date):
    try:
        print(f"Fetching data for date range: {start_date} to {end_date}")
        detected_plates_ref = db.collection('detected_plates')  # Use db reference from firebase_config

        # Filter based on arrival_time
        query = detected_plates_ref.where('arrival_time', '>=', f"{start_date} 00:00:00").where('arrival_time', '<=', f"{end_date} 23:59:59")
        results = query.stream()

        plate_info = []
        for doc in results:
            plate_data = doc.to_dict()
            print(f"Fetched Plate Data: {plate_data}")  # Debugging line to inspect each doc
            plate_info.append({
                'plate_number': plate_data.get('plate_number'),
                'arrival_time': plate_data.get('arrival_time'),
                'departure_time': plate_data.get('departure_time', 'N/A')
            })

        if not plate_info:
            print("No plate data found.")

        return plate_info
    except Exception as e:
        print(f"Error fetching detected plates data: {e}")
        return []

# Main function to generate the report
def generate_report(parking_file_path, daily_report_file_path, start_date, end_date):
    report = ""

    # Ensure start_date and end_date are datetime objects
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Load and filter parking timestamps
    try:
        timestamps = load_parking_data(parking_file_path)
        filtered_timestamps = [
            ts for ts in timestamps 
            if start_date <= ts.date() <= end_date
        ]
        total_full_events, hourly_counts, peak_hour, peak_count = process_parking_data(filtered_timestamps)
    except Exception as e:
        return f"Error processing parking data: {e}"

    # Load daily report data
    try:
        daily_report_data = load_daily_report(daily_report_file_path)
        daily_totals = [
            item for item in daily_report_data 
            if start_date <= datetime.strptime(item['date'], '%Y-%m-%d').date() <= end_date
        ]
    except Exception as e:
        return f"Error processing daily report data: {e}"

    # Fetch detected plates data from Firestore
    try:
        detected_plates_data = fetch_detected_plates(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        return f"Error fetching detected plates data: {e}"

    # Generate report content
    if daily_totals:
        for daily_total in daily_totals:
            report += f"Date: {daily_total['date']}\n"
            report += f"Total Parked Vehicles: {daily_total['total_parked_vehicles']}\n"
            report += f"Reserved Vehicles: {daily_total['reserved_vehicles']}\n\n"
    else:
        report += "No data available for Total Parked and Reserved Vehicles.\n\n"

    report += f"Total Parking Full Events: {total_full_events}, Peak Hour: {peak_hour} ({peak_count} times)\n\n"

    # Add plate number information
    report += "Arrival and Departure Information:\n"
    if detected_plates_data:
        for plate in detected_plates_data:
            report += f"Plate Number: {plate['plate_number']}, Arrival: {plate['arrival_time']}, Departure: {plate['departure_time']}\n"
    else:
        report += "No arrival and departure data available for the specified date range.\n"

    return report
