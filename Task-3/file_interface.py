import socket
import json
import base64
import logging

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received = ""  # empty string
        while True:
            # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(8192)
            if data:
                # data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as e:  # Change bare 'except' to 'except Exception as e'
        logging.warning(f"error during data receiving: {e}")
        return {'status': 'ERROR', 'data': str(e)}  # Return an error dictionary

def remote_list():
    command_str = f"LIST"
    hasil = send_command(command_str)
    if (hasil['status'] == 'OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status'] == 'OK'):
        # proses file dalam bentuk base64 ke bentuk bytes
        namafile = hasil['data_namafile']
        file_content = hasil['data_file'].strip()  # Bersihkan string
        logging.warning(f"String base64 sebelum decode (client): {file_content}")  # Log string

        # Penanganan padding eksplisit (mungkin tidak perlu)
        missing_padding = len(file_content) % 4
        if missing_padding:
            file_content += '=' * (4 - missing_padding)

        isifile = base64.b64decode(file_content)
        fp = open(namafile, 'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

def remote_upload(filename=""):  # Modifikasi: hanya menerima filename
    try:
        with open(filename, 'rb') as file:  # Baca file dalam mode binary
            file_content = base64.b64encode(file.read()).decode()
            logging.warning(f"String base64 sebelum upload: {file_content[:100]}...")  # Log string
        command_str = f"UPLOAD {filename} {file_content}"
        hasil = send_command(command_str)
        if (hasil['status'] == 'OK'):
            print(hasil['data'])
            return True
        else:
            print(f"Gagal: {hasil['data']}")  # Print the error message
            return False
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def remote_delete(filename=""):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if (hasil['status'] == 'OK'):
        print(hasil['data'])
        return True
    else:
        print(f"Gagal: {hasil['data']}")  # Print the error message
        return False

if __name__ == '__main__':
    server_address = ('172.16.16.101', 6667)
    remote_list()
    # remote_get('test.txt')
    # remote_upload('donalbebek.jpg') 
    # remote_delete('donalbebek.jpg')
    remote_list()