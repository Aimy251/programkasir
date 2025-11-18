#-------------------------------------------------------------------------------
# File: sistem_kasir_diperbarui.py
# Deskripsi: Sistem kasir sederhana - versi diperbarui
# Penambahan fitur:
# - Pencarian produk (barcode / nama)
# - Filter produk (stok range, harga range, diskon, stok rendah)
# - Opsi sorting dinamis (nama, stok, harga, diskon; asc/desc)
# - Opsi edit dan hapus produk dari daftar
# - Menu manajemen stok interaktif
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

# Helper: cari produk berdasarkan nama (case-insensitive) -> mengembalikan list barcode
def cari_by_nama(query):
    q = query.strip().lower()
    hasil = [bc for bc, p in produk_data.items() if q in p.get('nama','').lower()]
    return hasil

# -------------------------------------------------------------------------------
# MANAJEMEN PRODUK & STOK (FUNGSI UTAMA BARU: SEARCH / FILTER / SORT / EDIT / DELETE)
# -------------------------------------------------------------------------------

# #101 - Fungsi Tambah/Edit Produk (dipakai juga untuk edit lengkap)
def tambah_produk(edit_mode=False, barcode_target=None):
    """Menambahkan produk baru atau mengedit yang sudah ada. Jika edit_mode True, akan mengedit barcode_target."""
    print("\n--- TAMBAH / EDIT PRODUK ---")
    if edit_mode and barcode_target:
        barcode = barcode_target
        produk = produk_data.get(barcode, {})
        print(f"Mengedit produk dengan barcode: {barcode}")
        nama = input(f"Nama Produk [{produk.get('nama','')}]: ").strip() or produk.get('nama','')
    else:
        barcode = input("Masukkan Barcode Produk (tekan enter untuk batal): ").strip()
        if not barcode:
            return
        if barcode in produk_data:
            print("Barcode sudah ada - akan memperbarui data produk tersebut.")
        nama = input("Masukkan Nama Produk: ").strip()

    # Validasi Harga
    while True:
        try:
            harga_raw = input("Masukkan Harga Produk (contoh: 15000)" + (" [kosong = tidak berubah]" if edit_mode and barcode in produk_data else "") + ": ")
            if harga_raw == '' and edit_mode and barcode in produk_data:
                harga = produk_data[barcode]['harga']
                break
            harga = float(harga_raw)
            if harga < 0:
                print("Harga tidak boleh negatif.")
                continue
            break
        except ValueError:
            print("Input harga tidak valid. Harap masukkan angka.")

    # Validasi Stok
    while True:
        try:
            stok_raw = input("Masukkan Stok Awal" + (" [kosong = tidak berubah]" if edit_mode and barcode in produk_data else "") + ": ")
            if stok_raw == '' and edit_mode and barcode in produk_data:
                stok = produk_data[barcode]['stok']
                break
            stok = int(stok_raw)
            if stok < 0:
                print("Stok tidak boleh negatif.")
                continue
            break
        except ValueError:
            print("Input stok tidak valid. Harap masukkan bilangan bulat.")

    # Validasi Diskon
    while True:
        try:
            diskon_prompt = "Masukkan Diskon (0-100%)"
            diskon_raw = input(diskon_prompt + (" [kosong = tidak berubah]" if edit_mode and barcode in produk_data else "") + ": ")
            if diskon_raw == '' and edit_mode and barcode in produk_data:
                diskon = produk_data[barcode]['diskon']
                diskon_persen = int(diskon * 100)
                break
            diskon_persen = float(diskon_raw)
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

