#-------------------------------------------------------------------------------
# File: sistem_kasir.py
# Deskripsi: Sistem kasir sederhana untuk bisnis pribadi (versi diperbaiki)
# Menambahkan fitur: tampilkan semua stok produk beserta jumlahnya pada manajemen produk
#-------------------------------------------------------------------------------

import json
from datetime import datetime

# #001 - Konfigurasi File Data
DATA_FILE = 'data_produk.json'
LAPORAN_FILE = 'laporan_penjualan.json'

# #002 - Variabel Global untuk Data
# Struktur data produk: {barcode: {'nama': str, 'harga': float, 'stok': int, 'diskon': float (0.0 - 1.0)}}
produk_data = {}
laporan_penjualan = []

# #003 - Fungsi Load Data
def muat_data(filename, default_value):
    """Memuat data dari file JSON. Mengembalikan nilai default jika file tidak ditemukan."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ File data '{filename}' tidak ditemukan. Membuat data baru...")
        return default_value
    except json.JSONDecodeError:
        print(f"❌ Kesalahan saat membaca file JSON '{filename}'. Mengembalikan nilai default.")
        return default_value

# #004 - Fungsi Save Data
def simpan_data():
    """Menyimpan data produk dan laporan ke file JSON."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(produk_data, f, indent=4, ensure_ascii=False)
        with open(LAPORAN_FILE, 'w') as f:
            json.dump(laporan_penjualan, f, indent=4, ensure_ascii=False)
        print("✅ Data produk dan laporan berhasil disimpan.")
    except Exception as e:
        print(f"❌ Kesalahan saat menyimpan data: {e}")

# #005 - Fungsi Inisialisasi Program
def inisialisasi():
    """Memuat semua data saat program dimulai."""
    global produk_data, laporan_penjualan
    produk_data = muat_data(DATA_FILE, {})
    laporan_penjualan = muat_data(LAPORAN_FILE, [])

# #006 - Fungsi untuk Memformat Harga
def format_harga(harga):
    """Mengubah float menjadi format mata uang IDR."""
    try:
        harga = float(harga)
    except (TypeError, ValueError):
        harga = 0.0
    return f"Rp {harga:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Helper: cari barcode case-insensitive
def cari_barcode(input_barcode):
    """Mengembalikan key barcode asli dari input (case-insensitive), atau None jika tidak ada."""
    if input_barcode in produk_data:
        return input_barcode
    ib_up = input_barcode.upper()
    for k in produk_data.keys():
        if k.upper() == ib_up:
            return k
    return None

# -------------------------------------------------------------------------------
# MANAJEMEN PRODUK & STOK
# -------------------------------------------------------------------------------

# #101 - Fungsi Tambah/Edit Produk
def tambah_produk():
    """Menambahkan produk baru atau mengedit yang sudah ada."""
    print("\n--- TAMBAH / EDIT PRODUK ---")
    barcode = input("Masukkan Barcode Produk (tekan enter untuk batal): ").strip()
    if not barcode:
        return

    nama = input("Masukkan Nama Produk: ").strip()

    # Validasi Harga
    while True:
        try:
            harga = float(input("Masukkan Harga Produk (contoh: 15000): "))
            if harga < 0:
                print("Harga tidak boleh negatif.")
                continue
            break
        except ValueError:
            print("Input harga tidak valid. Harap masukkan angka.")

    # Validasi Stok
    while True:
        try:
            stok = int(input("Masukkan Stok Awal: "))
            if stok < 0:
                print("Stok tidak boleh negatif.")
                continue
            break
        except ValueError:
            print("Input stok tidak valid. Harap masukkan bilangan bulat.")

    # Validasi Diskon
    while True:
        try:
            diskon_persen = float(input("Masukkan Diskon (0-100%): "))
            if 0 <= diskon_persen <= 100:
                diskon = diskon_persen / 100
                break
            else:
                print("Diskon harus antara 0 sampai 100.")
        except ValueError:
            print("Input diskon tidak valid. Harap masukkan angka.")

    produk_data[barcode] = {
        'nama': nama,
        'harga': harga,
        'stok': stok,
        'diskon': diskon
    }
    print(f"\n✅ Produk {nama} (Barcode: {barcode}) berhasil ditambahkan/diperbarui.")
    print(f"Harga: {format_harga(harga)}, Stok: {stok}, Diskon: {diskon_persen}%")
    simpan_data()

