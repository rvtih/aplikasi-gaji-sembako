import streamlit as st
import pandas as pd
# Kita tambahkan fungsi 'hitung_gaji_bersih' yang baru kita buat
from layanan_gaji import (
    hitung_gaji_kotor, # Ini tetap ada untuk data lama
    simpan_slip_gaji, 
    ambil_semua_slip, 
    hapus_slip_gaji,
    hitung_gaji_bersih # Fungsi baru kita
)
from firebase_config import db

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Gaji Toko Sembako", page_icon="🛒", layout="wide")

# Cek koneksi di awal
if not db:
    st.error("KONEKSI KE DATABASE GAGAL! Pastikan 'kunci-firebase.json' benar.")
    st.stop()

# --- Navigasi Sidebar ---
with st.sidebar:
    st.title("🛒 Toko Sembako")
    pilihan_menu = st.radio(
        "Pilih Halaman:",
        ("Input Gaji Bulanan", "Laporan & Hapus Data") # Nama menu diubah
    )

# --- Halaman 1: Input Gaji Bulanan (BARU) ---
if pilihan_menu == "Input Gaji Bulanan":
    st.title("Formulir Input Gaji Bulanan")
    
    with st.form(key="form_gaji_bulanan", clear_on_submit=True):
        st.header("Data Karyawan")
        nama_karyawan = st.text_input("Nama Karyawan")
        gaji_pokok = st.number_input("Gaji Pokok Bulanan (Rp)", min_value=0, step=50000)
        
        st.divider()
        st.header("Data Potongan (Absensi)")
        
        # Buat 2 kolom agar rapi
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Izin (Pribadi)")
            hari_izin = st.number_input("Jumlah Hari Izin", min_value=0, step=1)
            pot_izin = st.number_input("Potongan per Hari Izin (Rp)", min_value=0, step=10000)
            
        with col2:
            st.subheader("Sakit")
            hari_sakit = st.number_input("Jumlah Hari Sakit", min_value=0, step=1)
            pot_sakit = st.number_input("Potongan per Hari Sakit (Rp)", min_value=0, step=10000)
        
        # Tombol submit untuk form
        tombol_simpan = st.form_submit_button(label="Hitung & Simpan Slip Gaji")

    # Logika SETELAH tombol form ditekan
    if tombol_simpan:
        if not nama_karyawan:
            st.warning("Nama karyawan tidak boleh kosong.")
        elif gaji_pokok <= 0:
            st.warning("Gaji pokok harus diisi.")
        else:
            # Panggil "Otak" (logika) baru kita
            gaji_bersih, total_potongan = hitung_gaji_bersih(
                gaji_pokok, hari_izin, pot_izin, hari_sakit, pot_sakit
            )
            
            st.header("Hasil Perhitungan:")
            st.info(f"Total Potongan (Izin + Sakit): Rp {total_potongan:,.0f}")
            st.success(f"GAJI BERSIH DITERIMA: Rp {gaji_bersih:,.0f}")
            
            data_untuk_disimpan = {
                'nama': nama_karyawan,
                'gaji_pokok': gaji_pokok,
                'hari_izin': hari_izin,
                'potongan_per_izin': pot_izin,
                'hari_sakit': hari_sakit,
                'potongan_per_sakit': pot_sakit,
                'total_potongan': total_potongan,
                'gaji_bersih': gaji_bersih
                # Kita tidak simpan 'gaji_kotor' lagi untuk model baru
            }
            
            # Panggil "Otak" (penyimpanan)
            doc_id = simpan_slip_gaji(data_untuk_disimpan)
            
            if doc_id:
                st.success(f"BERHASIL! Slip gaji {nama_karyawan} disimpan.")
                st.balloons()
            else:
                st.error("Gagal menyimpan data ke Firebase.")

# --- Halaman 2: Laporan & Hapus Data (UPDATE) ---
elif pilihan_menu == "Laporan & Hapus Data":
    st.title("Laporan Gaji Karyawan")

    semua_slip = ambil_semua_slip()
    
    if not semua_slip:
        st.info("Belum ada data slip gaji yang tersimpan.")
    else:
        df = pd.DataFrame(semua_slip) # Ubah data jadi DataFrame Pandas
        
        # --- Dashboard Ringkas (UPDATE) ---
        # Kita cek apakah kolom 'gaji_bersih' ada (data model baru)
        # Jika tidak, kita pakai 'gaji_kotor' (data model lama)
        
        total_gaji_bersih = 0
        if 'gaji_bersih' in df.columns:
            total_gaji_bersih = df['gaji_bersih'].sum()
            
        total_gaji_kotor = 0
        if 'gaji_kotor' in df.columns:
            total_gaji_kotor = df['gaji_kotor'].sum()

        jumlah_slip = len(df)
        
        st.header("Dashboard Ringkas")
        col1, col2 = st.columns(2)
        col1.metric("Total Gaji Dibayar (Model Baru)", f"Rp {total_gaji_bersih:,.0f}")
        col2.metric("Total Gaji Dibayar (Model Lama)", f"Rp {total_gaji_kotor:,.0f}")
        st.divider()

        # --- Tampilkan Tabel Data (UPDATE) ---
        st.header("Semua Data Slip Gaji")
        
        # Tentukan kolom yang idealnya ingin kita tampilkan
        # Ini akan otomatis menampilkan 'NaN' jika datanya tidak ada
        kolom_ideal = [
            'tanggal_simpan', 'nama', 
            'gaji_pokok', 'total_potongan', 'gaji_bersih', # Model Baru
            'gaji_kotor', 'jam_kerja', 'gaji_per_jam',     # Model Lama
            'id'
        ]
        
        # Filter kolom yang benar-benar ada di dataframe
        kolom_tampil = [col for col in kolom_ideal if col in df.columns]
        
        df_tampil = df[kolom_tampil]
        st.dataframe(df_tampil, use_container_width=True)
        st.caption(f"Total data: {len(semua_slip)}")
        
        # --- Fitur Hapus Data (UPDATE) ---
        st.divider()
        st.header("Hapus Data Slip Gaji")
        st.warning("PERHATIAN: Data yang sudah dihapus tidak bisa dikembalikan.")

        # Logika pintar untuk menampilkan label (bisa baca data lama & baru)
        pilihan_slip = []
        for slip in semua_slip:
            nama = slip.get('nama', 'N/A')
            doc_id = slip.get('id', 'ID-ERROR')
            
            # Cek apakah ini slip model baru atau lama
            if 'gaji_bersih' in slip:
                label_gaji = f"Gaji Bersih: Rp {slip.get('gaji_bersih', 0):,.0f}"
            else:
                label_gaji = f"Gaji Kotor: Rp {slip.get('gaji_kotor', 0):,.0f}"
            
            label = f"{nama} ({label_gaji}) - ID: {doc_id}"
            pilihan_slip.append(label)

        id_slip_hapus = st.selectbox("Pilih slip untuk dihapus:", pilihan_slip)

        if st.button("Hapus Slip Gaji Sekarang", type="primary"):
            if id_slip_hapus:
                # Ekstrak 'id' asli dari teks pilihan
                doc_id_terpilih = id_slip_hapus.split("ID: ")[-1]
                
                if hapus_slip_gaji(doc_id_terpilih):
                    st.success(f"BERHASIL menghapus slip dengan ID: {doc_id_terpilih}")
                    st.info("Data akan refresh otomatis setelah beberapa saat.")
                else:
                    st.error("Gagal menghapus data.")