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

     // Save the timestamp to the backend
     saveFullParkingTimestamp();
 } else if (parseInt(parkingAvailable, 10) > 0) {
     isAlertShown = false;
 }
}

function saveFullParkingTimestamp() {
 const now = new Date();
 const offset = 8 * 60;
 const localTime = new Date(now.getTime() + offset * 60 * 1000);
 const timestamp = localTime.toISOString().replace('Z', '+08:00');

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
         console.log('Fetched data:', data);  // Check what data is received
         updateParkingData(data);
     })
     .catch(error => {
         console.error('Error fetching parking information:', error);
     });
}


fetchParkingData();
setInterval(fetchParkingData, 1000);
