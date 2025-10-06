import socket
import threading
import queue
import time

# A thread-safe queue to hold ride requests
ride_queue = queue.Queue()

# --- Driver Simulation ---
def driver_worker():
    """
    This function runs in a separate thread and simulates a driver.
    It waits for ride requests in the queue and processes them.
    """
    print("[DRIVER] Driver is online and waiting for rides.")
    while True:
        try:
            # Wait until a ride request is available in the queue
            client_address, client_socket = ride_queue.get()
            
            print(f"[DRIVER] New ride request from {client_address}. Notifying driver...")
            
            # Simulate notifying the driver and getting an acceptance
            # In a real app, this would be a push notification
            print(f"[DRIVER] Sending message to driver app: 'You have a new ride from {client_address}. Accept? (Y/N)'")
            
            # Simulate driver taking 2 seconds to accept
            time.sleep(2)
            print(f"[DRIVER] Driver accepted the ride for {client_address}.")
            
            # Mark the task as done in the queue
            ride_queue.task_done()

        except Exception as e:
            print(f"[DRIVER] Error in driver worker: {e}")


# --- Client Handling ---
def handle_client(client_socket, client_address):
    """
    This function runs in a dedicated thread for each connected client.
    """
    print(f"[SERVER] New connection from {client_address}")
    
    try:
        while True:
            # Wait for a message from the client (e.g., "RIDE_REQUEST")
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                print(f"[SERVER] Client {client_address} disconnected.")
                break

            print(f"[SERVER] Received ride request from {client_address}")

            # 1. Add the ride request to the central queue for the driver
            ride_queue.put((client_address, client_socket))

            # 2. Immediately tell the client their ride is "booked"
            client_socket.send("booked".encode('utf-8'))
            print(f"[SERVER] Sent 'booked' to {client_address}")

            # 3. Wait for 10 seconds as requested
            time.sleep(10) # <--- THIS LINE WAS CHANGED FROM 3 TO 10

            # 4. Send the final "confirmed" status
            client_socket.send("confirmed".encode('utf-8'))
            print(f"[SERVER] Sent 'confirmed' to {client_address}")

    except ConnectionResetError:
        print(f"[SERVER] Client {client_address} forcefully disconnected.")
    except Exception as e:
        print(f"[SERVER] Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[SERVER] Closed connection to {client_address}")


# --- Main Server Setup ---
def main():
    HOST = '127.0.0.1'  # Localhost
    PORT = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5) # Allow up to 5 queued connections
    print(f"[SERVER] Server started on {HOST}:{PORT} and listening...")

    # Start the driver worker thread in the background
    driver_thread = threading.Thread(target=driver_worker, daemon=True)
    driver_thread.start()

    while True:
        # Wait for a new client to connect
        client_socket, client_address = server_socket.accept()
        
        # Create and start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()