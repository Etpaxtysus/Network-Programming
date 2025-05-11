import sys
import socket
import logging

#set basic logging
logging.basicConfig(level=logging.INFO)

try:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('172.19.0.4', 32444)
    logging.info(f"connecting to {server_address}")
    sock.connect(server_address)

    # Send data
    with open("sent.txt", "rb") as f:
        file_data = f.read()  # Read the file content
        logging.info(f"sending file data")
        sock.sendall(file_data)  # Send the entire file at once
    # Look for the response
    # amount_received = 0
    # amount_expected = len(file_data)
    # while amount_received < amount_expected:
    #     data = sock.recv(16)
    #     amount_received += len(data)
    #     logging.info(f"{data}")
        
except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
    exit(0)
finally:
    logging.info("closing")
    sock.close()
