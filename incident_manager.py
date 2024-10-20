import json
import os
from flask import jsonify, request
from firebase_admin import firestore

db = firestore.client()

FULL_PARKING_TIMESTAMPS_FILE = 'json_file/full_parking_timestamps.json'
FULL_PARKING_TIMESTAMPS_FILE2 = 'json_file/full_parking_timestamps2.json'

def report_incident():
    """
    Handle incident report submission.
    """
    try:
        data = request.json
        description = data.get('description')
        timestamp = data.get('timestamp')

        if not description or not timestamp:
            return jsonify({'error': 'Invalid input'}), 400

        # Save the incident report to Firestore
        incident_ref = db.collection('admin').add({
            'description': description,
            'timestamp': timestamp
        })

        return jsonify({'message': 'Incident report submitted successfully'}), 200

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


def save_full_parking_timestamp():
    """
    Save the timestamp of a full parking event.
    """
    timestamp = request.json.get('timestamp')

    if not timestamp:
        return jsonify({'error': 'No timestamp provided'}), 400

    # Read existing data from the JSON file
    if os.path.exists(FULL_PARKING_TIMESTAMPS_FILE):
        try:
            with open(FULL_PARKING_TIMESTAMPS_FILE, 'r') as file:
                timestamps = json.load(file)
        except json.JSONDecodeError:
            # Handle the case where the file is empty or corrupted
            timestamps = []
    else:
        timestamps = []

    # Append the new timestamp
    timestamps.append(timestamp)

    # Save the updated list back to the JSON file
    with open(FULL_PARKING_TIMESTAMPS_FILE, 'w') as file:
        json.dump(timestamps, file)

    return jsonify({'message': 'Timestamp saved successfully'}), 200

def save_full_parking_timestamp2():
    """
    Save the timestamp of a full parking event.
    """
    timestamp = request.json.get('timestamp')

    if not timestamp:
        print("No timestamp provided in request")
        return jsonify({'error': 'No timestamp provided'}), 400

    print(f"Received timestamp: {timestamp}")

    # Read existing data from the JSON file
    if os.path.exists(FULL_PARKING_TIMESTAMPS_FILE2):
        try:
            with open(FULL_PARKING_TIMESTAMPS_FILE2, 'r') as file:
                timestamps = json.load(file)
        except json.JSONDecodeError:
            print("Error reading JSON file, initializing with empty list")
            timestamps = []
    else:
        print("JSON file not found, creating new file")
        timestamps = []

    # Append the new timestamp
    timestamps.append(timestamp)

    # Save the updated list back to the JSON file
    with open(FULL_PARKING_TIMESTAMPS_FILE2, 'w') as file:
        json.dump(timestamps, file)

    print("Timestamp saved successfully")
    return jsonify({'message': 'Timestamp saved successfully'}), 200  # Added status code




def fetch_comments():
    """
    Fetch incidents and their related comments from Firestore.
    """
    try:
        admin_collection_ref = db.collection('admin')
        incidents = []

        # Loop through each document in the 'admin' collection
        for incident_doc in admin_collection_ref.stream():
            incident_data = incident_doc.to_dict()
            incident_id = incident_doc.id

            # Fetch description and timestamp from the incident document
            description = incident_data.get('description', 'No description available')
            timestamp = incident_data.get('timestamp', 'Unknown')

            # Fetch comments from the 'comments' subcollection ordered by timestamp
            comments_ref = admin_collection_ref.document(incident_id).collection('comments').order_by('timestamp')
            comments = []
            for comment in comments_ref.stream():
                comment_data = comment.to_dict()
                comments.append(comment_data)

            # Build the response with incident details and ordered comments
            incidents.append({
                'incident_id': incident_id,
                'description': description,
                'timestamp': timestamp,
                'comments': comments
            })

        # Return incidents with their respective comments
        return jsonify(incidents)
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return jsonify({'error': str(e)}), 500
