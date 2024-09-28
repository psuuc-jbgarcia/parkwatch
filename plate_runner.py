# plate_runner.py
import subprocess

def run_plate_script():
    try:
        # Provide the correct path to license.py, assuming it's in the same directory
        subprocess.Popen(['python', 'license.py'])
        print("license.py script is running...")
    except Exception as e:
        print(f"Error running license.py: {e}")
