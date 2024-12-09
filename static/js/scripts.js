let alertShown = false;

function updateDateTime() {
    const now = new Date();

    // Update the time in the 'hh:mm:ss AM/PM' format
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric'
    });
    document.getElementById('time').innerText = timeString;

    // Update the date in the '17 September 2024' format
    const dateString = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    document.getElementById('date').innerText = dateString;
}

// Update every second
setInterval(updateDateTime, 1000);

// Call once immediately on page load
updateDateTime();


function updateParkingInfo(data) {
    const { totalVehicles, parkingAvailable, slotsReserved } = data;

    // Update UI
    document.getElementById('total-vehicles').innerText = totalVehicles;
    document.getElementById('parking-available').innerText = parkingAvailable;
    document.getElementById('slots-reserved').innerText = slotsReserved;

    // Retrieve alertShown from localStorage (convert to boolean)
    let alertShown = localStorage.getItem('alertShown') === 'true';

    if (parseInt(parkingAvailable, 10) === 0 && !alertShown) {
        Swal.fire({
            icon: 'warning',
            title: 'Alert',
            text: 'Parking slots are full!',
            showConfirmButton: true
        });

        // Set alertShown to true in localStorage so it persists
        localStorage.setItem('alertShown', 'true');

        // Save the timestamp to the backend (custom function)
        saveFullParkingTimestamp();
    } else if (parseInt(parkingAvailable, 10) > 0) {
        // Reset alertShown when parking becomes available
        localStorage.removeItem('alertShown');
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
function runManagement3() {
    fetch('/run_management3')
    .then(response => {
        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Modification is successful!',
                showConfirmButton: true
            });
            console.log('Management 3 script started.');
        } else {
            console.error('Failed to start management script 3.');
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



// function fetchComments() {
//     fetch('/fetch_comments')
//         .then(response => {
//             if (response.ok) {
//                 return response.json();
//             }
//             throw new Error('Network response was not ok');
//         })
//         .then(data => {
//             updateCommentsList(data);
//         })
//         .catch(error => {
//             console.error('Error fetching comments:', error);
//         });
// }

// function updateCommentsList(incidents) {
//     const incidentsContainer = document.getElementById('incidents-container');
//     incidentsContainer.innerHTML = '';

//     incidents.forEach(incident => {
//         const listItem = document.createElement('li');
//         listItem.className = 'list-group-item';

//         const incidentId = incident.incident_id || 'N/A';
//         const description = incident.description || 'No description available';
//         const timestamp = incident.timestamp ? new Date(incident.timestamp).toLocaleString() : 'Unknown';

//         let commentsHtml = '';
//         const comments = incident.comments || [];
//         comments.forEach(comment => {
//             const commentDescription = comment.description || 'No description available';
//             const commentTimestamp = comment.timestamp ? new Date(comment.timestamp).toLocaleString() : 'Unknown';
//             commentsHtml += `
//                 <strong>Comment Description:</strong> ${commentDescription}<br>
//                 <strong>Comment Timestamp:</strong> ${commentTimestamp}<br><br>
//             `;
//         });

//         listItem.innerHTML = `
//             <strong>Description:</strong> ${description}<br>
//             <strong>Timestamp:</strong> ${timestamp}<br><br>
//             <strong>Comments:</strong><br>${commentsHtml}
//         `;

//         incidentsContainer.appendChild(listItem);
//     });
// }

// document.addEventListener('DOMContentLoaded', fetchComments);

document.getElementById('camera-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const cameraUrl = document.getElementById('camera_url').value;

    fetch('/add_camera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: cameraUrl }) // Remove sending ID from client-side
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
                icon: 'success',
                title: 'Success',
                text: 'Camera Added Successfully',
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
        fetch('/video_feed_parking_space_2')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const runManagement2ModalBtn = document.getElementById('run-management-2-modal-btn');
                const cameraFeed = document.getElementById('camera-feed');
                const parkingTab = document.getElementById('parking-tab-v2'); // Tab to hide

                if (data.error) {
                    console.error('No cameras available:', data.error);
                    cameraFeed.src = ""; // Clear the src if no cameras are available
                    runManagement2ModalBtn.style.display = 'none'; // Hide the button
                    parkingTab.style.display = 'none'; // Hide the tab
                } else {
                    let camerasAvailable = false;

                    data.forEach(camera => {
                        if (camera.id === 2) {
                            cameraFeed.src = '/video_feed/2'; // Set the src to the video feed URL
                            camerasAvailable = true;
                        }
                    });

                    if (camerasAvailable) {
                        runManagement2ModalBtn.style.display = 'block'; // Show the button
                        parkingTab.style.display = 'block'; // Ensure the tab is visible
                    } else {
                        cameraFeed.src = ""; // Clear the src if no relevant camera is found
                        runManagement2ModalBtn.style.display = 'none'; // Hide the button
                        parkingTab.style.display = 'none'; // Hide the tab
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching cameras:', error);
                document.getElementById('camera-feed').src = ""; // Clear the src on error
                document.getElementById('run-management-2-modal-btn').style.display = 'none'; // Hide the button
                document.getElementById('parking-tab-v2').style.display = 'none'; // Hide the tab on error
            });
    }
});


