from socket import *
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                d = data.decode('utf-8', errors="ignore")
                rcv += d

                if rcv.endswith('\r\n\r\n\r\n'):
					
                    hasil = httpserver.proses(rcv.removesuffix('\r\n\r\n\r\n'))
                    
                    connection.sendall(hasil)
                    connection.close()
                    return
            else:
                break
        except OSError:
            break
        except Exception as e:
            print(e)
    connection.close()
    return

def main():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(1)
    print("Main process started. Thread Pool Server running on port 8885.")

    try: # Start of try block for KeyboardInterrupt
        with ThreadPoolExecutor(20) as executor:
            while True:
                connection, client_address = my_socket.accept()
                logging.warning("connection from {}".format(client_address))
                p = executor.submit(ProcessTheClient, connection, client_address)
                the_clients.append(p)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        my_socket.close()
        print("Server socket closed.")
        
if __name__=="__main__":
    main()