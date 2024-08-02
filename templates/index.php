<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parking Space Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
            margin: 0;
            padding: 0;
        }
        .header {
            width: 100%;
            background-color: #6390D3;
            color: #ffffff;
            padding: 10px 0;
            text-align: center;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
        }
        .header h1 {
            margin: 0;
        }
        .header .date-time {
            font-size: 1.2em;
        }
        .menu {
            display: flex;
            justify-content: space-around;
            align-items: center;
            background-color: #6390D3;
            color: #ffffff;
            padding: 10px 0;
            position: fixed;
            width: 100%;
            top: 60px;
            left: 0;
            z-index: 1000;
        }
        .menu a {
            color: #ffffff;
            text-decoration: none;
            font-size: 1.2em;
        }
        .menu button {
            background-color: transparent;
            color: #ffffff;
            border: 1px solid #ffffff;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.2em;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
            margin-top: 140px;
        }
        .dashboard {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-right: 20px;
        }
        .info-box {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            color: #000000;
        }
        .info-box h2 {
            margin: 0;
            font-size: 2em;
        }
        .info-box p {
            margin: 5px 0;
            font-size: 1.2em;
        }
        .info-box .total-vehicles {
            background-color: #6390D3;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .info-box .parking-available {
            background-color: #32CD32;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .info-box .slots-reserved {
            background-color: #FFA500;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .info-box .icon {
            margin-right: 10px;
        }
        .cctv-cam {
            flex: 2;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .cctv-cam select {
            margin-bottom: 10px;
            padding: 5px;
            font-size: 1em;
        }
        .cctv-cam img {
            width: 100%;
            max-width: 800px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .cctv-cam h2 {
            text-align: center;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background-color: #fefefe;
            margin: 15% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
            border-radius: 10px;
        }
        .modal-header, .modal-footer {
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }
        .modal-header {
            border-bottom: none;
        }
        .modal-footer {
            border-top: 1px solid #ddd;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }
        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PARKWATCH</h1>
        <div class="date-time">
            <span id="current-date-time">Date and Time</span>
        </div>
    </div>
    <div class="menu" style="margin-top:10px">
        <a href="#">Home</a>
        <a href="#">Reports</a>
        <a href="#">About Us</a>
        <button onclick="showInstructions()">Run Management</button>
    </div>
    <div class="container">
        <div class="dashboard">
            <div class="info-box">
                <div class="total-vehicles">
                    <img src="../static/total-vehicles-icon.png" alt="Total Vehicles" class="icon">
                    <div>
                        <h2 id="total-vehicles">9</h2>
                        <p>Total Vehicles Parked</p>
                    </div>
                </div>
            </div>
            <div class="info-box">
                <div class="parking-available">
                    <img src="/static/parking-available-icon.png" alt="Parking Available" class="icon">
                    <div>
                        <h2 id="parking-available">0</h2>
                        <p>Parking Slot Available</p>
                    </div>
                </div>
            </div>
            <div class="info-box">
                <div class="slots-reserved">
                    <img src="/static/slots-reserved-icon.png" alt="Slots Reserved" class="icon">
                    <div>
                        <h2 id="slots-reserved">0</h2>
                        <p>Total Slot Reserved</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="cctv-cam">
            <h2>CCTV CAM</h2>
            <select id="cameraSelect" onchange="updateCamera()">
                <option value="1">Camera 1</option>
                <option value="2">Camera 2</option>
                <!-- Add more options as needed -->
            </select>
            <img id="video_feed" src="{{ url_for('video_feed', camera_id=1) }}" alt="CCTV Feed">
        </div>
    </div>

    <!-- Modal for Alert -->
    <div id="alert-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span class="close" onclick="closeAlert()">&times;</span>
                <h2>Alert</h2>
            </div>
            <div class="modal-body">
                <p>Parking slots are full!</p>
            </div>
            <div class="modal-footer">
                <button onclick="closeAlert()">Close</button>
            </div>
        </div>
    </div>

    <!-- Modal for Instructions -->
    <div id="instructions-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span class="close" onclick="closeInstructions()">&times;</span>
                <h2>Instructions</h2>
            </div>
            <div class="modal-body">
                <p>1. Left Click: Add a new parking space or rectangle.</p>
                <p>2. Right Click: Delete an existing parking space or rectangle. (Single click for landscape, double click for portrait)</p>
                <p>3. Middle Click: Toggle reservation status of a parking space.</p>
                <p>4. Press 'D' Key: Toggle delete mode. When in delete mode, right-click will delete the selected parking space.</p>
                <p>5. Press 'S' Key: Save the current configuration.</p>
            </div>
            <div class="modal-footer">
                <button onclick="runManagement()">Run Management</button>
            </div>
        </div>
    </div>

    <script>
        let alertShown = false;

        function updateDateTime() {
            const now = new Date();
            const dateTimeString = now.toLocaleString('en-US', { dateStyle: 'full', timeStyle: 'short' });
            document.getElementById('current-date-time').innerText = dateTimeString;
        }
        setInterval(updateDateTime, 1000);
        updateDateTime();

        function updateParkingInfo(data) {
            const { totalVehicles, parkingAvailable, slotsReserved } = data;

            document.getElementById('total-vehicles').innerText = totalVehicles;
            document.getElementById('parking-available').innerText = parkingAvailable;
            document.getElementById('slots-reserved').innerText = slotsReserved;

            if (parseInt(parkingAvailable, 10) === 0 && !alertShown) {
                showAlert();
                alertShown = true;
            } else if (parseInt(parkingAvailable, 10) > 0) {
                alertShown = false;
            }
        }

        function showAlert() {
            const alertModal = document.getElementById('alert-modal');
            alertModal.style.display = 'flex';
            
            setTimeout(() => {
                // closeAlert();
            }, 5000);
        }

        function closeAlert() {
            document.getElementById('alert-modal').style.display = 'none';
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

        function runManagement() {
            fetch('/run_management')
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    }
                    throw new Error('Network response was not ok');
                })
                .then(data => {
                    alert('Management script executed successfully!');
                })
                .catch(error => {
                    console.error('Error executing management script:', error);
                    alert('Failed to execute management script.');
                });
        }

        function showInstructions() {
            document.getElementById('instructions-modal').style.display = 'flex';
        }

        function closeInstructions() {
            document.getElementById('instructions-modal').style.display = 'none';
        }

        function updateCamera() {
            const cameraId = document.getElementById('cameraSelect').value;
            const videoFeed = document.getElementById('video_feed');
            videoFeed.src = `/video_feed/${cameraId}`;
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 's' || event.key === 'S') {
                event.preventDefault();
                alert('Saving configuration...');
            }
        });
    </script>
</body>
</html>
