import os
import pickle

# Path to your pickle file (make sure this path is correct)
parking_file = 'CarParkPos'

def load_pos_list():
    # Check if the file exists
    if not os.path.exists(parking_file):
        print(f"Error: File not found: {parking_file}")
        return []  # Return empty list if file doesn't exist

    try:
        # Open and load the pickle file
        with open(parking_file, 'rb') as f:
            data = pickle.load(f)  # Load the data from the pickle file
            return data  # Return the loaded data
    except (pickle.PickleError, EOFError, IOError) as e:
        # Handle exceptions if there are issues loading the pickle file
        print(f"Error loading pickle file: {e}")
        return []  # Return empty list on failure

# Call the function and print the loaded positions
positions = load_pos_list()

if positions:
    print("Loaded positions:")
    for idx, pos in enumerate(positions):
        print(f"Slot {idx + 1}: {pos}")
else:
    print("No positions loaded.")
