# Tugas 3 - Pemrograman Jaringan

## Deskripsi

Sistem file server ini memungkinkan client untuk berinteraksi dengan server untuk mengelola file. Fitur-fiturnya meliputi melihat daftar file, mengunduh file, mengunggah file, dan menghapus file. Komunikasi antara client dan server menggunakan protokol berbasis teks sederhana.

## Arsitektur

Sistem ini terdiri dari komponen-komponen berikut:

* **Server (`file_server.py`):**
    * Mendengarkan koneksi dari client.
    * Memproses request client dan mengirimkan response.
    * Menggunakan threading untuk menangani banyak client secara bersamaan.
* **Client (`file_client_cli.py`):**
    * Mengirimkan request ke server.
    * Menerima dan memproses response dari server.
    * Menyediakan fungsi-fungsi untuk berinteraksi dengan server (list, get, upload, delete).
* **Protokol (`PROTOKOL.txt`, `file_protocol.py`):**
    * Mendefinisikan aturan komunikasi antara client dan server.
    * `file_protocol.py` mengimplementasikan logika untuk memproses string request dari client dan menerjemahkannya menjadi tindakan server.
* **Interface File (`file_interface.py`):**
    * Menyediakan abstraksi untuk operasi file (list, get, upload, delete).
    * Menangani pembacaan dan penulisan file aktual di server.

## Cara Menggunakan

1.  **Jalankan Server:**
    * Pastikan server (`file_server.py`) berjalan terlebih dahulu.
2.  **Jalankan Client:**
    * Jalankan client (`file_client_cli.py`) untuk berinteraksi dengan server.
3.  **Perintah Client:**
    * `remote_list()`: Mendapatkan daftar file di server.
    * `remote_get(filename)`: Mengunduh file dari server.
    * `remote_upload(filename)`: Mengunggah file ke server.
    * `remote_delete(filename)`: Menghapus file dari server.

## Protokol

Komunikasi client-server berbasis teks dengan format:

```
REQUEST spasi PARAMETER1 spasi PARAMETER2 ...
```

Response dari server berupa JSON string yang diakhiri dengan `\r\n\r\n`.

## Catatan

* File diunggah dalam format base64.
* Server menyimpan file di direktori `files/`.