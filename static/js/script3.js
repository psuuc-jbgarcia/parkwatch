function openManageCamerasModal() {
    fetchCameraUrls(); // Call the function to fetch the camera URLs
    $('#manageCamerasModal').modal('show'); // Show the modal
}

// Function to fetch camera URLs and populate the table
async function fetchCameraUrls() {
    try {
        const response = await fetch('/camera_urls.json');
        if (!response.ok) throw new Error('Network response was not ok');

        const cameraUrls = await response.json();

        const cameraList = document.getElementById('camera-list');
        cameraList.innerHTML = '';

        cameraUrls.forEach((camera) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${camera.id}</td>
                <td>${camera.url}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="openEditCameraModal(${camera.id}, '${camera.url}')">Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="openDeleteCameraModal(${camera.id})">Delete</button>
                </td>
            `;
            cameraList.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching camera URLs:', error);
    }
}

// Function to open edit camera modal
function openEditCameraModal(id, url) {
    document.getElementById('edit-camera-id').value = id;
    document.getElementById('edit-camera-url').value = url;
    $('#editCameraModal').modal('show');
}

// Function to open delete camera modal
function openDeleteCameraModal(id) {
    document.getElementById('delete-camera-id').value = id;
    $('#deleteCameraModal').modal('show');
}

// Function to submit the edited camera data
async function submitEditCamera() {
const id = document.getElementById('edit-camera-id').value;
const url = document.getElementById('edit-camera-url').value;

try {
    const response = await fetch(`/edit_camera/${id}`, { // Adjust this URL based on your backend route
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url })
    });

    if (!response.ok) throw new Error('Failed to update camera');

    // Fetch updated camera URLs and refresh the list
    fetchCameraUrls();
    $('#editCameraModal').modal('hide');
    Swal.fire('Success', 'Camera updated successfully', 'success');
} catch (error) {
    console.error('Error updating camera:', error);
    Swal.fire('Error', 'Failed to update camera', 'error');
}
}

// Function to submit the delete camera request
async function submitDeleteCamera() {
const id = document.getElementById('delete-camera-id').value;

try {
    const response = await fetch(`/delete_camera/${id}`, { // Adjust this URL based on your backend route
        method: 'DELETE'
    });

    if (!response.ok) throw new Error('Failed to delete camera');

    // Fetch updated camera URLs and refresh the list
    fetchCameraUrls();
    $('#deleteCameraModal').modal('hide');
    Swal.fire('Deleted', 'Camera deleted successfully', 'success');
} catch (error) {
    console.error('Error deleting camera:', error);
    Swal.fire('Error', 'Failed to delete camera', 'error');
}
}



    // Function to show the Generate Report modal
    function openReportsModal() {
        $('#reportsModal').modal('show');
    }
    $(document).ready(function() {
    $('#reportsModal').on('show.bs.modal', function () {
        $('#reportList').empty();

        $.ajax({
            url: '/fetch_user_reports',
            method: 'GET',
            success: function(data) {
                if (data.length > 0) {
                    data.forEach(function(report) {
                        let reportItem = `<li class="list-group-item">
                                            <strong>Name:</strong> ${report.name} <br>
                                            <strong>Description:</strong> ${report.description} <br>
                                            <strong>Timestamp:</strong> ${report.timestamp}
                                          </li>`;
                        $('#reportList').append(reportItem);
                    });
                } else {
                    $('#reportList').append('<li class="list-group-item">No reports available</li>');
                }
            },
            error: function(err) {
                console.error("Error fetching reports:", err);
                $('#reportList').append('<li class="list-group-item text-danger">Error fetching reports</li>');
            }
        });
    });
});