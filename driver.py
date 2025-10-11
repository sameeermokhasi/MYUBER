from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import sys

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'

# --- "STREET RIDER" DARK MODE INTERFACE WITH MAP PANEL ---
DRIVER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Street Rider | Driver Portal</title>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    
    <style>
        :root {
            --bg-color: #1a1a1a;
            --surface-color: #2c2c2c;
            --primary-color: #ffc400;
            --text-primary: #ffffff;
            --text-secondary: #aaaaaa;
            --success-color: #00e676;
            --danger-color: #ff1744;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        /* --- AUTHENTICATION STYLES --- */
        .auth-container {
            background-color: var(--surface-color);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            overflow: hidden;
            max-width: 450px;
            width: 100%;
            padding: 40px;
            text-align: center;
            border-top: 5px solid var(--primary-color);
        }
        .auth-container h1 {
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 10px;
            font-weight: 700;
        }
        .auth-container p {
            color: var(--text-secondary);
            margin-bottom: 30px;
        }
        .developer-credit {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 30px;
        }
        .developer-credit span {
            font-weight: 600;
            color: var(--primary-color);
        }

        .form-group { margin-bottom: 20px; text-align: left; }
        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            background-color: var(--bg-color);
            border: 2px solid #444;
            border-radius: 8px;
            font-size: 15px;
            color: var(--text-primary);
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: var(--primary-color);
        }

        .btn {
            width: 100%;
            padding: 14px;
            background-color: var(--primary-color);
            color: #000;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
        }
        .btn:hover { background-color: #ffd64a; transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        
        .auth-switch-link {
            display: inline-block;
            margin-top: 20px;
            color: var(--primary-color);
            cursor: pointer;
            font-weight: 500;
        }

        /* --- DASHBOARD STYLES --- */
        .dashboard-container {
            max-width: 1200px;
            width: 100%;
        }
        .dashboard-header {
            background-color: var(--surface-color);
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .dashboard-header h2 { color: var(--primary-color); margin: 0; }
        .status-toggle { display: flex; align-items: center; gap: 15px; }
        .switch { position: relative; width: 60px; height: 34px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #555; transition: .4s; border-radius: 34px;
        }
        .slider:before {
            position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px;
            background-color: white; transition: .4s; border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--success-color); }
        input:checked + .slider:before { transform: translateX(26px); }
        .status-text { font-weight: 600; font-size: 18px; }
        
        .logout-btn {
            background: var(--danger-color); color: white; border: none;
            padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .panel {
            background-color: var(--surface-color);
            padding: 25px; border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .panel h3 {
            color: var(--primary-color); margin-bottom: 20px; padding-bottom: 10px;
            border-bottom: 2px solid #444;
        }
        .ride-card {
            background: var(--bg-color); padding: 15px; border-radius: 8px;
            margin-bottom: 15px; border-left: 4px solid var(--primary-color);
        }
        .ride-card p { margin: 8px 0; color: var(--text-secondary); }
        .ride-card p strong { color: var(--text-primary); }
        .ride-card .fare { color: var(--success-color); font-weight: bold; font-size: 18px; }
        .ride-btn {
            width: 100%; padding: 10px; border: none; border-radius: 6px;
            cursor: pointer; font-weight: 700; margin-top: 10px;
        }
        .accept-btn { background: var(--success-color); color: #000; }
        .progress-btn { background: #17a2b8; color: white; }
        .complete-btn { background: #6c757d; color: white; }
        
        .summary-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }
        .stat-card {
            background: linear-gradient(135deg, #444, #222); color: white;
            padding: 20px; border-radius: 10px; text-align: center;
        }
        .stat-card .number { font-size: 32px; font-weight: bold; color: var(--primary-color); }
        .stat-card .label { opacity: 0.9; margin-top: 5px; color: var(--text-secondary); }

        /* --- NEW MAP STYLES --- */
        #map {
            height: 300px;
            border-radius: 8px;
        }

        [style*="display: none"] { display: none !important; }
        .fade-in { animation: fadeIn 0.5s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
    </style>
</head>
<body>
    <div id="auth-view" class="auth-container fade-in">
        <div id="login-form">
            <h1>Join Street Rider</h1>
            <p class="developer-credit">Developed by <span>Venkatraman</span></p>
            <form onsubmit="login(event)">
                <div class="form-group">
                    <label>Driver ID</label>
                    <input type="number" id="loginDriverId" placeholder="Enter your driver ID" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <a class="auth-switch-link" onclick="switchTab('register')">Don't have an account? Register</a>
        </div>
        
        <div id="register-form" style="display: none;">
            <h1>Create Account</h1>
            <p>Become a Street Rider today.</p>
            <form onsubmit="registerDriver(event)">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" id="regName" placeholder="Enter your full name" required>
                </div>
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" id="regEmail" placeholder="Enter your email" required>
                </div>
                <div class="form-group">
                    <label>Vehicle Details</label>
                    <input type="text" id="regVehicle" placeholder="e.g., Maruti Swift (KA-01-AB-1234)" required>
                </div>
                <button type="submit" class="btn">Create Account</button>
            </form>
            <a class="auth-switch-link" onclick="switchTab('login')">Already have an account? Login</a>
        </div>
    </div>

    <div id="dashboard-view" class="dashboard-container" style="display: none;">
        <div class="dashboard-header">
            <h2 id="welcome-message">Welcome, Driver!</h2>
            <div class="status-toggle">
                <label class="switch">
                    <input type="checkbox" id="onlineToggle" onchange="toggleOnlineStatus()">
                    <span class="slider"></span>
                </label>
                <span id="statusText" class="status-text" style="color: var(--danger-color);">Offline</span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
        <div class="dashboard-grid">
            <div class="panel" id="current-ride-panel" style="display: none;">
                <h3>Current Ride</h3>
                <div id="current-ride-details"></div>
            </div>
            <div class="panel" id="available-rides-panel" style="display: none;">
                <h3>Available Rides</h3>
                <p style="background: #333; padding: 10px; border-radius: 6px; font-size: 14px; margin-bottom: 15px;">
                    🔄 <strong>Auto-refreshing every 3 seconds</strong>
                </p>
                <div id="available-rides"></div>
            </div>
            
            <div class="panel" id="map-panel" style="display: none;">
                <h3>Bengaluru Overview</h3>
                <div id="map"></div>
            </div>

            <div class="panel" id="summary-panel" style="display: none; grid-column: 1 / -1;">
                <h3>Today's Summary</h3>
                <div id="ride-summary" class="summary-stats"></div>
                <div id="completed-rides-list"></div>
            </div>
        </div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        // --- JAVASCRIPT LOGIC (MODIFIED FOR MAP) ---
        let currentDriverId = null;
        let currentRideFare = 0;
        let queueRefreshInterval = null;
        let map = null; // Map variable

        // --- NEW: Map Initialization Function ---
        function initializeMap() {
            if (map) return; // Don't re-initialize
            
            map = L.map('map', { zoomControl: false }).setView([12.9716, 77.5946], 11);
            
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            }).addTo(map);
        }

        // --- MODIFIED: toggleOnlineStatus to show map ---
        async function toggleOnlineStatus() {
            const toggle = document.getElementById('onlineToggle');
            const newStatus = toggle.checked ? 'online' : 'offline';
            try {
                const response = await fetch(`/api/driver/${currentDriverId}/status`, {
                    method: 'PUT', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                if (!response.ok) throw new Error('Failed to update status');
                
                const statusText = document.getElementById('statusText');
                statusText.textContent = toggle.checked ? 'Online' : 'Offline';
                statusText.style.color = toggle.checked ? 'var(--success-color)' : 'var(--danger-color)';
                
                if (toggle.checked) {
                    document.body.style.padding = '20px'; // Keep padding
                    document.getElementById('map-panel').style.display = 'block'; // Show map panel
                    initializeMap(); // Initialize map
                    checkActiveRide();
                    loadCompletedRides();
                    startQueueAutoRefresh();
                } else {
                    stopQueueAutoRefresh();
                    document.getElementById('current-ride-panel').style.display = 'none';
                    document.getElementById('available-rides-panel').style.display = 'none';
                    document.getElementById('summary-panel').style.display = 'none';
                    document.getElementById('map-panel').style.display = 'none'; // Hide map panel
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
                toggle.checked = !toggle.checked;
            }
        }
        
        // --- ALL OTHER FUNCTIONS ARE PRESERVED ---
        function switchTab(tab) {
            const loginForm = document.getElementById('login-form');
            const regForm = document.getElementById('register-form');
            if (tab === 'login') {
                loginForm.style.display = 'block';
                regForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                regForm.style.display = 'block';
            }
        }

        async function login(e) {
            e.preventDefault();
            const driverId = document.getElementById('loginDriverId').value;
            try {
                const response = await fetch(`/api/driver/${driverId}`);
                const result = await response.json();
                if (!result.success) throw new Error(result.error);
                
                currentDriverId = driverId;
                document.getElementById('auth-view').style.display = 'none';
                document.getElementById('dashboard-view').style.display = 'block';
                document.getElementById('welcome-message').textContent = `Welcome, ${result.data.name}!`;
                document.getElementById('onlineToggle').checked = false;
                document.getElementById('statusText').textContent = 'Offline';
                document.getElementById('statusText').style.color = 'var(--danger-color)';
            } catch (error) {
                alert(`Login Failed: ${error.message}`);
            }
        }

        function logout() {
            if (document.getElementById('onlineToggle').checked) {
                alert("Please go offline before logging out.");
                return;
            }
            stopQueueAutoRefresh();
            currentDriverId = null;
            document.getElementById('auth-view').style.display = 'block';
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('loginDriverId').value = '';
        }

        async function registerDriver(e) {
            e.preventDefault();
            const name = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const vehicle = document.getElementById('regVehicle').value;
            try {
                const response = await fetch('/api/driver/register', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ name, email, vehicle_details: vehicle }) 
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.details || result.error || 'Registration failed');
                alert(`Registration successful! Your Driver ID is ${result.driver_id}`);
                switchTab('login');
                document.getElementById('loginDriverId').value = result.driver_id;
            } catch (error) { 
                alert(`Registration Error: ${error.message}`); 
            }
        }
        
        function startQueueAutoRefresh() {
            if (queueRefreshInterval) clearInterval(queueRefreshInterval);
            loadAvailableRides();
            queueRefreshInterval = setInterval(loadAvailableRides, 3000);
        }
        
        function stopQueueAutoRefresh() {
            if (queueRefreshInterval) clearInterval(queueRefreshInterval);
            queueRefreshInterval = null;
        }

        async function checkActiveRide() {
            if (!currentDriverId) return;
            try {
                const response = await fetch(`/api/driver/${currentDriverId}/active-ride`);
                const data = await response.json();
                if (data.success && data.data) {
                    displayCurrentRide(data.data);
                } else if (document.getElementById('onlineToggle').checked) {
                    document.getElementById('current-ride-panel').style.display = 'none';
                    loadAvailableRides();
                }
            } catch (error) {
                console.error('Error checking active ride:', error);
            }
        }

        function displayCurrentRide(ride) {
            document.getElementById('available-rides-panel').style.display = 'none';
            const panel = document.getElementById('current-ride-panel');
            currentRideFare = ride.fare;
            let actionButton = '';
            if (ride.status === 'accepted') {
                actionButton = `<button class="ride-btn progress-btn" onclick="updateRideStatus(${ride.id}, 'in_progress')">Start Ride</button>`;
            } else if (ride.status === 'in_progress') {
                actionButton = `<button class="ride-btn complete-btn" onclick="updateRideStatus(${ride.id}, 'completed')">Complete Ride</button>`;
            }
            document.getElementById('current-ride-details').innerHTML = `
                <div class="ride-card">
                    <p><strong>Status:</strong> ${ride.status.replace('_', ' ').toUpperCase()}</p>
                    <p><strong>From:</strong> ${ride.source_location}</p>
                    <p><strong>To:</strong> ${ride.dest_location}</p>
                    <p class="fare">Fare: ₹${ride.fare}</p>
                    ${actionButton}
                </div>`;
            panel.style.display = 'block';
        }

        async function updateRideStatus(rideId, newStatus) {
            try {
                const response = await fetch(`/api/driver/rides/${rideId}/update-status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ driver_id: parseInt(currentDriverId), status: newStatus })
                });
                if (!response.ok) throw new Error('Failed to update status');
                
                if (newStatus === 'completed') {
                    alert(`Ride Completed! You earned ₹${currentRideFare}.`);
                    document.getElementById('current-ride-panel').style.display = 'none';
                    startQueueAutoRefresh();
                    loadCompletedRides();
                } else if (newStatus === 'accepted') {
                    stopQueueAutoRefresh();
                    checkActiveRide();
                } else {
                    checkActiveRide();
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }

        function acceptRide(rideId) {
            updateRideStatus(rideId, 'accepted');
        }

        async function loadAvailableRides() {
            if (!document.getElementById('onlineToggle').checked) return;
            if (document.getElementById('current-ride-panel').style.display === 'block') return;
            
            const panel = document.getElementById('available-rides-panel');
            panel.style.display = 'block';
            const ridesDiv = document.getElementById('available-rides');
            
            try {
                const response = await fetch('/api/driver/rides/available');
                const data = await response.json();
                if (!data.success || !data.data || data.data.length === 0) {
                    ridesDiv.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No available rides right now.</p>';
                    return;
                }
                
                ridesDiv.innerHTML = data.data.map((ride, index) => `
                    <div class="ride-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="background-color: var(--primary-color); color: #000; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                Queue #${index + 1}
                            </span>
                            <span style="color: var(--text-secondary); font-size: 12px;">Ride ID: ${ride.id}</span>
                        </div>
                        <p><strong>From:</strong> ${ride.source_location}</p>
                        <p><strong>To:</strong> ${ride.dest_location}</p>
                        <p class="fare">Fare: ₹${ride.fare}</p>
                        <button class="ride-btn accept-btn" onclick="acceptRide(${ride.id})">Accept Ride</button>
                    </div>`).join('');
            } catch (error) {
                ridesDiv.innerHTML = '<p style="color: var(--danger-color);">Could not connect to server.</p>';
            }
        }

        async function loadCompletedRides() {
            if (!currentDriverId) return;
            const summaryPanel = document.getElementById('summary-panel');
            summaryPanel.style.display = 'block';
            const summaryDiv = document.getElementById('ride-summary');
            
            try {
                const response = await fetch(`/api/driver/${currentDriverId}/completed-rides`);
                const data = await response.json();
                if (!data.success) throw new Error('Could not load summary');
                
                const summary = data.summary;
                summaryDiv.innerHTML = `
                    <div class="stat-card">
                        <div class="number">${summary.total_rides}</div>
                        <div class="label">Total Rides</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">₹${summary.total_earnings.toFixed(2)}</div>
                        <div class="label">Total Earnings</div>
                    </div>`;
                
                const listDiv = document.getElementById('completed-rides-list');
                if (data.data.length === 0) {
                    listDiv.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No completed rides today.</p>';
                } else {
                    listDiv.innerHTML = '<h4 style="margin: 20px 0 15px 0; color: var(--primary-color);">Completed Today:</h4>' + data.data.map(ride => `
                        <div class="ride-card">
                            <p><strong>From:</strong> ${ride.source_location}</p>
                            <p><strong>To:</strong> ${ride.dest_location}</p>
                            <p class="fare">Earned: ₹${ride.fare}</p>
                        </div>`).join('');
                }
            } catch (error) {
                summaryDiv.innerHTML = `<p style="color:red;">Could not load summary.</p>`;
            }
        }
    </script>
</body>
</html>
'''

# --- Python proxy endpoints (unchanged and complete) ---
@app.route('/')
def home():
    return render_template_string(DRIVER_DASHBOARD_HTML)

@app.route('/api/driver/<int:driver_id>', methods=['GET'])
def proxy_get_driver_details(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/register', methods=['POST'])
def proxy_register_driver():
    try:
        res = requests.post(f'{SERVER_URL}/api/drivers/register', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/status', methods=['PUT'])
def proxy_update_driver_status(driver_id):
    try:
        res = requests.put(f'{SERVER_URL}/api/drivers/{driver_id}/status', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/rides/available', methods=['GET'])
def proxy_get_available_rides():
    try:
        res = requests.get(f'{SERVER_URL}/api/rides/available')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/rides/<int:ride_id>/update-status', methods=['PUT'])
def proxy_update_ride_status(ride_id):
    try:
        res = requests.put(f'{SERVER_URL}/api/rides/{ride_id}/status', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/active-ride', methods=['GET'])
def proxy_get_active_ride(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}/active-ride')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/completed-rides', methods=['GET'])
def proxy_get_completed_rides(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}/completed-rides')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

if __name__ == '__main__':
    port = 5001
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f'Driver Portal running at http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)