# Utility: tampilkan daftar produk (dari list barcode atau semua jika None)
def tampilkan_daftar(barcodes=None, judul="DAFTAR PRODUK"):
    print("\n" + "="*40)
    print(f"      📦 {judul}      ")
    print("="*40)

    if barcodes is None:
        items = list(produk_data.items())
    else:
        items = [(bc, produk_data[bc]) for bc in barcodes if bc in produk_data]

    if not items:
        print("Belum ada produk yang cocok untuk ditampilkan.")
        return

    print(f"{'No':<4}{'Barcode':<16}{'Nama':<30}{'Stok':<8}{'Harga':<16}{'Diskon':<8}")
    print("-" * 90)
    i = 1
    for barcode, p in items:
        nama_pendek = p['nama'][:27] + '...' if len(p['nama']) > 30 else p['nama']
        diskon_persen = int(p.get('diskon', 0.0) * 100)
        print(f"{i:<4}{barcode:<16}{nama_pendek:<30}{p.get('stok',0):<8}{format_harga(p.get('harga',0.0)):<16}{diskon_persen}%")
        i += 1
    print("-" * 90)

# #103 - Fitur Pencarian (nama atau barcode)
def cari_produk_interaktif():
    print("\n--- PENCARIAN PRODUK ---")
    q = input("Masukkan barcode atau nama (bagian nama diterima): ").strip()
    if not q:
        print("Pencarian dibatalkan.")
        return

    # cek barcode langsung
    kode = cari_barcode(q)
    if kode:
        tampilkan_daftar([kode], judul=f"Hasil Pencarian untuk '{q}'")
        return

    # cari berdasarkan nama
    hasil = cari_by_nama(q)
    tampilkan_daftar(hasil, judul=f"Hasil Pencarian untuk '{q}'")

# #104 - Fitur Filter (stok range, harga range, diskon, stok rendah)
def filter_produk_interaktif():
    print("\n--- FILTER PRODUK ---")
    print("Kosongkan input jika ingin melewatkan kriteria tertentu.")
    try:
        stok_min_raw = input("Stok minimal: ")
        stok_min = int(stok_min_raw) if stok_min_raw.strip() != '' else None
    except ValueError:
        print("Input stok minimal tidak valid. Mengabaikan kriterium ini.")
        stok_min = None

    try:
        stok_max_raw = input("Stok maksimal: ")
        stok_max = int(stok_max_raw) if stok_max_raw.strip() != '' else None
    except ValueError:
        print("Input stok maksimal tidak valid. Mengabaikan kriterium ini.")
        stok_max = None

    try:
        harga_min_raw = input("Harga minimal: ")
        harga_min = float(harga_min_raw) if harga_min_raw.strip() != '' else None
    except ValueError:
        print("Input harga minimal tidak valid. Mengabaikan kriterium ini.")
        harga_min = None

    try:
        harga_max_raw = input("Harga maksimal: ")
        harga_max = float(harga_max_raw) if harga_max_raw.strip() != '' else None
    except ValueError:
        print("Input harga maksimal tidak valid. Mengabaikan kriterium ini.")
        harga_max = None

    diskon_only_raw = input("Hanya yang ada diskon? (Y/N): ").strip().upper()
    diskon_only = True if diskon_only_raw == 'Y' else (False if diskon_only_raw == 'N' else None)

    hasil = []
    for bc, p in produk_data.items():
        s = p.get('stok', 0)
        h = p.get('harga', 0.0)
        d = p.get('diskon', 0.0)

        if stok_min is not None and s < stok_min:
            continue
        if stok_max is not None and s > stok_max:
            continue
        if harga_min is not None and h < harga_min:
            continue
        if harga_max is not None and h > harga_max:
            continue
        if diskon_only is True and d <= 0:
            continue
        if diskon_only is False and d > 0:
            continue

        hasil.append(bc)

    tampilkan_daftar(hasil, judul="Hasil Filter")

# #105 - Fitur Sorting Dinamis
def sort_produk_interaktif():
    print("\n--- SORTING PRODUK ---")
    print("Field tersedia: nama, stok, harga, diskon")
    field = input("Pilih field untuk sorting: ").strip().lower()
    if field not in ['nama','stok','harga','diskon']:
        print("Field tidak valid. Sorting dibatalkan.")
        return
    order = input("Urutkan naik atau turun? (asc/desc): ").strip().lower()
    reverse = True if order == 'desc' else False

    # Buat daftar pasangan (barcode, produk)
    items = list(produk_data.items())

    if field == 'nama':
        items.sort(key=lambda kv: kv[1].get('nama','').lower(), reverse=reverse)
    else:
        items.sort(key=lambda kv: kv[1].get(field, 0), reverse=reverse)

    barcodes_sorted = [kv[0] for kv in items]
    tampilkan_daftar(barcodes_sorted, judul=f"Produk Terurut berdasarkan {field} ({'desc' if reverse else 'asc'})")

