let isAlertShown = false;
function updateParkingData(data) {
 // Ensure data has the correct properties
 const { totalVehicles = 'N/A', parkingAvailable = 'N/A', slotsReserved = 'N/A' } = data;

 document.getElementById('total-vehicles2').innerText = totalVehicles;
 document.getElementById('parking-available2').innerText = parkingAvailable;
 document.getElementById('slots-reserved2').innerText = slotsReserved;

 if (parseInt(parkingAvailable, 10) === 0 && !isAlertShown) {
     Swal.fire({
         icon: 'warning',
         title: 'Alert',
         text: 'Parking slots 2 are full!',
         showConfirmButton: true
     });
     isAlertShown = true;

     saveFullParkingTimestamp2();
 } else if (parseInt(parkingAvailable, 10) > 0) {
     isAlertShown = false;
 }
}

function saveFullParkingTimestamp2() {
    const now = new Date();
    const offset = 8 * 60;
    const localTime = new Date(now.getTime() + offset * 60 * 1000);
    const timestamp = localTime.toISOString().replace('Z', '+08:00');
    
    console.log("Sending timestamp:", timestamp); // Debug
   
    fetch('/save_full_parking_timestamp2', {
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
   

function fetchParkingData() {
 fetch('/get_parking_info2')  // Ensure this matches your Flask route
     .then(response => {
         if (response.ok) {
             return response.json();
         }
         throw new Error('Network response was not ok');
     })
     .then(data => {
        //  console.log('Fetched data:', data);  // Check what data is received
         updateParkingData(data);
     })
     .catch(error => {
         console.error('Error fetching parking information:', error);
     });
}


fetchParkingData();
setInterval(fetchParkingData, 1000);
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function generateReport() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    // Validate the date inputs
    if (!startDate || !endDate) {
        Swal.fire({
            title: 'Error',
            text: 'Please select both start and end dates.',
            icon: 'error',
        });
        return;
    }

    if (new Date(startDate) > new Date(endDate)) {
        Swal.fire({
            title: 'Error',
            text: 'Start date cannot be later than end date.',
            icon: 'error',
        });
        return;
    }

    fetch(`/generate_report?start_date=${startDate}&end_date=${endDate}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch the report from the server.');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                Swal.fire({
                    title: 'Error',
                    text: data.error,
                    icon: 'error',
                });
            } else {
                const { report } = data; // Extract the report string
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF();

                // Title Section
                doc.setFontSize(22);
                doc.setFont("helvetica", "bold");
                doc.setTextColor(0, 102, 204);
                doc.text('PARKWATCH', 15, 20);
                doc.setFontSize(18);
                doc.text(`Parking Report: ${startDate} to ${endDate}`, 15, 30);

                // Add a line below the title
                doc.setDrawColor(0, 0, 0);
                doc.line(15, 35, 195, 35);

                // Split the report into lines
                const reportLines = report.split('\n');
                const colX = [15, 60, 110, 195]; // Column positions
                const colWidths = [45, 50, 85]; // Column widths

                let y = 45; // Starting Y position
                doc.setFontSize(12);
                doc.setFont("helvetica", "normal");
                doc.setTextColor(0, 0, 0);

                // Process the report lines
                reportLines.forEach(line => {
                    if (line.trim()) {
                        if (line.startsWith('Total')) {
                            doc.text(line, 15, y);
                            y += 10;
                        } else if (line.startsWith('Arrival and Departure Information:')) {
                            y += 5;
                            doc.setFont("helvetica", "bold");
                            doc.text(line, 15, y);
                            y += 10;
                            doc.setFont("helvetica", "normal");

                            // Add table headers
                            doc.setFontSize(10);
                            doc.text('Plate Number', colX[0] + 2, y);
                            doc.text('Arrival', colX[1] + 2, y);
                            doc.text('Departure', colX[2] + 2, y);

                            doc.setDrawColor(0, 0, 0);
                            doc.rect(colX[0], y - 5, colWidths[0], 10);
                            doc.rect(colX[1], y - 5, colWidths[1], 10);
                            doc.rect(colX[2], y - 5, colWidths[2], 10);

                            y += 10;
                        } else {
                            const parts = line.split(',').map(item => item.trim());
                            if (parts.length >= 2) {
                                const plateInfo = parts[0].replace('Plate Number:', '').trim();
                                const arrivalInfo = parts[1].replace('Arrival:', '').trim();
                                const departureInfo = parts[2] ? parts[2].replace('Departure:', '').trim() : 'N/A';

                                doc.text(plateInfo, colX[0] + 2, y);
                                doc.text(arrivalInfo, colX[1] + 2, y);
                                doc.text(departureInfo, colX[2] + 2, y);

                                doc.rect(colX[0], y - 5, colWidths[0], 10);
                                doc.rect(colX[1], y - 5, colWidths[1], 10);
                                doc.rect(colX[2], y - 5, colWidths[2], 10);

                                y += 10;
                            }
                        }
                    }
                });

                const pageCount = doc.internal.getNumberOfPages();
                for (let i = 1; i <= pageCount; i++) {
                    doc.setPage(i);
                    doc.setFontSize(10);
                    doc.text(`Page ${i} of ${pageCount}`, 180, 290, { align: "right" });
                }

                doc.save(`Parking_Report_${startDate}_to_${endDate}.pdf`);
            }

            $('#generateReportModal').modal('hide');
        })
        .catch(error => {
            console.error('Error generating report:', error);

            Swal.fire({
                title: 'Error',
                text: 'Failed to generate report. Please try again.',
                icon: 'error',
            });
        });
}




////////////////////////////////////////////////////////////////////////////
//    // Fetch parking data for Camera ID 3
//    function fetchParkingDataForId3() {
//     fetch('/get_parking_info3')
//         .then(response => {
            
//             if (response.ok) {
//                 return response.json();
//             }
//             throw new Error('Network response was not ok');
//         })
//         .then(data => {
//             updateParkingDataForId3(data);
//         })
//         .catch(error => {
//             console.error('Error fetching parking information for ID 3:', error);
//         });
// }

// function updateParkingDataForId3(data) {
//     // Ensure data has the correct properties
//     const { totalVehicles = 'N/A', parkingAvailable = 'N/A', slotsReserved = 'N/A' } = data;

//     document.getElementById('total-vehicles3').innerText = totalVehicles;
//     document.getElementById('parking-available3').innerText = parkingAvailable;
//     document.getElementById('slots-reserved3').innerText = slotsReserved;

//     if (parseInt(parkingAvailable, 10) === 0 && !isAlertShown) {
//         Swal.fire({
//             icon: 'warning',
//             title: 'Alert',
//             text: 'Parking slots 3 are full!',
//             showConfirmButton: true
//         });
//         isAlertShown = true;

//         saveFullParkingTimestamp3();
//     } else if (parseInt(parkingAvailable, 10) > 0) {
//         isAlertShown = false;
//     }
// }

// function saveFullParkingTimestamp3() {
//     const now = new Date();
//     const offset = 8 * 60; // Adjust the offset for your timezone if needed
//     const localTime = new Date(now.getTime() + offset * 60 * 1000);
//     const timestamp = localTime.toISOString().replace('Z', '+08:00');
    
//     fetch('/save_full_parking_timestamp3', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ timestamp })
//     })
//     .then(response => {
//         if (response.ok) {
//             console.log('Timestamp saved successfully for Camera ID 3.');
//         } else {
//             console.error('Failed to save timestamp for Camera ID 3.');
//         }
//     })
//     .catch(error => {
//         console.error('Error saving timestamp for Camera ID 3:', error);
//     });
// }
// fetchParkingDataForId3();
// setInterval(fetchParkingDataForId3, 1000);