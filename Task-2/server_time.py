from socket import *
import socket
import threading
import logging
import time
import sys
from datetime import datetime

def proses_string(request_string):
    balas = "Error! Invalid request\r\n"
    if (request_string.startswith("TIME") and request_string.endswith("\n")):
        now = datetime.now()
        waktu = now.strftime("%H:%M:%S")
        balas=f"JAM {waktu}\r\n"
    if (request_string.startswith("QUIT") and request_string.endswith("\n")):
        balas="XXX"
    return balas

class ProcessTheClient(threading.Thread):
    def __init__(self,connection,address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)
    def run(self):
        logging.info(f"[CONNECTED] Client {self.address} connected to server.")
        try:
            while True:
                data = self.connection.recv(32)
                if data:
                    request_s = data.decode()
                    balas = proses_string(request_s)
                    if (balas == "XXX"):
                        logging.info(f"[DISCONNECTED] Client {self.address} disconnected.")
                        self.connection.close()
                        break
                    self.connection.sendall(balas.encode())
                else:
                    logging.info(f"[DISCONNECTED] Client {self.address} disconnected.")
                    break
        except Exception as e:
            logging.error(f"[ERROR] Client {self.address} connection error: {e}")
        finally:
            if not self.connection._closed:
                logging.info(f"[DISCONNECTED] Client {self.address} connection closed due to exception or unexpected termination.")
                self.connection.close()

class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0',45000))
        self.my_socket.listen(1)
        logging.info("[STARTED] Time Server listening on 0.0.0.0:45000")

        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.info(f"[ACCEPTED] Connection from {self.client_address}")

            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    svr = Server()
    svr.start()

if __name__=="__main__":
    main()