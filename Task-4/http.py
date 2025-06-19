import os
import os.path
from glob import glob
from datetime import datetime
import json
import base64

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
        self.public_dir = 'storage'
        if not os.path.exists(self.public_dir):
            os.makedirs(self.public_dir)
            print(f"Directory '{self.public_dir}' created.")

    
    def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append(f"HTTP/1.0 {kode} {message}\r\n") 
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers="".join(resp)
        
        if not isinstance(messagebody, bytes):
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self,data_string):
        print(f'data_string: {data_string}')
        try:
            head_str, body_str = data_string.split('\r\n\r\n', 1)
        except ValueError:
            head_str = data_string
            body_str = ""

        request_lines = head_str.split('\r\n')
        baris = request_lines[0]
        all_headers = request_lines[1:]
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.get(object_address, all_headers)
            elif method == 'POST':
                return self.post(object_address, all_headers, body_str.encode())
            elif method == 'DELETE':
                return self.delete(object_address, all_headers)
            else:
                return self.response(405, 'Method Not Allowed', 'This HTTP method is not allowed.', {})
        except IndexError:
            return self.response(400, 'Bad Request', 'The request format is invalid.', {})

    def get(self,object_address,headers):
        if object_address == '/':
            return self.response(200, 'OK', 'Ini adalah web server percobaan', {})
        
        if (object_address == '/list'):
            try:
                files = os.listdir(self.public_dir)
                
                response_data = {"status": "success", "files": files}
                response_body = json.dumps(response_data)
                return self.response(200, 'OK', response_body, {'Content-Type': 'application/json'})
            except Exception as e:
                error_data = {"status": "error", "message": f"Failed to list directory: {str(e)}"}
                response_body = json.dumps(error_data)
                return self.response(500, 'Internal Server Error', response_body, {'Content-Type': 'application/json'})

        object_address = object_address.lstrip('/')
        file_path = os.path.join(self.public_dir, object_address)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as fp:
                    isi = fp.read()
                          
                ext = os.path.splitext(file_path)[1].lower()
                content_type = self.types.get(ext, 'application/octet-stream')

                return self.response(200, 'OK', isi, {'Content-Type': content_type})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f"Error reading file: {str(e)}", {})
        else:
            return self.response(404, 'Not Found', 'The requested file was not found on the server.', {})
        
    def post(self, object_address, headers, body):
        if object_address != '/upload':
            return self.response(404, 'Not Found', 'POST requests are only supported for the /upload endpoint.', {})
        
        filename = None
        for header in headers:
            if header.lower().startswith('x-filename:'):
                filename = os.path.basename(header.split(':', 1)[1].strip())
                break
        if not filename:
            return self.response(400, 'Bad Request', 'X-Filename header is missing.', {})

        save_path = os.path.join(self.public_dir, filename)
        try:
            base64_bytes = body.decode('utf-8')
            original_binary_data = base64.b64decode(base64_bytes)
            with open(save_path, 'wb') as f:
                f.write(original_binary_data)
            response_data = json.dumps({"status": "success", "message": f"File '{filename}' successfully uploaded."})
            return self.response(201, 'Created', response_data, {'Content-Type': 'application/json'})
        except Exception as e:
            error_details = json.dumps({"status": "error", "message": f"Failed to upload file: {str(e)}"})
            return self.response(500, 'Internal Server Error', error_details, {'Content-Type': 'application/json'})

    def delete(self, object_address, headers):
        if not object_address.startswith('/delete/'):
            return self.response(400, 'Bad Request', 'Invalid endpoint format. Use /delete/filename.', {})

        filename_to_delete = os.path.basename(object_address[len('/delete/'):])

        if not filename_to_delete:
            return self.response(400, 'Bad Request', 'File name cannot be empty for deletion.', {})

        file_path = os.path.join(self.public_dir, filename_to_delete)

        if not os.path.isfile(file_path):
            response_data = json.dumps({"status": "error", "message": f"File '{filename_to_delete}' not found on server for deletion."})
            return self.response(404, 'Not Found', response_data, {'Content-Type': 'application/json'})

        try:
            os.remove(file_path)
            return self.response(200, 'OK', f'File "{filename_to_delete}" has been successfully deleted.', {})
        except Exception as e:
            response_data = json.dumps({"status": "error", "message": f"Failed to delete file: {e}"})
            return self.response(500, 'Internal Server Error', response_data, {'Content-Type': 'application/json'})

if __name__=="__main__":
    httpserver = HttpServer()
    pass