document.addEventListener('DOMContentLoaded', function() {
    // Initially hide the tab
    const parkingTab = document.getElementById('parking-tab-v3');
    parkingTab.style.display = 'none';  // Hide the tab initially
    const runManagementButton = document.getElementById('run-management-3-modal-btn');


    // Function to update the parking information for Parking Interface 3
    function updateParkingInfo3() {
        fetch('/get_parking_info3')
            .then(response => response.json())
            .then(data => {
                // Update the parking info elements
                document.getElementById('total-vehicles3').innerText = data.totalVehicles || 0;
                document.getElementById('parking-available3').innerText = data.parkingAvailable || 0;
                document.getElementById('slots-reserved3').innerText = data.slotsReserved || 0;
            })
            .catch(error => {
                console.error('Error fetching parking info:', error);
            });
    }

    // Function to check if the video feed is available and show the tab only if the feed loads
    function checkVideoFeedAvailability() {
        const cameraFeed = document.getElementById('camera-feed3');

        // Set the video feed source dynamically
        const videoFeedUrl = "/video_feed/3"; // Replace this with the correct URL, if needed
        console.log("Video feed URL:", videoFeedUrl);  // Debugging: Check if the URL is correct

        // Set the video feed source
        cameraFeed.src = videoFeedUrl;

        // Use 'onload' to check if the video feed loaded correctly
        cameraFeed.onload = function() {
            console.log("Video feed loaded successfully");
            parkingTab.style.display = 'block'; // Show the tab if feed is available
            runManagementButton.style.display = 'block'; // Show the button if feed is available

        };

        // Use 'onerror' to check if the video feed failed to load (404 error for unavailable source)
        cameraFeed.onerror = function() {
            console.log("Error loading video feed");
            parkingTab.style.display = 'none'; 
            runManagementButton.style.display = 'none'; // Show the button if feed is available
            // Hide the tab if feed is not available
        };
    }

    // When the tab is shown, check if the camera feed is available
    $('#parking-tab-v3').on('shown.bs.tab', function() {
        console.log("Tab is shown, checking video feed availability...");
        // Check video feed availability when the tab is shown
        checkVideoFeedAvailability();
    });

    // Call the functions initially
    updateParkingInfo3();

    // Refresh the parking info and video feed every 10 seconds
    setInterval(() => {
        updateParkingInfo3();
        checkVideoFeedAvailability();  // Re-check the video feed availability every 10 seconds
    }, 1000); // 10 seconds interval
});
function runManagement3() {
    fetch('/run_management3')
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