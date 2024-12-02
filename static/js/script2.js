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
    const selectedDate = document.getElementById('report-date').value;

    fetch(`/generate_report?date=${selectedDate}`)
        .then(response => {
            console.log('Raw response:', response);

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
                const { report } = data; 
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF();

                // Set title style
                doc.setFontSize(22);
                doc.setFont("helvetica", "bold");
                doc.setTextColor(0, 102, 204); // Blue color
                doc.text('PARKWATCH', 15, 20); // System name
                doc.setFontSize(18);
                doc.text(`Parking Report for ${selectedDate}`, 15, 30);

                // Add a line below the title
                doc.setDrawColor(0, 0, 0); // Black color for the line
                doc.line(15, 35, 195, 35); // Draw line from (15,35) to (195,35)

                // Set a smaller font size for the report content
                doc.setFontSize(12);
                doc.setFont("helvetica", "normal");
                doc.setTextColor(0, 0, 0); // Black color for text
                
                // Split the report into lines for proper formatting
                const reportLines = report.split('\n');
                let y = 40; // Start position for the content
                for (let line of reportLines) {
                    doc.text(line, 15, y);
                    y += 10; // Add space between lines
                }

                // Optional: Add page numbers
                const pageCount = doc.internal.getNumberOfPages();
                for (let i = 1; i <= pageCount; i++) {
                    doc.setPage(i);
                    doc.setFontSize(10);
                    doc.text(`Page ${i} of ${pageCount}`, 180, 290, { align: "right" });
                }

                // Save the PDF
                doc.save(`Parking_Report_${selectedDate}.pdf`);
            }

            // Close the modal after generating the report
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