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
    const now = new Date();
    const offset = 8 * 60;
    const localTime = new Date(now.getTime() + offset * 60 * 1000);
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
                title: 'Modification is successful!',
                showConfirmButton: true
            });
            console.log('Management script started.');
        } else {
            console.error('Failed to start management script.');
        }
    })
    .catch(error => console.error('Error:', error));
}

function runManagement2() {
    fetch('/run_management2')
    .then(response => {
        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Modification is successful!',
                showConfirmButton: true
            });
            console.log('Management 2 script started.');
        } else {
            console.error('Failed to start management script 2.');
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

function fetchComments() {
    fetch('/fetch_comments')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok');
        })
        .then(data => {
            updateCommentsList(data);
        })
        .catch(error => {
            console.error('Error fetching comments:', error);
        });
}

function updateCommentsList(incidents) {
    const incidentsContainer = document.getElementById('incidents-container');
    incidentsContainer.innerHTML = '';

    incidents.forEach(incident => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';

        const incidentId = incident.incident_id || 'N/A';
        const description = incident.description || 'No description available';
        const timestamp = incident.timestamp ? new Date(incident.timestamp).toLocaleString() : 'Unknown';

        let commentsHtml = '';
        const comments = incident.comments || [];
        comments.forEach(comment => {
            const commentDescription = comment.description || 'No description available';
            const commentTimestamp = comment.timestamp ? new Date(comment.timestamp).toLocaleString() : 'Unknown';
            commentsHtml += `
                <strong>Comment Description:</strong> ${commentDescription}<br>
                <strong>Comment Timestamp:</strong> ${commentTimestamp}<br><br>
            `;
        });

        listItem.innerHTML = `
            <strong>Incident ID:</strong> ${incidentId}<br>
            <strong>Description:</strong> ${description}<br>
            <strong>Timestamp:</strong> ${timestamp}<br><br>
            <strong>Comments:</strong><br>${commentsHtml}
        `;

        incidentsContainer.appendChild(listItem);
    });
}

document.addEventListener('DOMContentLoaded', fetchComments);

let cameraIdCounter = 2;

document.getElementById('camera-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const cameraUrl = document.getElementById('camera_url').value;
    const cameraId = cameraIdCounter++;

    fetch('/add_camera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: cameraId, url: cameraUrl })
    })
    .then(response => response.text())
    .then(text => {
        try {
            const data = JSON.parse(text);
            if (data.error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error,
                });
            } else {
                Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: data.message,
                });
                updateCameraFeeds(data.camera);
            }
        } catch (e) {
            Swal.fire({
                icon: 'error',
                title: 'Parsing Error',
                text: 'Error parsing response: ' + e.message,
            });
        }
    })
    .catch(error => {
        Swal.fire({
            icon: 'error',
            title: 'Fetch Error',
            text: 'An error occurred: ' + error.message,
        });
    });
});

function updateCameraFeeds(camera) {
    const container = document.getElementById('camera-feeds-container');
    const video = document.createElement('video');
    video.src = camera.url;
    video.controls = true;
    container.appendChild(video);
}

document.addEventListener('DOMContentLoaded', function() {
    $('#parking-tab-v2').on('shown.bs.tab', function() {
        fetchCameras();
    });

    function fetchCameras() {
        fetch('/video_feed/2')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const runManagement2ModalBtn = document.getElementById('run-management-2-modal-btn');
            const cameraContainer = document.getElementById('camera-feeds-container');
            
            if (data.error) {
                console.error('No cameras available:', data.error);
                cameraContainer.innerHTML = "<p>No cameras available.</p>";
                runManagement2ModalBtn.style.display = 'none'; // Hide the button
            } else {
                console.log(data);
                cameraContainer.innerHTML = '';
                let camerasAvailable = false;

                data.forEach(camera => {
                    if (camera.id === 2) {
                        const videoElement = document.createElement('img');
                        videoElement.src = '/video_feed_parking_space_2';
                        videoElement.width = "640";
                        videoElement.height = "480";
                        cameraContainer.appendChild(videoElement);
                        camerasAvailable = true;
                    }
                });

                if (camerasAvailable) {
                    runManagement2ModalBtn.style.display = 'block'; // Show the button
                } else {
                    runManagement2ModalBtn.style.display = 'none'; // Hide the button
                }
            }
        })
        .catch(error => {
            console.error('Error fetching cameras:', error);
            document.getElementById('camera-feeds-container').innerHTML = "<p>No camera Available.</p>";
            document.getElementById('run-management-2-modal-btn').style.display = 'none'; // Hide the button
        });
    }
});
