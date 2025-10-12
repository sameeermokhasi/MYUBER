from flask import Flask, jsonify, render_template_string
import requests
import sys

app = Flask(__name__)

# The main server is running on port 3000
SERVER_URL = 'http://localhost:3000'

# --- NEW "STREET RIDER" ADMIN INTERFACE ---
ADMIN_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel | MYUBER</title>
    
    <style>
        :root {
            --bg-color: #1a1a1a;
            --surface-color: #2c2c2c;
            --primary-color: #ffc400; /* Admin Panel Gold */
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
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background-color: var(--surface-color);
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            border-left: 5px solid var(--primary-color);
        }
        .header h1 { color: var(--primary-color); }
        .refresh-btn {
            background-color: var(--primary-color);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            transition: background-color 0.3s;
        }
        .refresh-btn:hover { background-color: #ffd64a; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .panel {
            background-color: var(--surface-color);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .panel h2 {
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .count-badge {
            background-color: var(--primary-color);
            color: #000;
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 0.9rem;
        }
        .table-container {
            max-height: 400px;
            overflow-y: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #444;
        }
        th {
            background-color: var(--bg-color);
            position: sticky;
            top: 0;
        }
        tr:hover {
            background-color: #333;
        }
        .status { font-weight: bold; text-transform: capitalize; }
        .status-requested { color: #ffeb3b; }
        .status-accepted { color: #03a9f4; }
        .status-in_progress { color: #ffc400; }
        .status-completed { color: var(--success-color); }
        .status-offline { color: var(--danger-color); }
        .status-online { color: var(--success-color); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MYUBER Admin Dashboard</h1>
            <button class="refresh-btn" onclick="fetchData()">Refresh Data</button>
        </div>
        <div class="grid">
            <div class="panel">
                <h2>Riders (Users) <span id="user-count" class="count-badge">0</span></h2>
                <div class="table-container">
                    <table id="users-table">
                        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
            <div class="panel">
                <h2>Drivers <span id="driver-count" class="count-badge">0</span></h2>
                <div class="table-container">
                    <table id="drivers-table">
                        <thead><tr><th>ID</th><th>Name</th><th>Vehicle</th><th>Status</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="panel" style="margin-top: 20px;">
            <h2>Ride History <span id="ride-count" class="count-badge">0</span></h2>
            <div class="table-container">
                <table id="rides-table">
                    <thead><tr><th>ID</th><th>User ID</th><th>Driver ID</th><th>From</th><th>To</th><th>Fare</th><th>Status</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        async function fetchData() {
            try {
                const response = await fetch('/api/admin/data');
                const result = await response.json();

                if (result.success) {
                    populateTable('users-table', result.data.users, ['id', 'name', 'email', 'phone']);
                    populateTable('drivers-table', result.data.drivers, ['id', 'name', 'vehicle_details', 'online_status']);
                    populateTable('rides-table', result.data.rides, ['id', 'user_id', 'driver_id', 'source_location', 'dest_location', 'fare', 'status']);
                    
                    document.getElementById('user-count').textContent = result.data.users.length;
                    document.getElementById('driver-count').textContent = result.data.drivers.length;
                    document.getElementById('ride-count').textContent = result.data.rides.length;
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error("Failed to fetch admin data:", error);
                alert("Could not load data from the server.");
            }
        }

        function populateTable(tableId, data, columns) {
            const tableBody = document.querySelector(`#${tableId} tbody`);
            tableBody.innerHTML = ''; // Clear existing data

            if (data.length === 0) {
                const colSpan = columns.length;
                tableBody.innerHTML = `<tr><td colspan="${colSpan}" style="text-align: center;">No data available</td></tr>`;
                return;
            }

            data.forEach(item => {
                const row = document.createElement('tr');
                columns.forEach(col => {
                    const cell = document.createElement('td');
                    let value = item[col] === null ? 'N/A' : item[col];
                    
                    // Special styling for status columns
                    if (col === 'status' || col === 'online_status') {
                        cell.innerHTML = `<span class="status status-${value.replace('_', '-')}">${value.replace('_', ' ')}</span>`;
                    } else {
                        cell.textContent = value;
                    }
                    row.appendChild(cell);
                });
                tableBody.appendChild(row);
            });
        }

        // Fetch data on page load and set auto-refresh
        window.onload = () => {
            fetchData();
            setInterval(fetchData, 5000); // Auto-refresh every 5 seconds
        };
    </script>
</body>
</html>
'''

# --- Proxy Endpoint for the Admin Panel ---
@app.route('/api/admin/data')
def proxy_admin_data():
    """Proxies the request to the main server to get all admin data."""
    try:
        res = requests.get(f'{SERVER_URL}/api/admin/all-data')
        return jsonify(res.json()), res.status_code
    except requests.exceptions.RequestException as e:
        print(f"Admin Panel Proxy Error: {e}")
        return jsonify({'success': False, 'error': 'Main server connection failed'}), 503

@app.route('/')
def home():
    return render_template_string(ADMIN_DASHBOARD_HTML)

if __name__ == '__main__':
    port = 5002  # Running on a different port (e.g., 5002)
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f'Admin Panel running at http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)