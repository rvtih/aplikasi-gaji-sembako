import streamlit as st
import pandas as pd
# Kita ganti 'hitung_gaji_bersih' dengan 'hitung_gaji_lengkap'
from layanan_gaji import (
    simpan_slip_gaji, 
    ambil_semua_slip, 
    hapus_slip_gaji,
    hitung_gaji_lengkap # Fungsi baru kita yang canggih
)
from firebase_config import db
import datetime

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
        ("Input Gaji Detail", "Laporan & Hapus Data") # Nama menu diubah
    )

# --- Halaman 1: Input Gaji Detail (SUPER BARU) ---
if pilihan_menu == "Input Gaji Detail":
    st.title("Formulir Input Gaji Detail")
    
    with st.form(key="form_gaji_detail", clear_on_submit=False):
        
        # --- Bagian 1: Data Karyawan & Gaji Pokok ---
        st.header("1. Data Pokok")
        col1, col2 = st.columns(2)
        with col1:
            nama_karyawan = st.text_input("Nama Karyawan")
        with col2:
            gaji_pokok = st.number_input("Gaji Pokok Bulanan (Rp)", min_value=0, step=50000, help="Gaji utama sebelum tambahan/potongan.")

        st.divider()
        
        # --- Bagian 2: Tunjangan & Lembur (Pendapatan) ---
        st.header("2. Pendapatan Tambahan")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Tunjangan")
            uang_makan = st.number_input("Total Uang Makan (Rp)", min_value=0, step=10000)
            uang_transport = st.number_input("Total Uang Transport (Rp)", min_value=0, step=10000)
        with col2:
            st.subheader("Lembur")
            jam_lembur = st.number_input("Total Jam Lembur", min_value=0.0, step=0.5)
            upah_lembur_per_jam = st.number_input("Upah Lembur per Jam (Rp)", min_value=0, step=5000)

        st.divider()

        # --- Bagian 3: Potongan (Absensi & Kasbon) ---
        st.header("3. Potongan-potongan")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Potongan Absensi")
            hari_izin = st.number_input("Jumlah Hari Izin", min_value=0, step=1)
            pot_izin = st.number_input("Potongan per Hari Izin (Rp)", min_value=0, step=10000)
            hari_sakit = st.number_input("Jumlah Hari Sakit", min_value=0, step=1)
            pot_sakit = st.number_input("Potongan per Hari Sakit (Rp)", min_value=0, step=10000)
        with col2:
            st.subheader("Potongan Lain")
            kasbon = st.number_input("Total Kasbon / Bon (Rp)", min_value=0, step=10000)
        
        st.divider()
        
        # Tombol submit untuk form
        tombol_simpan = st.form_submit_button(label="Hitung & Simpan Slip Gaji")

    # --- Logika SETELAH tombol form ditekan ---
    if tombol_simpan:
        if not nama_karyawan:
            st.warning("Nama karyawan tidak boleh kosong.")
        elif gaji_pokok <= 0:
            st.warning("Gaji pokok harus diisi.")
        else:
            # 1. Kumpulkan semua data input ke 1 dict
            data_input = {
                'nama': nama_karyawan,
                'gaji_pokok': gaji_pokok,
                'uang_makan': uang_makan,
                'uang_transport': uang_transport,
                'jam_lembur': jam_lembur,
                'upah_lembur_per_jam': upah_lembur_per_jam,
                'hari_izin': hari_izin,
                'pot_izin': pot_izin,
                'hari_sakit': hari_sakit,
                'pot_sakit': pot_sakit,
                'kasbon': kasbon
            }
            
            # 2. Panggil "Otak" (logika) baru kita
            hasil_hitung = hitung_gaji_lengkap(data_input)
            
            # 3. Tampilkan Rincian Perhitungan (INI YANG ANDA MAU)
            st.header(f"Rincian Gaji untuk: {nama_karyawan}")
            st.subheader("✅ RINCIAN PENDAPATAN")
            st.text(f"  + Gaji Pokok          : Rp {hasil_hitung['gaji_pokok']:,.0f}")
            st.text(f"  + Total Tunjangan     : Rp {hasil_hitung['total_tunjangan']:,.0f}")
            st.text(f"  + Total Lembur        : Rp {hasil_hitung['total_lembur']:,.0f}")
            st.subheader(f"Total Pendapatan: Rp {hasil_hitung['total_pendapatan']:,.0f}")
            
            st.subheader("❌ RINCIAN POTONGAN")
            st.text(f"  - Potongan Absensi    : Rp {hasil_hitung['total_pot_absensi']:,.0f}")
            st.text(f"  - Potongan Kasbon     : Rp {hasil_hitung['kasbon']:,.0f}")
            st.subheader(f"Total Potongan: Rp {hasil_hitung['total_potongan']:,.0f}")
            
            st.divider()
            st.success(f"GAJI BERSIH DITERIMA: Rp {hasil_hitung['gaji_bersih']:,.0f}")
            st.divider()

            # 4. Siapkan data untuk disimpan ke Firebase
            # Kita gabungkan data input dan data hasil hitung
            data_untuk_disimpan = {**data_input, **hasil_hitung}
            
            # Tambahkan nama karyawan (lagi) dan tanggal
            data_untuk_disimpan['nama'] = nama_karyawan
            data_untuk_disimpan['periode_gaji'] = datetime.datetime.now().strftime("%B %Y") # Misal: Oktober 2025
            
            # 5. Panggil "Otak" (penyimpanan)
            doc_id = simpan_slip_gaji(data_untuk_disimpan)
            
            if doc_id:
                st.success(f"BERHASIL! Slip gaji {nama_karyawan} disimpan ke Firebase.")
                st.balloons()
            else:
                st.error("Gagal menyimpan data ke Firebase.")

