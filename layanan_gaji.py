# Impor variabel 'db' dari file config kita
from firebase_config import db
import datetime
from firebase_admin import firestore # <- TAMBAHKAN INI

def hitung_gaji_kotor(jam_kerja, gaji_per_jam):
    """
    Fungsi murni untuk menghitung gaji.
    Menerima angka, mengembalikan angka.
    """
    return jam_kerja * gaji_per_jam

def simpan_slip_gaji(data_slip):
    """
    Fungsi untuk menyimpan data slip ke Firebase.
    Menerima data (dictionary), mengembalikan ID dokumen jika berhasil.
    """
    
    # Pastikan koneksi db ada (dari file config)
    if not db:
        print("ERROR: Koneksi database tidak ada. Data tidak tersimpan.")
        return None # Kembalikan 'None' untuk menandakan kegagalan

    try:
        # Tambahkan stempel waktu di sini, bukan di file utama
        data_slip['tanggal_simpan'] = datetime.datetime.now()
        
        # Kirim data ke collection 'slip_gaji'
        doc_ref = db.collection('slip_gaji').add(data_slip)
        
        # Kembalikan ID dokumen sebagai konfirmasi
        return doc_ref[1].id
    
    except Exception as e:
        print(f"ERROR saat mencoba menyimpan ke Firebase: {e}")
        return None
    
def ambil_semua_slip():
    """
    Fungsi untuk mengambil semua data slip dari Firebase.
    Daftar slip diurutkan berdasarkan tanggal terbaru.
    """
    if not db:
        print("ERROR: Koneksi database tidak ada.")
        return [] # Kembalikan daftar kosong jika gagal

    try:
        # Kita ambil data dari koleksi 'slip_gaji'
        # Kita urutkan berdasarkan 'tanggal_simpan', dari yang terbaru (DESCENDING)
        docs_stream = db.collection('slip_gaji').order_by(
            'tanggal_simpan', direction=firestore.Query.DESCENDING
        ).stream()
        
        semua_slip = []
        for doc in docs_stream:
            # doc.to_dict() adalah data (nama, gaji, dll)
            # doc.id adalah ID unik (DWem0bLrTcuqFP712T39)
            data = doc.to_dict()
            data['id'] = doc.id  # Kita selipkan ID-nya ke data
            semua_slip.append(data)
        
        return semua_slip
    
    except Exception as e:
        print(f"ERROR saat mengambil data dari Firebase: {e}")
        return [] # Kembalikan daftar kosong
    
def hapus_slip_gaji(doc_id):
    """
    Fungsi untuk menghapus 1 dokumen slip berdasarkan ID-nya.
    """
    if not db:
        print("ERROR: Koneksi database tidak ada.")
        return False

    try:
        # Perintahnya sederhana: pilih dokumen berdasarkan ID, lalu .delete()
        db.collection('slip_gaji').document(doc_id).delete()
        return True # Kembalikan True jika berhasil
    
    except Exception as e:
        print(f"ERROR saat menghapus data: {e}")
        return False # Kembalikan False jika gagal
    
def hitung_gaji_bersih(gaji_pokok, hari_izin, pot_izin, hari_sakit, pot_sakit):
    """
    Fungsi baru untuk menghitung gaji bersih bulanan.
    Mengembalikan (gaji_bersih, total_potongan)
    """
    potongan_izin = hari_izin * pot_izin
    potongan_sakit = hari_sakit * pot_sakit
    
    total_potongan = potongan_izin + potongan_sakit
    gaji_bersih = gaji_pokok - total_potongan
    
    # Kita kembalikan 2 nilai ini agar bisa ditampilkan
    return gaji_bersih, total_potongan