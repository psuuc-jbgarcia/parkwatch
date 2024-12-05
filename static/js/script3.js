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
                        // Check if image_url exists and render the image with a fixed max width and height
                        let imageElement = report.image_url 
                            ? `<div class="col-3" style="max-width: 150px; max-height: 150px;">
                                <img src="${report.image_url}" alt="Incident Image" class="img-fluid" style="max-width: 100%; max-height: 100%; object-fit: cover;">
                               </div>`
                            : '';  // If no image URL, leave it empty

                        // Create the report item with Bootstrap grid layout (image on the left)
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


function downloadPDF() {
    // Fetch reports from the Flask backend
    fetch('/fetch_user_reports')
        .then(response => response.json())
        .then(data => {
            // Check if the data is not empty
            if (data.length > 0) {
                // Create a new jsPDF instance
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF();

                // Set title style
                doc.setFontSize(22);
                doc.setFont("helvetica", "bold");
                doc.setTextColor(0, 0, 0); // Black color
                doc.text('PARKWATCH User Reports', 15, 20); // Title
                doc.setFontSize(18);
                doc.text(`Report Generated on: ${new Date().toLocaleString()}`, 15, 30);

                // Prepare data for the table
                const reportData = data.map(report => [
                    report.name, 
                    report.description, 
                    report.timestamp
                ]);

                // Starting position for the table
                let x = 15;
                let y = 40;
                const rowHeight = 10;
                const columnWidth = [60, 80, 40];  // Define column widths

                // Table Header
                doc.setFontSize(12);
                doc.setFont("helvetica", "bold");
                doc.text('Name', x + 2, y + 7); // Slightly offset text for padding
                doc.text('Description', x + columnWidth[0] + 2, y + 7);
                doc.text('Timestamp', x + columnWidth[0] + columnWidth[1] + 2, y + 7);

                // Draw table header border
                doc.setDrawColor(0, 0, 0); // Black border
                doc.rect(x, y, columnWidth[0], rowHeight); // Name column
                doc.rect(x + columnWidth[0], y, columnWidth[1], rowHeight); // Description column
                doc.rect(x + columnWidth[0] + columnWidth[1], y, columnWidth[2], rowHeight); // Timestamp column

                y += rowHeight; // Move to the next row

                // Table Body
                doc.setFontSize(10);
                doc.setFont("helvetica", "normal");
                data.forEach(report => {
                    // Add text to the table
                    doc.text(report.name, x + 2, y + 7);
                    doc.text(report.description, x + columnWidth[0] + 2, y + 7);
                    doc.text(report.timestamp, x + columnWidth[0] + columnWidth[1] + 2, y + 7);

                    // Draw borders for each row
                    doc.rect(x, y, columnWidth[0], rowHeight); // Name column
                    doc.rect(x + columnWidth[0], y, columnWidth[1], rowHeight); // Description column
                    doc.rect(x + columnWidth[0] + columnWidth[1], y, columnWidth[2], rowHeight); // Timestamp column

                    y += rowHeight; // Move to the next row

                    // Check if the page is about to end
                    if (y > 270) {
                        doc.addPage();
                        y = 20; // Reset y for new page

                        // Redraw the table header on the new page
                        doc.setFontSize(12);
                        doc.setFont("helvetica", "bold");
                        doc.text('Name', x + 2, y + 7);
                        doc.text('Description', x + columnWidth[0] + 2, y + 7);
                        doc.text('Timestamp', x + columnWidth[0] + columnWidth[1] + 2, y + 7);

                        // Draw table header border
                        doc.rect(x, y, columnWidth[0], rowHeight); // Name column
                        doc.rect(x + columnWidth[0], y, columnWidth[1], rowHeight); // Description column
                        doc.rect(x + columnWidth[0] + columnWidth[1], y, columnWidth[2], rowHeight); // Timestamp column

                        y += rowHeight; // Move to the next row
                    }
                });

                // Save the generated PDF
                doc.save('user_reports.pdf');
            } else {
                // If no reports are found
                Swal.fire({
                    title: 'No Reports',
                    text: 'No reports available to download.',
                    icon: 'warning',
                });
            }
        })
        .catch(error => {
            console.error("Error fetching reports:", error);
            Swal.fire({
                title: 'Error',
                text: 'Failed to fetch reports for PDF generation.',
                icon: 'error',
            });
        });
}
