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

        // Get selected start and end dates
        let startDate = $('#startDate').val();
        let endDate = $('#endDate').val();

        // Fetch reports from the backend
        $.ajax({
            url: '/fetch_user_reports',
            method: 'GET',
            success: function(data) {
                // Filter reports based on the selected date range
                const filteredReports = data.filter(report => {
                    const reportDate = new Date(report.timestamp);
                    const start = startDate ? new Date(startDate) : new Date('1970-01-01');
                    const end = endDate ? new Date(endDate) : new Date();
                    return reportDate >= start && reportDate <= end;
                });

                // Display the filtered reports
                if (filteredReports.length > 0) {
                    filteredReports.forEach(function(report) {
                        let imageElement = report.image_url 
                            ? `<div class="col-3" style="max-width: 150px; max-height: 150px;">
                                <img src="${report.image_url}" alt="Incident Image" class="img-fluid" style="max-width: 100%; max-height: 100%; object-fit: cover;">
                               </div>`
                            : '';

                        let reportItem = `<li class="list-group-item" style="background-color: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
                                            <div class="row">
                                                ${imageElement}
                                                <div class="col-9">
                                                    <strong>Name:</strong> ${report.name} <br>
                                                    <strong>Description:</strong> ${report.description} <br>
                                                    <strong>Timestamp:</strong> ${report.timestamp}
                                                </div>
                                            </div>
                                          </li>`;
                        $('#reportList').append(reportItem);
                    });
                } else {
                    $('#reportList').append('<li class="list-group-item">No reports available for the selected date range</li>');
                }
            },
            error: function(error) {
                console.log('Error fetching reports:', error);
            }
        });
    });
});

// Function to download PDF
function downloadPDF() {
    // Get selected start and end dates
    let startDate = $('#startDate').val();
    let endDate = $('#endDate').val();

    // Fetch reports from the backend
    $.ajax({
        url: '/fetch_user_reports',
        method: 'GET',
        success: function(data) {
            // Filter reports based on the selected date range
            const filteredReports = data.filter(report => {
                const reportDate = new Date(report.timestamp);
                const start = startDate ? new Date(startDate) : new Date('1970-01-01');
                const end = endDate ? new Date(endDate) : new Date();
                return reportDate >= start && reportDate <= end;
            });

            if (filteredReports.length > 0) {
                // Create HTML content for the PDF
                let reportHTML = `
                    <h2>PARKWATCH User Reports</h2>
                    <p>Generated on: ${new Date().toLocaleString()}</p>
                    <p><strong>From:</strong> ${startDate ? new Date(startDate).toLocaleDateString() : 'Any Date'} 
                       <strong>To:</strong> ${endDate ? new Date(endDate).toLocaleDateString() : 'Any Date'}</p>
                    <table style="width: 100%; border: 1px solid #ccc; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="border: 1px solid #ccc; padding: 8px;">Image</th>
                                <th style="border: 1px solid #ccc; padding: 8px;">Name</th>
                                <th style="border: 1px solid #ccc; padding: 8px;">Description</th>
                                <th style="border: 1px solid #ccc; padding: 8px;">Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>`;

                filteredReports.forEach(report => {
                    let imageElement = '';
                    if (report.image_url) {
                        imageElement = `<img src="${report.image_url}" alt="Incident Image" style="width: 100px; height: auto;">`;
                    } else {
                        imageElement = `<span>No image available</span>`;
                    }

                    reportHTML += `
                        <tr>
                            <td style="border: 1px solid #ccc; padding: 8px;">
                                ${imageElement}
                            </td>
                            <td style="border: 1px solid #ccc; padding: 8px;">${report.name}</td>
                            <td style="border: 1px solid #ccc; padding: 8px;">${report.description}</td>
                            <td style="border: 1px solid #ccc; padding: 8px;">${report.timestamp}</td>
                        </tr>
                    `;
                });

                reportHTML += '</tbody></table>';

                // Open a new window with the HTML content for printing
                const printWindow = window.open('', '', 'width=800,height=600');
                printWindow.document.write(`
                    <html>
                        <head>
                            <title>User Reports</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 20px; }
                                h2 { text-align: center; }
                                table { width: 100%; border-collapse: collapse; }
                                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                            </style>
                        </head>
                        <body>
                            ${reportHTML}
                        </body>
                    </html>
                `);

                // Wait for all images to load before printing
                const images = printWindow.document.querySelectorAll('img');
                let loadedImagesCount = 0;

                images.forEach((img) => {
                    img.onload = () => {
                        loadedImagesCount++;
                        if (loadedImagesCount === images.length) {
                            printWindow.document.close();
                            printWindow.print(); // Open the print dialog to save as PDF
                            setTimeout(() => printWindow.close(), 1000);
                        }
                    };
                    img.onerror = () => printWindow.document.close();
                });

                if (images.length === 0) {
                    printWindow.document.close();
                    printWindow.print(); // Open the print dialog to save as PDF
                    setTimeout(() => printWindow.close(), 1000);
                }
            } else {
                Swal.fire({
                    title: 'No Reports',
                    text: 'No reports available for the selected date range.',
                    icon: 'warning',
                });
            }
        },
        error: function(error) {
            console.log('Error fetching reports:', error);
        }
    });
}