# #106 - Hapus Produk
def hapus_produk_interaktif():
    print("\n--- HAPUS PRODUK ---")
    barcode = input("Masukkan Barcode produk yang ingin dihapus (tekan enter untuk batal): ").strip()
    if not barcode:
        return
    kode = cari_barcode(barcode)
    if not kode:
        print("Produk tidak ditemukan.")
        return
    confirm = input(f"Yakin ingin menghapus produk {produk_data[kode]['nama']} (Barcode: {kode})? (Y/N): ").strip().upper()
    if confirm == 'Y':
        del produk_data[kode]
        simpan_data()
        print("✅ Produk berhasil dihapus.")
    else:
        print("Penghapusan dibatalkan.")

# #107 - Edit Produk (memanggil tambah_produk dengan edit_mode)
def edit_produk_interaktif():
    print("\n--- EDIT PRODUK ---")
    barcode = input("Masukkan Barcode produk yang ingin diedit (tekan enter untuk batal): ").strip()
    if not barcode:
        return
    kode = cari_barcode(barcode)
    if not kode:
        print("Produk tidak ditemukan.")
        return
    tambah_produk(edit_mode=True, barcode_target=kode)

# Menu manajemen stok interaktif
def kelola_stok_interaktif():
    while True:
        print("\n--- MANAJEMEN STOK (INTERAKTIF) ---")
        print("1. Tampilkan Semua Produk")
        print("2. Cari Produk")
        print("3. Filter Produk")
        print("4. Sort Produk")
        print("5. Tambah/Edit Produk")
        print("6. Edit Produk (khusus)")
        print("7. Hapus Produk")
        print("8. Pembelian Stok (Stock In)")
        print("9. Kembali")
        pilihan = input("Pilih aksi (1-9): ").strip()

        if pilihan == '1':
            tampilkan_daftar()
        elif pilihan == '2':
            cari_produk_interaktif()
        elif pilihan == '3':
            filter_produk_interaktif()
        elif pilihan == '4':
            sort_produk_interaktif()
        elif pilihan == '5':
            tambah_produk()
        elif pilihan == '6':
            edit_produk_interaktif()
        elif pilihan == '7':
            hapus_produk_interaktif()
        elif pilihan == '8':
            pembelian_stok()
        elif pilihan == '9':
            break
        else:
            print("Pilihan tidak valid.")

# -------------------------------------------------------------------------------
# MODE KASIR (PENJUALAN)  -- tetap sama, hanya sedikit refactor untuk pemanggilan fungsi
# -------------------------------------------------------------------------------

def mode_kasir():
    """Memproses transaksi penjualan."""
    print("\n==================================")
    print("      🛒 MODE KASIR (PENJUALAN)      ")
    print("==================================")

    keranjang = {}
    total_belanja = 0.0

    try:
        while True:
            print("\n--- Transaksi Saat Ini ---")
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

                total_belanja = sum(item['subtotal'] for item in keranjang.values())
                print("-" * 70)
                print(f"{'TOTAL BELANJA':<55}{format_harga(total_belanja):<15}")

            raw_input_aksi = input("\nScan Barcode, atau ketik 'BAYAR', 'BATAL', 'CANCEL <barcode>': ").strip()
            if not raw_input_aksi:
                continue
            input_aksi = raw_input_aksi.upper()

            if input_aksi == 'BAYAR':
                if total_belanja > 0:
                    proses_pembayaran(keranjang, total_belanja)
                    break
                else:
                    print("Keranjang masih kosong.")
                    continue

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

                harga_satuan = produk['harga']
                diskon_persen = produk['diskon']
                diskon_per_item = harga_satuan * diskon_persen
                harga_setelah_diskon = harga_satuan - diskon_per_item
                subtotal = harga_setelah_diskon * jumlah
                diskon_total = diskon_per_item * jumlah

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

                produk_data[kode]['stok'] -= jumlah
                print(f"✅ {jumlah} item {produk['nama']} ditambahkan ke keranjang.")
                simpan_data()
                continue

            print("❌ Barcode atau perintah tidak dikenal. Coba lagi.")
    except KeyboardInterrupt:
        if keranjang:
            for bc, it in keranjang.items():
                produk_data[bc]['stok'] += it['jumlah']
            simpan_data()
        print("\nProgram dibatalkan oleh pengguna. Kembali ke menu utama.")
        return