# #102 - Fungsi Pembelian (Stock In)
def pembelian_stok():
    """Menambah stok produk yang sudah ada (Pembelian/Stock In)."""
    print("\n--- PEMBELIAN STOK (STOCK IN) ---")
    barcode_in = input("Masukkan Barcode Produk yang akan ditambah stoknya (tekan enter untuk batal): ").strip()
    if not barcode_in:
        return

    kode = cari_barcode(barcode_in)
    if not kode:
        print(f"❌ Produk dengan barcode '{barcode_in}' tidak ditemukan.")
        return

    while True:
        try:
            jumlah_tambah = int(input("Masukkan Jumlah Stok yang Ditambah: "))
            if jumlah_tambah <= 0:
                print("Jumlah penambahan stok harus lebih dari 0.")
                continue
            break
        except ValueError:
            print("Input tidak valid. Harap masukkan bilangan bulat.")

    produk_data[kode]['stok'] += jumlah_tambah
    print(f"\n✅ Stok {produk_data[kode]['nama']} berhasil ditambahkan sebanyak {jumlah_tambah}.")
    print(f"Stok Baru: {produk_data[kode]['stok']}")
    simpan_data()

# #103 - Fungsi Tampilkan Semua Stok Produk (FITUR BARU)
def tampilkan_semua_stok():
    """Menampilkan semua produk beserta jumlah stoknya dalam format tabel."""
    print("\n==================================")
    print("      📦 DAFTAR STOK PRODUK      ")
    print("==================================")

    if not produk_data:
        print("Belum ada produk terdaftar.")
        return

    print(f"{'No':<4}{'Barcode':<16}{'Nama':<30}{'Stok':<8}{'Harga':<16}{'Diskon':<8}")
    print("-" * 90)
    i = 1
    # Sortir berdasarkan nama produk untuk keteraturan
    for barcode in sorted(produk_data.keys(), key=lambda k: produk_data[k]['nama'].lower()):
        p = produk_data[barcode]
        nama_pendek = p['nama'][:27] + '...' if len(p['nama']) > 30 else p['nama']
        diskon_persen = int(p.get('diskon', 0.0) * 100)
        print(f"{i:<4}{barcode:<16}{nama_pendek:<30}{p.get('stok',0):<8}{format_harga(p.get('harga',0.0)):<16}{diskon_persen}%")
        i += 1

    print("-" * 90)

# -------------------------------------------------------------------------------
# MODE KASIR (PENJUALAN)
# -------------------------------------------------------------------------------

