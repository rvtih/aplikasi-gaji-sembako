def hitung_gaji_lengkap(data_input):
    """
    Fungsi super lengkap untuk menghitung gaji bersih.
    Menerima 1 'dict' data input, mengembalikan 1 'dict' hasil perhitungan.
    """
    
    # Ambil semua data dari dict input, beri nilai 0 jika tidak ada
    gaji_pokok = data_input.get('gaji_pokok', 0)
    uang_makan = data_input.get('uang_makan', 0)
    uang_transport = data_input.get('uang_transport', 0)
    
    jam_lembur = data_input.get('jam_lembur', 0)
    upah_lembur_per_jam = data_input.get('upah_lembur_per_jam', 0)
    
    hari_izin = data_input.get('hari_izin', 0)
    pot_izin = data_input.get('pot_izin', 0)
    hari_sakit = data_input.get('hari_sakit', 0)
    pot_sakit = data_input.get('pot_sakit', 0)
    
    kasbon = data_input.get('kasbon', 0)
    
    # --- PROSES PERHITUNGAN ---
    
    # 1. Total Pendapatan
    total_tunjangan = uang_makan + uang_transport
    total_lembur = jam_lembur * upah_lembur_per_jam
    total_pendapatan = gaji_pokok + total_tunjangan + total_lembur
    
    # 2. Total Potongan
    total_pot_absensi = (hari_izin * pot_izin) + (hari_sakit * pot_sakit)
    total_potongan = total_pot_absensi + kasbon
    
    # 3. Gaji Bersih
    gaji_bersih = total_pendapatan - total_potongan
    
    # Kembalikan SEMUA rinciannya dalam bentuk dict
    hasil = {
        'gaji_pokok': gaji_pokok,
        'total_tunjangan': total_tunjangan,
        'total_lembur': total_lembur,
        'total_pendapatan': total_pendapatan,
        'total_pot_absensi': total_pot_absensi,
        'kasbon': kasbon,
        'total_potongan': total_potongan,
        'gaji_bersih': gaji_bersih
    }
    return hasil