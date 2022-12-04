# IF3130 Jaringan Komputer

> _Repository ini ditujukan untuk memenuhi Tugas Besar 2 IF3130_

## Deskripsi
   Program ini bertujuan untuk membuat simulasi pengiriman data antara server dan client melalui jaringan dengan menggunakan protokol transport layer. Program dibuat dengan bahasa pemrograman Python 3 dan library bawaannya. Program dijalankan di lingkungan sistem operasi berbasis Linux dengan server dan client dibuat secara terpisah dan dijalankan secara terpisah. Server dan client akan saling mengirim dan menerima berkas file yang merupakan data binary.

## Requirements
Untuk menjalankan program pastikan Anda telah mendownload dan menginstall hal-hal berikut:
1. Teks editor
2. Python 3
3. WSL/VM (jika menggunakan Windows)

## How To Install
1. Teks Editor yang kami sarankan adalah Visual Studio Code yang panduan download dan installnya dapat dilihat pada tautan berikut ini [vscode](https://www.belajarisme.com/tutorial/install-vscode/#:~:text=Sekarang%20mari%20kita%20install%20VSCode%20dengan%20cara%20berikut,Select%20Star%20Menu%20Folder%20klik%20Next.%20More%20items)
2. Panduan instalasi Python 3 dapat dilihat pada tautan berikut [Python 3](https://www.sebardi.id/2021/05/cara-instal-python-395-di-windows-10.html)
3. Panduan instalasi WSL dapat dilihat pada tautan berikut [WSL](https://www.youtube.com/watch?v=X-DHaQLrBi8)

## How To Run
1. Clone repository ini
2. Buka minimal 2 buah window WSL, satu untuk server dan yang lainnya untuk client (dapat membuka lebih dari 2 window jika menginginkan jumlah client lebih dari 1)
3. Sesuaikan directory dengan folder repository ini untuk masing-masing window
4. Pada window pertama (server), ketik dan enter command line berikut:
```
$ python3 server.py [broadcast port] [path file input]
```
5. Pada window sisanya (client), ketik dan enter command line berikut:
```
$ python3 client.py [client port] [broadcast port] [path output]
```

## Contributor
<table>
  <tr >
      <td><b>Nama</b></td>
      <td><b>NIM</b></td>
    </tr>
    <tr >
      <td><b>Daniel Salim</b></td>
      <td>13520008</td>
    </tr>
    <tr>
      <td><b>Muhammad Gilang Ramadhan</b></td>
      <td>13520137</td>
    </tr>
    <tr>
      <td><b>Febryola Kurnia Putri</b></td>
      <td>13520140</td>
    </tr>
</table>
