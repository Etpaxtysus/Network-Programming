import os
import json
import base64
from glob import glob
import logging


class FileInterface:

    def __init__(self):
        os.chdir('files/')

    def list(self, params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fp = open(f"{filename}", 'rb')
            isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            filecontent = params[1]
            logging.warning(f"String base64 sebelum decode (server): {filecontent}")  # Log string

            # Penanganan padding eksplisit
            missing_padding = len(filecontent) % 4
            if missing_padding:
                filecontent += '=' * (4 - missing_padding)

            filecontent = base64.b64decode(filecontent)
            if (filename == ''):
                return dict(status='ERROR', data='Nama file harus diisi')
            fp = open(f"{filename}", 'wb+')
            fp.write(filecontent)
            fp.close()
            return dict(status='OK', data='File berhasil diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return dict(status='ERROR', data='Nama file harus diisi')
            os.remove(f"{filename}")
            return dict(status='OK', data='File berhasil dihapus')
        except Exception as e:
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))