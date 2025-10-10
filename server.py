from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg.rows import dict_row
import psycopg
import random
import traceback # Import the traceback module for better error logging

app = Flask(__name__)
CORS(app)

# --- Database Configuration ---
DB_NAME = "MYUBER_db"
DB_USER = "postgres"
DB_PASS = "0987"  # 👈 *** USE THE PASSWORD THAT WORKED FOR setup_database.py ***
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """Establishes a robust connection to the PostgreSQL database."""
    try:
        return psycopg.connect(
            f"user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT} dbname={DB_NAME}",
            autocommit=True
        )
    except psycopg.OperationalError as e:
        print(f"CRITICAL: Database connection failed: {e}")
        raise

# --- Fare Calculation Logic ---
def calculate_fare(source, destination):
    base_fare = 50.0
    rate_per_km = 12.5
    simulated_distance = max(1, (len(source) + len(destination)) / 2 + random.uniform(-2, 2))
    return round(base_fare + (simulated_distance * rate_per_km), 2)

# --- Driver Login Endpoint ---
@app.route('/api/drivers/<int:driver_id>', methods=['GET'])
def get_driver_details(driver_id):
    """Fetches details for a single driver to verify their existence."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name FROM drivers WHERE id = %s;", (driver_id,))
                driver = cur.fetchone()
        
        if driver:
            return jsonify({'success': True, 'data': driver})
        else:
            return jsonify({'success': False, 'error': 'Driver not found'}), 404
    except Exception as e:
        print(f"Error in get_driver_details:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Ride Lifecycle Endpoint ---
@app.route('/api/rides/<int:ride_id>/status', methods=['PUT'])
def update_ride_status(ride_id):
    try:
        data = request.get_json()
        driver_id = data.get('driver_id')
        new_status = data.get('status')
        
        if not all([driver_id, new_status]):
            return jsonify({'success': False, 'error': 'driver_id and status are required'}), 400

        query, params = "", ()
        if new_status == 'accepted':
            query = "UPDATE rides SET driver_id = %s, status = 'accepted' WHERE id = %s AND status = 'requested' RETURNING id;"
            params = (driver_id, ride_id)
        elif new_status == 'completed':
            query = "UPDATE rides SET status = 'completed', completed_at = NOW() WHERE id = %s AND driver_id = %s RETURNING id;"
            params = (ride_id, driver_id)
        elif new_status == 'in_progress':
            query = "UPDATE rides SET status = 'in_progress' WHERE id = %s AND driver_id = %s RETURNING id;"
            params = (ride_id, driver_id)
        else:
            return jsonify({'success': False, 'error': 'Invalid status update provided'}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()
                if not result:
                    return jsonify({'success': False, 'error': 'Ride state change failed. Ride might not be in the correct state or does not exist.'}), 404
        
        print(f"✅ Ride {ride_id} status updated to {new_status} by driver {driver_id}")
        return jsonify({'success': True, 'message': f'Ride status updated to {new_status}'})
    except Exception as e:
        print(f"Error in update_ride_status:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Driver Summary Endpoint ---
@app.route('/api/drivers/<int:driver_id>/completed-rides', methods=['GET'])
def get_completed_rides_today(driver_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT * FROM rides WHERE driver_id = %s AND status = 'completed' "
                    "AND completed_at >= date_trunc('day', NOW()) ORDER BY completed_at DESC;",
                    (driver_id,)
                )
                rides = cur.fetchall()
                total_earnings = sum(ride.get('fare') or 0 for ride in rides)
                
                for ride in rides:
                    if ride.get('completed_at'):
                        ride['completed_at'] = ride['completed_at'].isoformat()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_rides': len(rides),
                'total_earnings': float(total_earnings)
            },
            'data': rides
        })
    except Exception as e:
        print(f"Error in get_completed_rides_today:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Health Check ---
@app.route('/api/health', methods=['GET'])
def health_check():
    db_status = "Connection failed"
    ride_count = 0
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM rides;")
                result = cur.fetchone()
                if result:
                    ride_count = result[0]
                db_status = f"Connected - {ride_count} rides in system"
    except Exception as e:
        print(f"Health check error: {e}")
    
    return jsonify({
        'service': 'Core Server API',
        'status': 'running',
        'db_status': db_status
    })

# --- Registration Endpoints ---
@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'email', 'phone']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s) RETURNING id;",
                    (data['name'], data['email'], data['phone'])
                )
                # --- FIX: Safely fetch the result ---
                result = cur.fetchone()
                if result:
                    user_id = result[0]
                else:
                    return jsonify({'success': False, 'error': 'Failed to create user'}), 500
        
        return jsonify({'success': True, 'user_id': user_id}), 201
    except Exception as e:
        print(f"Error in register_user:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

@app.route('/api/drivers/register', methods=['POST'])
def register_driver():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'email', 'vehicle_details']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO drivers (name, email, vehicle_details) VALUES (%s, %s, %s) RETURNING id;",
                    (data['name'], data['email'], data['vehicle_details'])
                )
                # --- FIX: Safely fetch the result ---
                result = cur.fetchone()
                if result:
                    driver_id = result[0]
                else:
                    return jsonify({'success': False, 'error': 'Failed to create driver'}), 500
        
        return jsonify({'success': True, 'driver_id': driver_id}), 201
    except Exception as e:
        print(f"Error in register_driver:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Ride Request Endpoint ---
@app.route('/api/rides/request', methods=['POST'])
def request_ride():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['user_id', 'source_location', 'dest_location']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        user_id = data['user_id']
        fare = calculate_fare(data['source_location'], data['dest_location'])
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # --- FIX: Validate user_id exists before inserting ride ---
                cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
                if not cur.fetchone():
                    return jsonify({'success': False, 'error': f'User with id {user_id} not found'}), 404

                cur.execute(
                    "INSERT INTO rides (user_id, source_location, dest_location, status, fare) "
                    "VALUES (%s, %s, %s, 'requested', %s) RETURNING id;",
                    (user_id, data['source_location'], data['dest_location'], fare)
                )
                # --- FIX: Safely fetch the result ---
                result = cur.fetchone()
                if result:
                    ride_id = result[0]
                else:
                    return jsonify({'success': False, 'error': 'Failed to create ride'}), 500
        
        return jsonify({'success': True, 'ride_id': ride_id, 'estimated_fare': fare}), 201
    except Exception as e:
        print(f"Error in request_ride:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Ride Request with Queue Info ---
@app.route('/api/rides/request-with-queue', methods=['POST'])
def request_ride_with_queue():
    """Request a ride and get immediate queue information"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['user_id', 'source_location', 'dest_location']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        user_id = data['user_id']
        fare = calculate_fare(data['source_location'], data['dest_location'])
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # --- FIX: Validate user_id exists before inserting ride ---
                cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
                if not cur.fetchone():
                    return jsonify({'success': False, 'error': f'User with id {user_id} not found'}), 404

                # Insert the ride
                cur.execute(
                    "INSERT INTO rides (user_id, source_location, dest_location, status, fare) "
                    "VALUES (%s, %s, %s, 'requested', %s) RETURNING id, created_at;",
                    (user_id, data['source_location'], data['dest_location'], fare)
                )
                result = cur.fetchone()
                if not result:
                    return jsonify({'success': False, 'error': 'Failed to create ride'}), 500

                ride_id = result[0]
                created_at = result[1]
                
                # Get queue position - count all requested rides created before or at same time
                cur.execute("SELECT COUNT(*) FROM rides WHERE status = 'requested' AND created_at <= %s;", (created_at,))
                queue_position_result = cur.fetchone()
                queue_position = queue_position_result[0] if queue_position_result else 1
                
                # Get online drivers
                cur.execute("SELECT COUNT(*) FROM drivers WHERE online_status = 'online'")
                online_drivers_result = cur.fetchone()
                online_drivers = online_drivers_result[0] if online_drivers_result else 0
        
        print(f"🎫 New ride #{ride_id} created - Queue position: {queue_position}, Online drivers: {online_drivers}")
        
        return jsonify({
            'success': True,
            'ride_id': ride_id,
            'estimated_fare': fare,
            'queue_position': queue_position,
            'online_drivers': online_drivers
        }), 201
    except Exception as e:
        print(f"Error in request_ride_with_queue:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Get Queue Position ---
@app.route('/api/rides/<int:ride_id>/queue-position', methods=['GET'])
def get_queue_position(ride_id):
    """Get the position of a ride in the queue - REAL-TIME UPDATE"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # First check if ride exists and get its status
                cur.execute("SELECT id, status, created_at FROM rides WHERE id = %s", (ride_id,))
                ride = cur.fetchone()
                
                if not ride:
                    return jsonify({'success': False, 'error': 'Ride not found'}), 404
                
                if ride['status'] != 'requested':
                    print(f"📍 Ride {ride_id} status: {ride['status']} (not in queue)")
                    return jsonify({'success': True, 'status': ride['status'], 'in_queue': False})
                
                # --- FIX: Safely fetch COUNT results ---
                cur.execute("SELECT COUNT(*) FROM rides WHERE status = 'requested' AND created_at < %s", (ride['created_at'],))
                rides_before_result = cur.fetchone()
                rides_before = rides_before_result['count'] if rides_before_result else 0
                
                queue_position = rides_before + 1
                
                cur.execute("SELECT COUNT(*) FROM rides WHERE status = 'requested'")
                total_waiting_result = cur.fetchone()
                total_waiting = total_waiting_result['count'] if total_waiting_result else 0
                
                cur.execute("SELECT COUNT(*) FROM drivers WHERE online_status = 'online'")
                online_drivers_result = cur.fetchone()
                online_drivers = online_drivers_result['count'] if online_drivers_result else 0
                
                print(f"📊 Ride {ride_id} - Position: {queue_position}/{total_waiting}, Drivers: {online_drivers}")
                
                return jsonify({
                    'success': True,
                    'queue_position': queue_position,
                    'total_waiting': total_waiting,
                    'online_drivers': online_drivers,
                    'in_queue': True,
                    'status': 'requested'
                })
    except Exception as e:
        print(f"Error in get_queue_position:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Get All Rides for a User ---
@app.route('/api/users/<int:user_id>/rides', methods=['GET'])
def get_user_rides(user_id):
    """Get all rides for a user"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT r.*, d.name as driver_name 
                    FROM rides r
                    LEFT JOIN drivers d ON r.driver_id = d.id
                    WHERE r.user_id = %s 
                    ORDER BY r.created_at DESC
                """, (user_id,))
                rides = cur.fetchall()
                
                for ride in rides:
                    if ride.get('created_at'):
                        ride['created_at'] = ride['created_at'].isoformat()
                    if ride.get('completed_at'):
                        ride['completed_at'] = ride['completed_at'].isoformat()
                
                return jsonify({'success': True, 'data': rides})
    except Exception as e:
        print(f"Error in get_user_rides:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Available Rides Endpoint ---
@app.route('/api/rides/available', methods=['GET'])
def get_available_rides():
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM rides WHERE status = 'requested' ORDER BY created_at ASC;")
                rides = cur.fetchall()
                
                for r in rides:
                    if r.get('created_at'):
                        r['created_at'] = r['created_at'].isoformat()
        
        print(f"📋 Available rides in queue: {len(rides)}")
        return jsonify({'success': True, 'data': rides})
    except Exception as e:
        print(f"Error in get_available_rides:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Active Ride Endpoint ---
@app.route('/api/drivers/<int:driver_id>/active-ride', methods=['GET'])
def get_active_ride(driver_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT * FROM rides WHERE driver_id = %s AND status IN ('accepted', 'in_progress');",
                    (driver_id,)
                )
                ride = cur.fetchone()
                
                if ride and ride.get('created_at'):
                    ride['created_at'] = ride['created_at'].isoformat()
        
        return jsonify({'success': True, 'data': ride})
    except Exception as e:
        print(f"Error in get_active_ride:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

# --- Driver Status Endpoint ---
@app.route('/api/drivers/<int:driver_id>/status', methods=['PUT'])
def update_driver_status(driver_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE drivers SET online_status = %s WHERE id = %s;", (new_status, driver_id))
        
        print(f"🚗 Driver {driver_id} is now {new_status}")
        return jsonify({'success': True, 'message': f'Driver is now {new_status}.'})
    except Exception as e:
        print(f"Error in update_driver_status:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'details': str(e)}), 500

if __name__ == '__main__':
    print('=' * 60)
    print('🚗 Mini Uber Core Server')
    print('=' * 60)
    print('Server starting at: http://localhost:3000')
    print('Queue system: First-In-First-Out (FIFO)')
    print('Real-time updates: Enabled')
    print('=' * 60)
    app.run(host='0.0.0.0', port=3000, debug=True)