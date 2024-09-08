<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ParkWatch Dashboard</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <!-- SweetAlert2 CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <style>
        body {
            background-color: #f5f5f5;
            padding-top: 60px; /* Add padding to account for the fixed header */
        }

        .header-section {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            display: flex;
            align-items: center;
            background-color: #6390D3;
            padding: 10px 20px;
            border-radius: 0 0 5px 5px;
            z-index: 1000; /* Ensure the header is above other content */
        }

        .header-section .navbar {
            flex: 1;
            display: flex;
            justify-content: center;
            padding: 0;
        }

        .header-section img {
            height: 40px; /* Adjust the logo height */
        }

        .header-section h1 {
            color: white;
            font-size: 1.5em;
            margin: 0;
        }

        .header-section .navbar-nav {
            flex-direction: row;
        }

        .header-section .nav-item {
            color: white;
            font-size: 16px;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 5px;
            transition: background-color 0.3s, color 0.3s;
        }

        .header-section .nav-item:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        .header-section .current-time {
            color: white;
            font-size: 1.2em;
            margin-left: auto; /* Pushes the time to the right */
        }

        .main-content {
            display: flex;
            justify-content: space-between;
            margin-top: 80px; /* Add margin-top to account for fixed header */
        }

        .info-boxes {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin: 0 20px;
        }

        .info-box {
            flex: 1;
            max-width: 100%;
            margin-bottom: 20px;
        }

        .info-box .card {
            border: none;
            border-radius: 10px;
            text-align: center;
            padding: 10px;
            background-color: white;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .info-box .card img {
            width: 60px;
            height: 60px;
        }

        .info-box .card h2 {
            font-size: 1.8em;
            margin: 0;
        }

        .info-box .card p {
            font-size: 0.9em;
        }

        .cctv-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0 20px;
        }

        .cctv-container h2 {
            margin-bottom: 20px;
        }

        #video_feed {
            width: 100%;
            max-width: 1200px;
            height: auto;
            border-radius: 10px;
        }

        .modal-content {
            border-radius: 10px;
        }

        .modal-header,
        .modal-footer {
            border: none;
        }

        .modal-body {
            padding: 20px;
        }
    </style>
</head>

<body>
    <!-- Header Section -->
    <div class="header-section">
        <a class="navbar-brand" href="#">
            <img src="{{ url_for('static', filename='logo.png') }}" alt="ParkWatch Logo" height="100px"> <!-- Adjust path to your logo -->
        </a>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="#">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" onclick="showReportIncidentModal()">Report Incident</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" onclick="generateReport()">Generate Report</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" onclick="showInstructions()">Run Management</a>
                    </li>
                </ul>
            </div>
        </nav>
        <div class="current-time" id="current-date-time"></div>
    </div>

    <!-- Main Content -->
    <div class="container mt-4">
        <div class="main-content">
            <!-- Info Boxes Section -->
            <div class="info-boxes">
                <div class="info-box">
                    <div class="card bg-primary text-white">
                        <div class="card-body d-flex align-items-center">
                            <img src="../static/total-vehicles-icon.png" alt="Total Vehicles">
                            <div>
                                <h2 id="total-vehicles">9</h2>
                                <p>Total Vehicles Parked</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="info-box">
                    <div class="card bg-success text-white">
                        <div class="card-body d-flex align-items-center">
                            <img src="/static/parking-available-icon.png" alt="Parking Available">
                            <div>
                                <h2 id="parking-available">0</h2>
                                <p>Parking Slot Available</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="info-box">
                    <div class="card bg-warning text-white">
                        <div class="card-body d-flex align-items-center">
                            <img src="/static/slots-reserved-icon.png" alt="Slots Reserved">
                            <div>
                                <h2 id="slots-reserved">0</h2>
                                <p>Total Slot Reserved</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CCTV Section -->
            <div class="cctv-container">
                <!-- <h2>CCTV CAM</h2> -->
                <div>
                    <img id="video_feed" src="{{ url_for('video_feed', camera_id=1) }}" alt="CCTV Feed" class="img-fluid">
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for Reporting an Incident -->
    <div id="report-incident-modal" class="modal fade" tabindex="-1" role="dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Report an Incident</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="incident-report-form">
                        <div class="form-group">
                            <textarea id="incident-description" class="form-control" placeholder="Describe the incident here" required></textarea>
                        </div>
                        <input type="hidden" id="incident-timestamp" value="">
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="submitIncidentReport()">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for Instructions -->
    <div id="instructions-modal" class="modal fade" tabindex="-1" role="dialog">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Instructions</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
    <p>1. **Left Click**: Add a new parking space or rectangle.</p>
    <p>2. **Right Click**: Delete an existing parking space or rectangle. (Single click for landscape, double click for portrait)</p>
    <p>3. **Middle Click**: Toggle the reservation status of a parking space.</p>
    <p>4. **Press 'D' Key**: Toggle delete mode. When in delete mode, right-click will delete the selected parking space.</p>
    <p>5. **Press 'S' Key**: Save the current configuration.</p>
    <p>6. **Press 'R' Key**: Resize the parking space. You need to drag it to adjust the size.</p>
</div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" onclick="runManagement()">Run Management</button>
                </div>
            </div>
        </div>
    </div>

    <!-- SweetAlert2 JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <!-- Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="{{ url_for('static', filename='js/scripts.js') }}"></script>
</body>

</html>