# #201 - Fungsi Mode Kasir
def mode_kasir():
    """Memproses transaksi penjualan."""
    print("\n==================================")
    print("      🛒 MODE KASIR (PENJUALAN)      ")
    print("==================================")

    keranjang = {} # {barcode: {'nama': str, 'harga_satuan': float, 'jumlah': int, 'diskon_rp': float, 'subtotal': float}}
    total_belanja = 0.0

    try:
        while True:
            print("\n--- Transaksi Saat Ini ---")
            # #202 - Tampilkan Keranjang
            if not keranjang:
                print("Keranjang kosong.")
            else:
                print(f"{'No':<4}{'Produk':<20}{'Harga':<12}{'Jml':<5}{'Diskon':<12}{'Subtotal':<15}")
                print("-" * 70)
                i = 1
                for barcode, item in keranjang.items():
                    nama_pendek = item['nama'][:17] + '...' if len(item['nama']) > 20 else item['nama']
                    print(
                        f"{i:<4}{nama_pendek:<20}"
                        f"{format_harga(item['harga_satuan']):<12}"
                        f"{item['jumlah']:<5}"
                        f"{format_harga(item['diskon_rp']):<12}"
                        f"{format_harga(item['subtotal']):<15}"
                    )
                    i += 1

                # #203 - Hitung Total
                total_belanja = sum(item['subtotal'] for item in keranjang.values())
                print("-" * 70)
                print(f"{'TOTAL BELANJA':<55}{format_harga(total_belanja):<15}")

            # #204 - Input Barcode atau Aksi
            raw_input_aksi = input("\nScan Barcode, atau ketik 'BAYAR', 'BATAL', 'CANCEL <barcode>': ").strip()
            if not raw_input_aksi:
                continue
            input_aksi = raw_input_aksi.upper()

            # Perintah BAYAR
            if input_aksi == 'BAYAR':
                if total_belanja > 0:
                    proses_pembayaran(keranjang, total_belanja)
                    break
                else:
                    print("Keranjang masih kosong.")
                    continue

            # Perintah BATAL (batalkan transaksi saat ini, kembalikan stok)
            if input_aksi == 'BATAL':
                if keranjang:
                    for bc, it in keranjang.items():
                        produk_data[bc]['stok'] += it['jumlah']
                    keranjang.clear()
                    print("🚫 Transaksi dibatalkan dan stok dikembalikan.")
                    simpan_data()
                else:
                    print("Tidak ada transaksi untuk dibatalkan.")
                break

            # Perintah CANCEL <barcode>
            if input_aksi.startswith('CANCEL'):
                parts = raw_input_aksi.split(' ', 1)
                if len(parts) < 2:
                    print("Format CANCEL salah. Gunakan: CANCEL <barcode>")
                    continue
                barcode_cancel_raw = parts[1].strip()
                kode_cancel = cari_barcode(barcode_cancel_raw)
                if not kode_cancel:
                    print(f"❌ Barcode '{barcode_cancel_raw}' tidak ada di daftar produk.")
                    continue
                if kode_cancel in keranjang:
                    produk_data[kode_cancel]['stok'] += keranjang[kode_cancel]['jumlah']
                    del keranjang[kode_cancel]
                    print(f"✅ Item dengan barcode {kode_cancel} berhasil dibatalkan dari keranjang.")
                    simpan_data()
                else:
                    print(f"❌ Barcode {kode_cancel} tidak ada di keranjang.")
                continue

            # Jika user input adalah barcode (product)
            kode = cari_barcode(raw_input_aksi)
            if kode:
                produk = produk_data[kode]

                if produk['stok'] <= 0:
                    print(f"❌ Stok {produk['nama']} kosong!")
                    continue

                print(f"Produk: {produk['nama']} | Harga: {format_harga(produk['harga'])} | Stok Tersedia: {produk['stok']}")

                while True:
                    try:
                        jumlah = int(input(f"Masukkan Jumlah {produk['nama']} (Stok maks: {produk['stok']}): "))
                        if 0 < jumlah <= produk['stok']:
                            break
                        else:
                            print(f"Jumlah tidak valid. Harus antara 1 sampai {produk['stok']}.")
                    except ValueError:
                        print("Input tidak valid. Harap masukkan angka.")

                # Perhitungan
                harga_satuan = produk['harga']
                diskon_persen = produk['diskon']
                diskon_per_item = harga_satuan * diskon_persen
                harga_setelah_diskon = harga_satuan - diskon_per_item
                subtotal = harga_setelah_diskon * jumlah
                diskon_total = diskon_per_item * jumlah

                # Update keranjang (jika sudah ada, tambahkan jumlah & subtotal & diskon)
                if kode in keranjang:
                    keranjang[kode]['jumlah'] += jumlah
                    keranjang[kode]['subtotal'] += subtotal
                    keranjang[kode]['diskon_rp'] += diskon_total
                else:
                    keranjang[kode] = {
                        'nama': produk['nama'],
                        'harga_satuan': harga_satuan,
                        'jumlah': jumlah,
                        'diskon_rp': diskon_total,
                        'subtotal': subtotal
                    }

                # #207 - Kurangi Stok (Stock Out)
                produk_data[kode]['stok'] -= jumlah
                print(f"✅ {jumlah} item {produk['nama']} ditambahkan ke keranjang.")
                simpan_data()
                continue

            # Jika mencapai sini, perintah tidak dikenal
            print("❌ Barcode atau perintah tidak dikenal. Coba lagi.")
    except KeyboardInterrupt:
        # Jika user tekan Ctrl+C, kembalikan stok jika ada keranjang
        if keranjang:
            for bc, it in keranjang.items():
                produk_data[bc]['stok'] += it['jumlah']
            simpan_data()
        print("\nProgram dibatalkan oleh pengguna. Kembali ke menu utama.")
        return

# #208 - Fungsi Proses Pembayaran & Cetak Struk
def proses_pembayaran(keranjang, total_belanja):
    """Memproses pembayaran, mencetak struk, dan menyimpan laporan."""
    while True:
        try:
            bayar = float(input(f"TOTAL: {format_harga(total_belanja)}. Masukkan jumlah Bayar: "))
            if bayar >= total_belanja:
                break
            else:
                print("Jumlah pembayaran kurang. Harap masukkan jumlah yang cukup.")
        except ValueError:
            print("Input tidak valid. Harap masukkan angka.")
        except KeyboardInterrupt:
            print("\nPembayaran dibatalkan.")
            # Jika batal saat pembayaran, kembalikan stok yang ada di keranjang
            for bc, it in keranjang.items():
                produk_data[bc]['stok'] += it['jumlah']
            simpan_data()
            return

    kembalian = bayar - total_belanja
    waktu_transaksi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_transaksi = datetime.now().strftime("%Y%m%d%H%M%S") # ID unik sederhana

    # #209 - Simpan Laporan
    rincian_penjualan = [
        {'barcode': k, 'nama': v['nama'], 'jumlah': v['jumlah'], 'subtotal': v['subtotal']}
        for k, v in keranjang.items()
    ]
    laporan = {
        'id_transaksi': id_transaksi,
        'waktu': waktu_transaksi,
        'total': total_belanja,
        'rincian': rincian_penjualan
    }
    laporan_penjualan.append(laporan)
    simpan_data() # Simpan data produk (stok) dan laporan

    # #210 - Cetak Struk (print)
    print("\n\n" + "="*50)
    print("              STRUK PEMBAYARAN")
    print(f"ID Transaksi : {id_transaksi}")
    print(f"Tanggal/Waktu: {waktu_transaksi}")
    print("-"*50)
    print(f"{'Produk':<20}{'Harga/pc':<12}{'Jml':<5}{'Subtotal':<12}")
    print("-" * 50)

    total_diskon = 0
    for barcode, item in keranjang.items():
        # harga_setelah_diskon_per_item = (item['subtotal'] / item['jumlah'])
        total_diskon += item.get('diskon_rp', 0)
        print(
            f"{item['nama'][:19]:<20}"
            f"{format_harga(item['harga_satuan']):<12}"
            f"{item['jumlah']:<5}"
            f"{format_harga(item['subtotal']):<12}"
        )

    print("-" * 50)
    print(f"{'TOTAL HARGA':<38}{format_harga(total_belanja):>12}")
    print(f"{'DISKON DITERAPKAN':<38}{format_harga(total_diskon):>12}")
    print(f"{'BAYAR':<38}{format_harga(bayar):>12}")
    print(f"{'KEMBALIAN':<38}{format_harga(kembalian):>12}")
    print("="*50 + "\n")
    print("Terima kasih sudah berbelanja!")

