# Impor FUNGSI dari file layanan_gaji
# Perhatikan, kita tambah 'ambil_semua_slip'
from layanan_gaji import hitung_gaji_kotor, simpan_slip_gaji, ambil_semua_slip
# Impor 'db' untuk cek koneksi
from firebase_config import db

def input_slip_baru():
    """
    Fungsi ini HANYA mengurus proses input dan output
    untuk menambah slip gaji baru.
    """
    print("\n--- Menu 1: Input Slip Gaji Baru ---")
    
    # 1. INPUT (Tampilan Pengguna)
    nama_karyawan = input("Masukkan Nama Karyawan: ")
    jam_kerja_str = input("Masukkan Total Jam Kerja: ")
    gaji_per_jam_str = input("Masukkan Gaji per Jam (contoh: 15000): ")

    try:
        jam_kerja = float(jam_kerja_str)
        gaji_per_jam = float(gaji_per_jam_str)

        # 2. PROSES (Panggil "Otak")
        gaji_kotor = hitung_gaji_kotor(jam_kerja, gaji_per_jam)

        # 3. OUTPUT (Tampilan Pengguna)
        print("\n===== SLIP GAJI KARYAWAN =====")
        print(f"Nama Karyawan: {nama_karyawan}")
        print(f"Total Gaji Kotor: Rp {gaji_kotor}")
        print("================================")

        # 4. SIMPAN (Panggil "Otak")
        print("\nMencoba menyimpan data ke Firebase...")
        
        data_untuk_disimpan = {
            'nama': nama_karyawan,
            'jam_kerja': jam_kerja,
            'gaji_per_jam': gaji_per_jam,
            'gaji_kotor': gaji_kotor
        }
        
        doc_id = simpan_slip_gaji(data_untuk_disimpan)
        
        if doc_id:
            print(f">>> Data BERHASIL disimpan di Firebase!")
            print(f"    Document ID: {doc_id}")
        else:
            print(">>> Data GAGAL disimpan.")

    except ValueError:
        print("\nERROR: Jam kerja dan Gaji per Jam harus berupa angka.")

def tampilkan_semua_slip():
    """
    Fungsi ini HANYA mengurus proses menampilkan
    semua data slip gaji.
    """
    print("\n--- Menu 2: Tampilkan Semua Slip Gaji ---")
    print("Mengambil data dari Firebase (diurutkan dari terbaru)...")
    
    # Panggil "Otak" untuk ambil data
    semua_slip = ambil_semua_slip()
    
    if not semua_slip:
        print("\nBelum ada data slip gaji yang tersimpan.")
        return

    print(f"\nTotal slip ditemukan: {len(semua_slip)}")
    print("--------------------------------------------------")
    
    # Loop dan tampilkan setiap data
    for slip in semua_slip:
        # .get() dipakai agar aman jika data/field-nya tidak ada
        nama = slip.get('nama', 'N/A')
        gaji = slip.get('gaji_kotor', 0)
        tanggal = slip.get('tanggal_simpan', None)
        
        # Ubah format tanggal agar gampang dibaca
        if tanggal:
            tanggal_str = tanggal.strftime("%Y-%m-%d %H:%M")
        else:
            tanggal_str = "Tanggal tidak ada"

        print(f"[{tanggal_str}] - {nama} - Gaji: Rp {gaji}")
    
    print("--------------------------------------------------")

def main():
    """
    Fungsi utama yang berisi MENU dan LOOPING.
    """
    print("\n===== Aplikasi Gaji Toko Sembako (Menu Utama) =====")
    
    while True:
        # Tampilkan Pilihan Menu
        print("\nPILIH MENU:")
        print("1. Input Slip Gaji Baru")
        print("2. Lihat Semua Slip Gaji (Terbaru dulu)")
        print("3. Keluar")
        pilihan = input("Masukkan pilihan (1/2/3): ")

        if pilihan == '1':
            input_slip_baru()
        elif pilihan == '2':
            tampilkan_semua_slip()
        elif pilihan == '3':
            print("\nTerima kasih, aplikasi ditutup.")
            break # Hentikan loop 'while True'
        else:
            print("\nPilihan tidak valid. Silakan masukkan 1, 2, atau 3.")

# --- Ini adalah baris yang akan dijalankan pertama kali ---
if __name__ == "__main__":
    if db: # Cek dulu, apakah koneksi Firebase berhasil?
        main() # Jalankan fungsi 'main' yang berisi menu
    else:
        print("\nAplikasi GAGAL berjalan karena tidak bisa konek ke database.")