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
            return response.json(); // This should be returning JSON
        })
        .then(data => {
            if (data.error) {
                Swal.fire({
                    title: 'Error',
                    text: data.error,
                    icon: 'error',
                });
            } else {
                const { report } = data; // Accessing the report from data
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF();

                // Add content to the PDF
                doc.text(`Parking Report for ${selectedDate}`, 10, 10);
                doc.text(report, 10, 20); // Make sure to correctly use the report content

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