# #208 - Fungsi Proses Pembayaran & Cetak Struk (sama seperti sebelumnya)
def proses_pembayaran(keranjang, total_belanja):
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
            for bc, it in keranjang.items():
                produk_data[bc]['stok'] += it['jumlah']
            simpan_data()
            return

    kembalian = bayar - total_belanja
    waktu_transaksi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_transaksi = datetime.now().strftime("%Y%m%d%H%M%S")

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
    simpan_data()

    print("\n\n" + "="*50)
    print("              STRUK PEMBAYARAN")
    print(f"ID Transaksi : {id_transaksi}")
    print(f"Tanggal/Waktu: {waktu_transaksi}")
    print("-"*50)
    print(f"{'Produk':<20}{'Harga/pc':<12}{'Jml':<5}{'Subtotal':<12}")
    print("-" * 50)

    total_diskon = 0
    for barcode, item in keranjang.items():
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
# LAPORAN PENJUALAN (tetap sama)
# -------------------------------------------------------------------------------

def tampilkan_laporan():
    print("\n==================================")
    print("      📈 LAPORAN PENJUALAN      ")
    print("==================================")

    if not laporan_penjualan:
        print("Belum ada transaksi penjualan.")
        return

    total_semua_penjualan = 0.0
    for transaksi in laporan_penjualan:
        if 'total' in transaksi:
            total_semua_penjualan += transaksi['total']
        elif 'total_bersih' in transaksi:
            total_semua_penjualan += transaksi['total_bersih']

    print(f"Total Transaksi: {len(laporan_penjualan)}")
    print(f"Total Pendapatan Kotor: {format_harga(total_semua_penjualan)}\n")

    print("--- 5 TRANSAKSI TERBARU ---")
    riwayat_tampil = laporan_penjualan[-5:]

    print(f"{'ID Transaksi':<16}{'Waktu':<20}{'Total':<14}")
    print("-" * 50)

    for laporan in reversed(riwayat_tampil):
        transaksi_total = laporan.get('total', laporan.get('total_bersih', 0.0))
        print(
            f"{laporan['id_transaksi'][8:]:<16}"
            f"{laporan['waktu']:<20}"
            f"{format_harga(transaksi_total):<14}"
        )
    print("-" * 50)

# -------------------------------------------------------------------------------
# MENU UTAMA
# -------------------------------------------------------------------------------

def menu_utama():
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
            while True:
                print("\n--- MANAJEMEN PRODUK ---")
                print("1. Kelola Stok (Interaktif: cari, filter, sort, edit, hapus)")
                print("2. Tambah/Edit Produk (langsung)")
                print("3. Pembelian Stok (Stock In)")
                print("4. Tampilkan Semua Stok Produk")
                print("5. Kembali ke Menu Utama")
                pilihan_manajemen = input("Pilih aksi (1-5): ").strip()

                if pilihan_manajemen == '1':
                    kelola_stok_interaktif()
                elif pilihan_manajemen == '2':
                    tambah_produk()
                elif pilihan_manajemen == '3':
                    pembelian_stok()
                elif pilihan_manajemen == '4':
                    tampilkan_daftar()
                elif pilihan_manajemen == '5':
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
