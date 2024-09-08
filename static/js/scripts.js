let alertShown = false;

function updateDateTime() {
    const now = new Date();
    const dateTimeString = now.toLocaleString('en-US', {
        dateStyle: 'short',
        timeStyle: 'short'
    });
    document.getElementById('current-date-time').innerText = dateTimeString;
}
setInterval(updateDateTime, 1000);
updateDateTime();

function updateParkingInfo(data) {
    const { totalVehicles, parkingAvailable, slotsReserved } = data;

    document.getElementById('total-vehicles').innerText = totalVehicles;
    document.getElementById('parking-available').innerText = parkingAvailable;
    document.getElementById('slots-reserved').innerText = slotsReserved;

    if (parseInt(parkingAvailable, 10) === 0 && !alertShown) {
        Swal.fire({
            icon: 'warning',
            title: 'Alert',
            text: 'Parking slots are full!',
            showConfirmButton: true
        });
        alertShown = true;

        // Save the timestamp to the backend
        saveFullParkingTimestamp();
    } else if (parseInt(parkingAvailable, 10) > 0) {
        alertShown = false;
    }
}

function saveFullParkingTimestamp() {
    // Get the current time in UTC
    const now = new Date();
    
    // Convert UTC time to Philippine Time (UTC+8)
    const offset = 8 * 60; // Offset in minutes
    const localTime = new Date(now.getTime() + offset * 60 * 1000);

    // Format the date as ISO string
    const timestamp = localTime.toISOString().replace('Z', '+08:00');

    fetch('/save_full_parking_timestamp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ timestamp })
    })
    .then(response => {
        if (response.ok) {
            console.log('Timestamp saved successfully.');
        } else {
            console.error('Failed to save timestamp.');
        }
    })
    .catch(error => {
        console.error('Error saving timestamp:', error);
    });
}

function fetchParkingInfo() {
    fetch('/get_parking_info')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok');
        })
        .then(data => {
            updateParkingInfo(data);
        })
        .catch(error => {
            console.error('Error fetching parking information:', error);
        });
}

fetchParkingInfo();
setInterval(fetchParkingInfo, 1000);

// Other functions remain unchanged...


function updateCamera() {
    const cameraSelect = document.getElementById('cameraSelect');
    const selectedCamera = cameraSelect.value;
    const videoFeed = document.getElementById('video_feed');
    videoFeed.src = `/video_feed/${selectedCamera}`;
}

function runManagement() {
    fetch('/run_management')
    .then(response => {
        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Modification is successful!', // Updated title
                showConfirmButton: true
            });
            console.log('Management script started.');
        } else {
            console.error('Failed to start management script.');
        }
    })
    .catch(error => console.error('Error:', error));

}

function showInstructions() {
    $('#instructions-modal').modal('show');
}

function showReportIncidentModal() {
    const timestamp = new Date().toISOString();
    document.getElementById('incident-timestamp').value = timestamp;
    $('#report-incident-modal').modal('show');
}

function submitIncidentReport() {
    const description = document.getElementById('incident-description').value;
    const timestamp = document.getElementById('incident-timestamp').value;

    if (!description) {
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: 'Please provide a description of the incident.',
            showConfirmButton: true
        });
        return;
    }

    fetch('/report_incident', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description, timestamp })
        })
        .then(response => {
            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: 'Incident reported successfully!',
                    showConfirmButton: true
                });
                $('#report-incident-modal').modal('hide');
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Failed to report incident.',
                    showConfirmButton: true
                });
            }
        })
        .catch(error => {
            console.error('Error reporting incident:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Failed to report incident.',
                showConfirmButton: true
            });
        });
}

function generateReport() {
    Swal.fire({
        icon: 'success',
        title: 'Success',
        text: 'Generated report successfully.',
        showConfirmButton: true
    });
}