# -------------------------------------------------------------------------------
# LAPORAN PENJUALAN
# -------------------------------------------------------------------------------

# #301 - Fungsi Laporan Penjualan
def tampilkan_laporan():
    """Menampilkan ringkasan laporan penjualan."""
    print("\n==================================")
    print("      📈 LAPORAN PENJUALAN      ")
    print("==================================")

    if not laporan_penjualan:
        print("Belum ada transaksi penjualan.")
        return

    total_semua_penjualan = 0.0
    for transaksi in laporan_penjualan:
        # Check for 'total' key first, then 'total_bersih' for backward compatibility
        if 'total' in transaksi:
            total_semua_penjualan += transaksi['total']
        elif 'total_bersih' in transaksi:
            total_semua_penjualan += transaksi['total_bersih']

    print(f"Total Transaksi: {len(laporan_penjualan)}")
    print(f"Total Pendapatan Kotor: {format_harga(total_semua_penjualan)}\n")

    # #302 - Menampilkan riwayat transaksi terbaru
    print("--- 5 TRANSAKSI TERBARU ---")
    riwayat_tampil = laporan_penjualan[-5:] # 5 transaksi terakhir

    print(f"{'ID Transaksi':<16}{'Waktu':<20}{'Total':<14}")
    print("-" * 50)

    for laporan in reversed(riwayat_tampil):
        # Use .get() with a fallback for 'total' key
        transaksi_total = laporan.get('total', laporan.get('total_bersih', 0.0))
        print(
            f"{laporan['id_transaksi'][8:]:<16}" # Tampilkan hanya jam/menit/detik
            f"{laporan['waktu']:<20}"
            f"{format_harga(transaksi_total):<14}"
        )
    print("-" * 50)


# -------------------------------------------------------------------------------
# MENU UTAMA
# -------------------------------------------------------------------------------

# #401 - Fungsi Menu Utama
def menu_utama():
    """Fungsi utama untuk menjalankan program."""
    inisialisasi()

    while True:
        print("\n==================================")
        print("      SISTEM KASIR BISNISKU      ")
        print("==================================")
        print("1. 🛒 Mode Kasir (Penjualan)")
        print("2. 📦 Manajemen Produk (Tambah/Edit, Stok, Tampilkan Stok)")
        print("3. 📈 Laporan Penjualan & Riwayat")
        print("4. ❌ Keluar Program")

        pilihan = input("Masukkan pilihan Anda (1-4): ").strip()

        if pilihan == '1':
            mode_kasir()
        elif pilihan == '2':
            # #402 - Sub Menu Manajemen
            while True:
                print("\n--- MANAJEMEN PRODUK ---")
                print("1. Tambah/Edit Produk (Barcode, Nama, Harga, Diskon)")
                print("2. Pembelian Stok (Stock In)")
                print("3. Tampilkan Semua Stok Produk")
                print("4. Kembali ke Menu Utama")
                pilihan_manajemen = input("Pilih aksi (1-4): ").strip()

                if pilihan_manajemen == '1':
                    tambah_produk()
                elif pilihan_manajemen == '2':
                    pembelian_stok()
                elif pilihan_manajemen == '3':
                    tampilkan_semua_stok()
                elif pilihan_manajemen == '4':
                    break
                else:
                    print("Pilihan tidak valid.")

        elif pilihan == '3':
            tampilkan_laporan()
        elif pilihan == '4':
            simpan_data()
            print("Program ditutup. Sampai jumpa! 👋")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# #403 - Jalankan Program
if __name__ == "__main__":
    menu_utama()
