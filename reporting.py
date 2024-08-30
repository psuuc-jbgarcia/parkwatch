import csv
from datetime import datetime
import pandas as pd

import csv
from datetime import datetime
import logging

def log_detailed_data(posList, free_spaces, reserved_spaces):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_path = 'detailed_data_log.csv'
    
    try:
        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([timestamp, free_spaces, reserved_spaces])
    except Exception as e:
        print(f"Error logging data: {e}")

# Analyze data from log file
def analyze_data():
    try:
        df = pd.read_csv('detailed_parking_data.csv')
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Aggregate data
        total_parked = df['total_vehicles'].sum()
        reserved_spaces = df['reserved_spaces'].iloc[0]  # Assuming reserved spaces don't change frequently
        
        # Determine the times when parking was full
        full_parking_times = df[df['free_spaces'] == 0]
        
        return {
            'total_parked': total_parked,
            'reserved_spaces': reserved_spaces,
            'full_parking_times': full_parking_times['timestamp'].tolist()
        }
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None
