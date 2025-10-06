import socket
import time

HOST = '127.0.0.1'
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((HOST, PORT))
    print("Connected to Uber server.")

    # 1. Send a ride request
    print("Requesting a ride...")
    client_socket.send("RIDE_REQUEST".encode('utf-8'))

    # 2. Wait for the "booked" status
    status1 = client_socket.recv(1024).decode('utf-8')
    print(f"Status: {status1.upper()}") # Should print "Status: BOOKED"

    # 3. Wait for the "confirmed" status
    status2 = client_socket.recv(1024).decode('utf-8')
    print(f"Status: {status2.upper()}") # Should print "Status: CONFIRMED"

    print("Ride confirmed! Your driver is on the way.")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client_socket.close()
    print("Disconnected from server.")
    