# --- Halaman 2: Laporan & Hapus Data (TIDAK BERUBAH BANYAK) ---
elif pilihan_menu == "Laporan & Hapus Data":
    st.title("Laporan Gaji Karyawan")

    semua_slip = ambil_semua_slip()
    
    if not semua_slip:
        st.info("Belum ada data slip gaji yang tersimpan.")
    else:
        df = pd.DataFrame(semua_slip) 
        
        # --- Dashboard Ringkas ---
        total_gaji_bersih_all = 0
        if 'gaji_bersih' in df.columns:
            total_gaji_bersih_all = df['gaji_bersih'].sum()
            
        st.header("Dashboard Ringkas")
        col1, col2 = st.columns(2)
        col1.metric("Total Gaji Bersih Dibayar (Model Baru)", f"Rp {total_gaji_bersih_all:,.0f}")
        col2.metric("Jumlah Slip Gaji Tercatat", f"{len(df)} slip")
        st.divider()

        # --- Tampilkan Tabel Data ---
        st.header("Semua Data Slip Gaji")
        
        # Coba tampilkan kolom-kolom penting
        kolom_utama = [
            'tanggal_simpan', 'nama', 'gaji_bersih', 'total_pendapatan', 'total_potongan', 'gaji_pokok', 'id'
        ]
        
        kolom_tampil = [col for col in kolom_utama if col in df.columns]
        
        df_tampil = df[kolom_tampil]
        st.dataframe(df_tampil, use_container_width=True)
        
        # Tambahkan Expander untuk melihat data mentah (semua kolom)
        with st.expander("Lihat Data Mentah (Semua Kolom)"):
            st.dataframe(df.fillna(0), use_container_width=True) # fillna(0) agar NaN jadi 0
        
        # --- Fitur Hapus Data (Logika masih sama) ---
        st.divider()
        st.header("Hapus Data Slip Gaji")
        st.warning("PERHATIAN: Data yang sudah dihapus tidak bisa dikembalikan.")

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
                doc_id_terpilih = id_slip_hapus.split("ID: ")[-1]
                
                if hapus_slip_gaji(doc_id_terpilih):
                    st.success(f"BERHASIL menghapus slip dengan ID: {doc_id_terpilih}")
                else:
                    st.error("Gagal menghapus data.")