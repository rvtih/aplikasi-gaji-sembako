import streamlit as st
import pandas as pd
# Kita tambahkan fungsi 'hapus_slip_gaji' yang baru kita buat
from layanan_gaji import (
    hitung_gaji_kotor, 
    simpan_slip_gaji, 
    ambil_semua_slip, 
    hapus_slip_gaji
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
        ("Input Slip Gaji", "Laporan & Hapus Data")
    )

# --- Konten Halaman: Sesuai Pilihan Menu ---

if pilihan_menu == "Input Slip Gaji":
    st.title("Formulir Input Slip Gaji")
    
    # Kita pakai st.form agar lebih rapi
    with st.form(key="form_gaji", clear_on_submit=True):
        nama_karyawan = st.text_input("Nama Karyawan")
        
        # Buat 2 kolom agar input angka berdampingan
        col1, col2 = st.columns(2)
        with col1:
            jam_kerja = st.number_input("Total Jam Kerja", min_value=0.0, step=0.5)
        with col2:
            gaji_per_jam = st.number_input("Gaji per Jam (Rp)", min_value=0, step=1000)
        
        # Tombol submit untuk form
        tombol_simpan = st.form_submit_button(label="Simpan Slip Gaji")

    # Logika SETELAH tombol form ditekan
    if tombol_simpan:
        if not nama_karyawan:
            st.warning("Nama karyawan tidak boleh kosong.")
        elif jam_kerja <= 0 or gaji_per_jam <= 0:
            st.warning("Jam kerja dan Gaji per Jam harus lebih dari 0.")
        else:
            # Panggil "Otak" (logika)
            gaji_kotor = hitung_gaji_kotor(jam_kerja, gaji_per_jam)
            
            data_untuk_disimpan = {
                'nama': nama_karyawan,
                'jam_kerja': jam_kerja,
                'gaji_per_jam': gaji_per_jam,
                'gaji_kotor': gaji_kotor
            }
            
            # Panggil "Otak" (penyimpanan)
            doc_id = simpan_slip_gaji(data_untuk_disimpan)
            
            if doc_id:
                st.success(f"BERHASIL! Gaji {nama_karyawan} (Rp {gaji_kotor}) disimpan.")
                st.balloons()
            else:
                st.error("Gagal menyimpan data ke Firebase.")

elif pilihan_menu == "Laporan & Hapus Data":
    st.title("Laporan Gaji Karyawan")

    # Ambil semua data slip
    semua_slip = ambil_semua_slip()
    
    if not semua_slip:
        st.info("Belum ada data slip gaji yang tersimpan.")
    else:
        # --- Fitur Baru: Dashboard Sederhana ---
        df = pd.DataFrame(semua_slip) # Ubah data jadi DataFrame Pandas
        total_gaji_dibayar = df['gaji_kotor'].sum()
        jumlah_slip = len(df)
        rata_rata_gaji = df['gaji_kotor'].mean()

        st.header("Dashboard Ringkas")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gaji Dibayar", f"Rp {total_gaji_dibayar:,.0f}")
        col2.metric("Jumlah Slip Gaji", f"{jumlah_slip} slip")
        col3.metric("Rata-rata Gaji", f"Rp {rata_rata_gaji:,.0f}")
        st.divider()

        # --- Tampilkan Tabel Data ---
        st.header("Semua Data Slip Gaji")
        
        # Kolom yg mau ditampilkan & urutannya
        kolom_tampil = [
            'tanggal_simpan', 
            'nama', 
            'gaji_kotor', 
            'jam_kerja', 
            'gaji_per_jam',
            'id' # Kita butuh 'id' untuk hapus data
        ]
        df_tampil = df[kolom_tampil]
        
        # Tampilkan tabel
        st.dataframe(df_tampil, use_container_width=True)
        st.caption(f"Total data: {len(semua_slip)}")
        
        # --- Fitur Baru: Hapus Data ---
        st.divider()
        st.header("Hapus Data Slip Gaji")
        st.warning("PERHATIAN: Data yang sudah dihapus tidak bisa dikembalikan.")

        # Buat dropdown (selectbox) untuk memilih slip yang mau dihapus
        # Kita buat format yg gampang dibaca: "Nama (ID: ...)"
        pilihan_slip = [f"{slip['nama']} (Rp {slip['gaji_kotor']}) - ID: {slip['id']}" for slip in semua_slip]
        id_slip_hapus = st.selectbox("Pilih slip untuk dihapus:", pilihan_slip)

        if st.button("Hapus Slip Gaji Sekarang", type="primary"):
            # Kita perlu ekstrak 'id' asli dari teks pilihan
            doc_id_terpilih = id_slip_hapus.split("ID: ")[-1]
            
            # Panggil "Otak" (logika hapus)
            if hapus_slip_gaji(doc_id_terpilih):
                st.success(f"BERHASIL menghapus slip dengan ID: {doc_id_terpilih}")
                st.info("Data akan refresh otomatis, silakan cek tabel di atas.")
                # st.experimental_rerun() # Bisa dipakai jika perlu refresh paksa
            else:
                st.error("Gagal menghapus data.")