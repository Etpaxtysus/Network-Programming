import socket
import sys
import csv
import json
import base64
import os
import time
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


server_address = ('127.0.0.1', 6668)

def send_command(command_str):
    try:
        with socket.create_connection(server_address, timeout=300) as sock:
            sock.sendall(command_str.encode())

            data_received = b""
            end_marker = b"\r\n\r\n"

            while True:
                chunk = sock.recv(2**20)
                if not chunk:
                    break
                data_received += chunk

                if end_marker in data_received[-8:]:
                    break

            response_str = data_received.decode()
            response_str = response_str.strip()

            return json.loads(response_str)
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "ERROR", "message": str(e)}

def remote_list():
    command_str = "LIST\r\n\r\n"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"  • {nmfile}")
        return True, "Success"
    else:
        print(f"Gagal: {hasil.get('data', 'Unknown error')}")
        return False, "Gagal"

def remote_get(filename=""):
    command_str = f"GET {filename}\r\n\r\n"
    print(f"Sending GET request for {filename}...")

    start_time = time.time()
    hasil = send_command(command_str)
    end_time = time.time()

    print(f"Response received in {end_time - start_time:.2f} seconds")

    if (hasil['status']=='OK'):
        namafile = hasil['data_namafile']
        print(f"Decoding file data for {namafile}...")
        isifile = base64.b64decode(hasil['data_file'])

        print(f"Writing {len(isifile)} bytes to file...")
        with open(namafile, 'wb') as fp:
            fp.write(isifile)

        print(f"File {filename} berhasil didownload ({len(isifile)} bytes)")
        return True, "Success"
    else:
        print(f"Gagal: {hasil.get('data', 'Unknown error')}")
        return False, "Gagal"

def remote_add(filename=""):
    isFileExist = os.path.exists(filename)

    if not isFileExist:
        print(f"File {filename} tidak ditemukan...")
        return False, "File tidak ditemukan"

    file_size = os.path.getsize(filename)
    print(f"Reading file {filename} ({file_size} bytes)...")

    with open(filename, 'rb') as f:
        content = f.read()

    print(f"Encoding file data ({file_size} bytes)...")
    encodedContent = base64.b64encode(content).decode()
    encoded_size = len(encodedContent)
    print(f"Encoded size: {encoded_size} bytes")

    command_str = f"ADD {filename} {encodedContent}\r\n\r\n"
    print(f"Sending ADD request ({len(command_str)} bytes total)...")

    start_time = time.time()
    result = send_command(command_str)
    end_time = time.time()

    print(f"Response received in {end_time - start_time:.2f} seconds")

    if (result['status']=='OK'):
        print(f"File {filename} berhasil diupload")
        return True, "Success"
    else:
        print(f"Gagal: {result.get('data', 'Unknown error')}")
        return False, "Gagal"

def remote_delete(filename=""):
    command_str = f"DELETE {filename}\r\n\r\n"
    hasil = send_command(command_str)

    if (hasil['status']=='OK'):
        print(f"File {filename} berhasil dihapus")
        return True, "Success"
    else:
        print(f"Gagal: {hasil.get('data', 'Unknown error')}")
        return False, "Gagal"

def stress_worker(task_type, filename):
    start = time.time()
    print(f"----> Starting {task_type} for {filename}")
    if task_type == "upload":
        success, res = remote_add(filename)
        print(f"----> Uploading {filename} completed")
    else:
        success, res = remote_get(filename)
    end = time.time()
    size = os.path.getsize(filename) if os.path.exists(filename) else 0
    elapsed = end - start
    return {
        "task": task_type,
        "filename": filename,
        "success": success,
        "time": elapsed,
        "throughput": size / elapsed if success and elapsed > 0 else 0,
        "message": res if not success else "OK"
    }

def run_stress_test(task_type, filename,  num_clients, server_workers=5):
    print(f"\nTesting {task_type.upper()} - File: {filename} | Server Pool: {server_workers}, Clients: {num_clients}")
    client_results = []

    start_all = time.time()
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = [executor.submit(stress_worker, task_type, filename) for _ in range(num_clients)]
        for future in tqdm(futures):
            client_result = future.result()
            
            total_time = time.time() - start_all

            result_to_write = {
                "task": task_type,
                "file": filename,
                "client_pool": "process",
                "server_pool": server_workers,
                "clients": num_clients,
                "client_success": 1 if client_result["success"] else 0,
                "client_fail": 0 if client_result["success"] else 1,
                "server_success": 1 if client_result["success"] else 0,
                "server_fail": 0 if client_result["success"] else 1,
                "total_time": round(total_time, 2),
                "avg_client_time": round(client_result["time"], 2),
                "avg_throughput": round(client_result["throughput"], 2) if client_result["success"] else 0
            }
            write_result([result_to_write], 50)

def create_files():
    sizes = {
        "10MB.txt": 10*1024*1024,
        "50MB.txt": 50*1024*1024,
        #"100MB.txt": 100*1024*1024,
    }

    for name, size in sizes.items():
        if not os.path.exists(name):
            print(f"Generating {name}...")
            with open(name, "wb") as f:
                f.write(os.urandom(size))

def write_result(results, server_workers):
    """
    Write successful test results to CSV, avoiding duplicates.
    """
    file_path = "multiprocessing_50server.csv"
    file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
    existing_data = []

    if file_exists:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_data.append(row)

    next_row_num = 1
    if existing_data:
        try:
            next_row_num = int(existing_data[-1]['no']) + 1
        except (ValueError, KeyError, IndexError):
            next_row_num = 1  # Fallback to 1 if 'no' is missing or invalid

    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ["no", "operation", "volume", "client_pool_size", "server_pool_size",
                      "avg_client_time", "avg_throughput", "client_success", "client_fail",
                      "server_success", "server_fail"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for i, r in enumerate(results):
            if r["client_success"] == 1:
                # Prepare the row to write
                row_to_write = {
                    "no": next_row_num + i,
                    "operation": r["task"],
                    "volume": r["file"],
                    "client_pool_size": r["clients"],
                    "server_pool_size": server_workers,
                    "avg_client_time": r["avg_client_time"],
                    "avg_throughput": r["avg_throughput"],
                    "client_success": r["client_success"],
                    "client_fail": r["client_fail"],
                    "server_success": r["server_success"],
                    "server_fail": r["server_fail"]
                }

                row_key = (row_to_write["operation"], row_to_write["volume"],
                           row_to_write["client_pool_size"], row_to_write["server_pool_size"])

                if not any(
                    (row["operation"], row["volume"], row["client_pool_size"], row["server_pool_size"]) == row_key
                    for row in existing_data
                ):
                    writer.writerow(row_to_write)
                    existing_data.append(row_to_write)

    print(f"✅ Hasil ada di : {file_path}")

def main():
    create_files()
    combinations = [
        (t, f, c)
        for t in ["download", "upload"]
        for f in ["10MB.txt", "50MB.txt"] #,"100MB.txt"]
        for c in [1, 5, 50]
    ]

    print("Test combinations:", combinations)
    results = []

    server_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    for task, file, clients in combinations:
        r = run_stress_test(task, file, clients, server_workers)
        results.append(r)

    write_result(results)

if __name__ == "__main__":
    main()