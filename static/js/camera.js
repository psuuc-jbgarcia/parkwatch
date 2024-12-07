// Function to open the Camera Plate Management Modal and fetch cameras
let storedID="";
function openCameraPlateModal() {
    fetchCameraPlateData();
    const modal = new bootstrap.Modal(document.getElementById('customCameraManagementModalForPlate'));
    modal.show();
}

// Function to fetch camera plate data and populate the table
function fetchCameraPlateData() {
    fetch('/fetch_cameras_plate')  // The Flask endpoint to fetch camera plate data
    .then(response => response.json())
    .then(data => {
        const cameraList = document.getElementById('customCameraList');
        cameraList.innerHTML = '';  // Clear the table before inserting new data

        // Check if camera plate data exists
        if (data.length === 0) {
            cameraList.innerHTML = '<tr><td colspan="4">No camera plates found</td></tr>';
            return;
        }

        // Loop through the camera plate data and append rows to the table
        data.forEach((camera, index) => {
            const row = document.createElement('tr');
            row.innerHTML = ` 
                <td>${index + 1}</td>
                <td>${camera.cameraUrl}</td>
                <td>${camera.cameraPurpose}</td>
                <td>
                    <button class="btn btn-warning" onclick="editCameraPlate('${camera.id}')">Edit</button>
                    <button class="btn btn-danger" onclick="deleteCameraPlate('${camera.id}')">Delete</button>
                </td>
            `;
            cameraList.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error fetching camera plates:', error);
        Swal.fire({
            title: 'Error!',
            text: 'There was a problem fetching the camera plates.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    });
}

// Function to open the Add Camera Plate Modal (or Edit if camera data exists)
function openCameraPlateModalForAdd() {
    const modalElement = document.getElementById('customAddEditCameraModalForPlate');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else {
        console.error('Modal with id customAddEditCameraModalForPlate not found.');
    }
}

// Function to populate the Add/Edit Camera Plate Modal with data (for editing)
function editCameraPlate(cameraId) {
    fetch(`/fetch_camera_by_id/${cameraId}`)  // Fetch camera plate data by ID
    .then(response => response.json())
    .then(camera => {
        console.log('cameraId:', cameraId);  // Debugging line
        storedID=cameraId;
        // Populate the modal with the camera plate data
        document.getElementById('customCameraPlateUrl').value = camera.cameraUrl;
        document.getElementById('customCameraPlatePurpose').value = camera.cameraPurpose;
        document.getElementById('customCameraPlateId').value = camera.id;  // Set the hidden ID field

        const modal = new bootstrap.Modal(document.getElementById('customAddEditCameraModalForPlate'));
        modal.show();
    })
    .catch(error => {
        console.error('Error fetching camera plate data for editing:', error);
        Swal.fire({
            title: 'Error!',
            text: 'There was a problem fetching the camera plate data.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    });
}

// Function to save camera plate (either add or edit)
function saveCameraPlate() {
    const cameraIdElement = document.getElementById('customCameraPlateId');
    const cameraUrlElement = document.getElementById('customCameraPlateUrl');
    const cameraPurposeElement = document.getElementById('customCameraPlatePurpose');
    
    if (!cameraIdElement || !cameraUrlElement || !cameraPurposeElement) {
        console.error('One or more form elements are missing!');
        return;
    }

    const cameraId = cameraIdElement.value;
    const cameraUrl = cameraUrlElement.value;
    const cameraPurpose = cameraPurposeElement.value;

    // Prepare data to be sent to the server
    const cameraData = {
        cameraUrl: cameraUrl,
        cameraPurpose: cameraPurpose
    };

    if (cameraId) {
        // If cameraId is set, update the existing camera plate
        fetch(`/update_camera/${storedID}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cameraData),
        })
        .then(response => response.json())
        .then(data => {
            Swal.fire({
                title: 'Success!',
                text: 'Camera plate updated successfully.',
                icon: 'success',
                confirmButtonText: 'OK'
            });
            fetchCameraPlateData();  // Refresh the camera list
        })
        .catch(error => {
            console.error('Error updating camera plate:', error);
            Swal.fire({
                title: 'Error!',
                text: 'There was a problem updating the camera plate.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    } else {
        // Otherwise, add a new camera plate
        fetch('/add_camera_plate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cameraData),
        })
        .then(response => response.json())
        .then(data => {
            Swal.fire({
                title: 'Success!',
                text: 'Camera plate added successfully.',
                icon: 'success',
                confirmButtonText: 'OK'
            });
            fetchCameraPlateData();  // Refresh the camera list
        })
        .catch(error => {
            console.error('Error adding camera plate:', error);
            Swal.fire({
                title: 'Error!',
                text: 'There was a problem adding the camera plate.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    }

    // Close the modal after saving
    const modal = new bootstrap.Modal(document.getElementById('customAddEditCameraModalForPlate'));
    modal.hide();
}

// Function to delete a camera plate using SweetAlert for confirmation
function deleteCameraPlate(cameraId) {
    // Use SweetAlert for confirmation
    Swal.fire({
        title: 'Are you sure?',
        text: 'You will not be able to recover this camera plate!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            // If confirmed, proceed with deletion
            fetch(`/delete_camera_plate/${cameraId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message with SweetAlert
                    Swal.fire({
                        title: 'Deleted!',
                        text: 'The camera plate has been deleted.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    });
                    fetchCameraPlateData();  // Refresh the camera list after deletion
                } else {
                    // Show error message with SweetAlert
                    Swal.fire({
                        title: 'Error!',
                        text: 'There was a problem deleting the camera plate.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                }
            })
            .catch(error => {
                console.error('Error deleting camera plate:', error);
                // Show error message with SweetAlert in case of an exception
                Swal.fire({
                    title: 'Error!',
                    text: 'An unexpected error occurred.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            });
        }
    });
}
