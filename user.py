from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import sys

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'

# --- "JOIN RIDER" INTERFACE WITH AUTO-REFRESHING RIDE HISTORY ---
USER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Join Rider | Passenger Portal</title>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    
    <style>
        :root {
            --bg-color: #1a1a2e;
            --surface-color: #1e1e3f;
            --primary-color: #9c4aee; /* Vibrant Purple */
            --secondary-color: #667eea;
            --text-primary: #ffffff;
            --text-secondary: #a0a0c0;
            --success-color: #00ffc3;
            --danger-color: #ff5e5e;
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
        .auth-container {
            background-color: var(--surface-color);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            max-width: 450px;
            width: 100%;
            padding: 40px;
            text-align: center;
            border-top: 5px solid var(--primary-color);
        }
        .auth-container h1 { font-size: 2.5rem; color: var(--primary-color); margin-bottom: 10px; font-weight: 700; }
        .auth-container p { color: var(--text-secondary); margin-bottom: 30px; }
        .developer-credit { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 30px; }
        .developer-credit span { font-weight: 600; color: var(--primary-color); }
        .form-group { margin-bottom: 20px; text-align: left; }
        label { display: block; margin-bottom: 8px; color: var(--text-secondary); font-weight: 500; font-size: 14px; }
        input {
            width: 100%; padding: 12px 15px; background-color: var(--bg-color);
            border: 2px solid #444; border-radius: 8px; font-size: 15px;
            color: var(--text-primary); transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: var(--primary-color); }
        .btn {
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
            color: white; border: none; border-radius: 8px; font-size: 16px;
            font-weight: 700; cursor: pointer; transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .auth-switch-link { display: inline-block; margin-top: 20px; color: var(--primary-color); cursor: pointer; font-weight: 500; }
        .dashboard-container { max-width: 1200px; width: 100%; }
        .dashboard-header {
            background-color: var(--surface-color); padding: 20px 30px; border-radius: 12px;
            margin-bottom: 20px; display: flex; justify-content: space-between;
            align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .dashboard-header h2 { color: var(--primary-color); margin: 0; }
        .logout-btn { background: var(--danger-color); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
        .panel { background-color: var(--surface-color); padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .panel h3 { color: var(--primary-color); margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #444; }
        #ride-history-panel { grid-column: 1 / -1; }
        .ride-card { background: var(--bg-color); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid var(--primary-color); }
        .ride-card p { margin: 8px 0; color: var(--text-secondary); }
        .ride-card p strong { color: var(--text-primary); }
        .status { font-weight: bold; text-transform: capitalize; }
        .status-requested { color: #ffeb3b; }
        .status-accepted { color: #03a9f4; }
        .status-in_progress { color: var(--primary-color); }
        .status-completed { color: var(--success-color); }
        #map { height: 300px; border-radius: 8px; }
        [style*="display: none"] { display: none !important; }
        .fade-in { animation: fadeIn 0.5s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <div id="auth-view" class="auth-container fade-in">
        <div id="login-form">
            <h1>Join Rider</h1>
            <p class="developer-credit">Developed by <span>Venkatraman</span></p>
            <form onsubmit="login(event)">
                <div class="form-group"><label>User ID</label><input type="number" id="loginUserId" placeholder="Enter your user ID" required></div>
                <button type="submit" class="btn">Login</button>
            </form>
            <a class="auth-switch-link" onclick="switchAuthView('register')">Don't have an account? Register</a>
        </div>
        <div id="register-form" style="display: none;">
            <h1>Create Account</h1>
            <p>Become a Rider today.</p>
            <form onsubmit="registerUser(event)">
                <div class="form-group"><label>Full Name</label><input type="text" id="regName" required></div>
                <div class="form-group"><label>Email Address</label><input type="email" id="regEmail" required></div>
                <div class="form-group"><label>Phone Number</label><input type="tel" id="regPhone" required></div>
                <button type="submit" class="btn">Create Account</button>
            </form>
            <a class="auth-switch-link" onclick="switchAuthView('login')">Already have an account? Login</a>
        </div>
    </div>
    <div id="dashboard-view" class="dashboard-container" style="display: none;">
        <div class="dashboard-header">
            <h2 id="welcome-message">Welcome!</h2>
            <button class="logout-btn" onclick="logout()">Logout</button>
        </div>
        <div class="dashboard-grid">
            <div id="ride-request-panel" class="panel">
                <h3>Book a New Ride</h3>
                <form onsubmit="requestRide(event)">
                    <div class="form-group"><label>Pickup Location</label><input id="source" required></div>
                    <div class="form-group"><label>Drop-off Location</label><input id="destination" required></div>
                    <button type="submit" class="btn">Request Ride</button>
                </form>
                <div id="queueDisplay" style="display: none;"></div>
            </div>
            <div id="map-panel" class="panel">
                <h3>Bengaluru Overview</h3>
                <div id="map"></div>
            </div>
            <div id="ride-history-panel" class="panel">
                <h3>Your Rides <span style="font-size: 0.8rem; color: var(--text-secondary);">(updates every 3s)</span></h3>
                <div id="myRides"></div>
            </div>
        </div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        let currentUserId = null;
        let queueCheckInterval = null;
        let historyRefreshInterval = null; // New interval for history
        let map = null;

        function initializeMap() {
            if (map) return;
            try {
                map = L.map('map', { zoomControl: false }).setView([12.9716, 77.5946], 11);
                L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; CARTO'
                }).addTo(map);
            } catch (e) {
                document.getElementById('map').innerHTML = "Map failed to load.";
            }
        }
        
        function switchAuthView(view) {
            document.getElementById('login-form').style.display = view === 'login' ? 'block' : 'none';
            document.getElementById('register-form').style.display = view === 'register' ? 'block' : 'none';
        }

        async function login(e) {
            e.preventDefault();
            const userId = document.getElementById('loginUserId').value;
            currentUserId = userId;
            document.getElementById('auth-view').style.display = 'none';
            document.getElementById('dashboard-view').style.display = 'block';
            document.getElementById('welcome-message').textContent = `Welcome, User #${userId}!`;
            initializeMap();
            checkForQueuedRides();
            startHistoryRefresh(); // Start auto-refresh for rides
        }
        
        async function registerUser(e) {
            e.preventDefault();
            const name = document.getElementById('regName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const phone = document.getElementById('regPhone').value.trim();
            try {
                const response = await fetch('/api/user/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, phone })
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'Registration failed');
                alert(`Registration successful! Your User ID is ${result.user_id}`);
                switchAuthView('login');
                document.getElementById('loginUserId').value = result.user_id;
            } catch (error) {
                alert(`Registration Error: ${error.message}`);
            }
        }
        
        function logout() {
            if (queueCheckInterval) clearInterval(queueCheckInterval);
            if (historyRefreshInterval) clearInterval(historyRefreshInterval); // Stop history refresh
            currentUserId = null;
            document.getElementById('auth-view').style.display = 'block';
            document.getElementById('dashboard-view').style.display = 'none';
        }
        
        async function requestRide(e) {
            e.preventDefault();
            const source = document.getElementById('source').value.trim();
            const destination = document.getElementById('destination').value.trim();
            try {
                const response = await fetch('/api/user/request-ride-queue', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: parseInt(currentUserId), source_location: source, dest_location: destination })
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'Ride request failed');
                displayQueueInfo(result);
                startQueueCheck(result.ride_id);
                loadMyRides(); // Immediate update after request
            } catch (error) {
                alert(`Ride Request Error: ${error.message}`);
            }
        }
        
        function displayQueueInfo(data) {
            const queueDisplay = document.getElementById('queueDisplay');
            queueDisplay.innerHTML = `<p style="margin-top: 15px;"><strong>Status:</strong> In Queue (#${data.queue_position})</p>`;
            queueDisplay.style.display = 'block';
        }

        function updateQueueDisplay(data) {
            const queueDisplay = document.getElementById('queueDisplay');
            if (queueDisplay) {
                queueDisplay.innerHTML = `<p style="margin-top: 15px;"><strong>Status:</strong> In Queue (#${data.queue_position})</p>`;
            }
        }
        
        function startQueueCheck(rideId) {
            if (queueCheckInterval) clearInterval(queueCheckInterval);
            queueCheckInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/user/queue-position/${rideId}`, { cache: 'no-cache' });
                    if (!response.ok) throw new Error('Server error');
                    const data = await response.json();
                    if (data.success && data.in_queue) {
                        updateQueueDisplay(data);
                    } else {
                        clearInterval(queueCheckInterval);
                        document.getElementById('queueDisplay').style.display = 'none';
                        loadMyRides(); // Update history when ride is accepted
                    }
                } catch (error) {
                    clearInterval(queueCheckInterval);
                }
            }, 3000);
        }
        
        async function checkForQueuedRides() {
            try {
                const response = await fetch(`/api/user/rides/${currentUserId}`);
                const data = await response.json();
                if (data.success && data.data) {
                    const requestedRide = data.data.find(ride => ride.status === 'requested');
                    if (requestedRide) {
                        const queueResponse = await fetch(`/api/user/queue-position/${requestedRide.id}`);
                        const queueData = await queueResponse.json();
                        if (queueData.success && queueData.in_queue) {
                            displayQueueInfo(queueData);
                            startQueueCheck(requestedRide.id);
                        }
                    }
                }
            } catch (error) { console.error('Error checking for queued rides:', error); }
        }
        
        // --- NEW FUNCTIONS FOR HISTORY REFRESH ---
        function startHistoryRefresh() {
            if (historyRefreshInterval) clearInterval(historyRefreshInterval);
            loadMyRides(); // Load immediately on start
            historyRefreshInterval = setInterval(loadMyRides, 3000); // Refresh every 3 seconds
        }

        async function loadMyRides() {
            if (!currentUserId) return; // Don't run if not logged in
            const ridesDiv = document.getElementById('myRides');
            try {
                const response = await fetch(`/api/user/rides/${currentUserId}`);
                const data = await response.json();
                if (!data.success || !data.data || data.data.length === 0) {
                    ridesDiv.innerHTML = '<p>No rides yet</p>';
                    return;
                }
                ridesDiv.innerHTML = data.data.map(ride => `
                    <div class="ride-card">
                        <p><span class="status status-${ride.status.replace('_', '-')}">${ride.status.replace('_', ' ')}</span></p>
                        <p><strong>From:</strong> ${ride.source_location}</p>
                        <p><strong>To:</strong> ${ride.dest_location}</p>
                        <p><strong>Fare:</strong> ₹${ride.fare}</p>
                        ${ride.driver_name ? `<p><strong>Driver:</strong> ${ride.driver_name}</p>` : ''}
                    </div>`).join('');
            } catch (error) {
                // Do not show an alert, just log it, to avoid spamming the user
                console.error("Could not auto-refresh rides.", error);
            }
        }
    </script>
</body>
</html>
'''

# --- Python proxy endpoints (unchanged) ---
@app.route('/')
def home():
    return render_template_string(USER_DASHBOARD_HTML)

@app.route('/api/user/register', methods=['POST'])
def proxy_register_user():
    try:
        res = requests.post(f'{SERVER_URL}/api/users/register', json=request.get_json(), timeout=5)
        return jsonify(res.json()), res.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/user/request-ride-queue', methods=['POST'])
def proxy_request_ride_queue():
    try:
        res = requests.post(f'{SERVER_URL}/api/rides/request-with-queue', json=request.get_json(), timeout=5)
        return jsonify(res.json()), res.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/user/queue-position/<int:ride_id>', methods=['GET'])
def proxy_queue_position(ride_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/rides/{ride_id}/queue-position', timeout=5)
        return jsonify(res.json()), res.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/user/rides/<int:user_id>', methods=['GET'])
def proxy_user_rides(user_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/users/{user_id}/rides', timeout=5)
        return jsonify(res.json()), res.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f'User Client running at http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)