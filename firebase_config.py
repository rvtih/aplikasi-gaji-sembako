import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os

NAMA_FILE_KUNCI = "kunci-firebase.json"
db = None  # Mulai dengan db = None

try:
    # Cek apakah aplikasi sedang berjalan di server Streamlit (ONLINE)
    if hasattr(st, 'secrets'):
        print("--- Mode: ONLINE (Streamlit Cloud) ---")
        
        # Cek apakah 'firebase_secrets' sudah di-set di Secrets
        if "firebase_secrets" not in st.secrets:
            raise Exception("Kunci 'firebase_secrets' tidak ditemukan di Streamlit Secrets.")
            
        # Ambil dari Streamlit Secrets
        kunci_dict = dict(st.secrets["firebase_secrets"])
        cred = credentials.Certificate(kunci_dict)
        print("--- Kunci diambil dari Streamlit Secrets ---")
    
    # Jika tidak di server (LOKAL)
    else:
        print("--- Mode: LOKAL (Komputer Sendiri) ---")
        if not os.path.exists(NAMA_FILE_KUNCI):
            raise FileNotFoundError(f"File kunci '{NAMA_FILE_KUNCI}' tidak ditemukan di folder lokal.")
        
        cred = credentials.Certificate(NAMA_FILE_KUNCI)
        print("--- Kunci diambil dari file JSON lokal ---")
    
    # Inisialisasi aplikasi Firebase (hanya jika belum)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("--- Koneksi ke Firebase Berhasil ---")

except firebase_admin.exceptions.AlreadyExistsError:
    # Ini normal, artinya koneksi sudah ada
    db = firestore.client()
    print("--- Koneksi Firebase sudah ada (re-used) ---")

except Exception as e:
    # Tangkap semua error lain (misal: format Secrets salah)
    print(f"ERROR: Gagal koneksi ke Firebase: {e}")
    # Tampilkan error ini di aplikasi Streamlit
    st.error(f"KONEKSI KE DATABASE GAGAL! Detail Error: {e}")