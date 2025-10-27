import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# --- LOGIKA BARU UNTUK KONEKSI ---

# Tentukan nama file kunci LOKAL
NAMA_FILE_KUNCI = "kunci-firebase.json"

# Cek apakah aplikasi sedang berjalan di server Streamlit
# (st.secrets akan ada jika di server, dan tidak ada jika di lokal)
if hasattr(st, 'secrets'):
    print("--- Mode: ONLINE (Streamlit Cloud) ---")
    # 1. AMBIL DARI STREAMLIT SECRETS
    # Kita akan buat 'secret' bernama 'firebase_secrets'
    try:
        # st.secrets["firebase_secrets"] akan berisi SEMUA isi file JSON
        kunci_dict = dict(st.secrets["firebase_secrets"])
        cred = credentials.Certificate(kunci_dict)
        print("--- Kunci diambil dari Streamlit Secrets ---")
    except Exception as e:
        print(f"ERROR: Gagal mengambil 'firebase_secrets': {e}")
        st.error(f"Gagal mengambil 'firebase_secrets': {e}")
        db = None
else:
    print("--- Mode: LOKAL (Komputer Sendiri) ---")
    # 2. AMBIL DARI FILE JSON LOKAL
    if not os.path.exists(NAMA_FILE_KUNCI):
        print(f"ERROR: File kunci '{NAMA_FILE_KUNCI}' tidak ditemukan.")
        db = None
    else:
        cred = credentials.Certificate(NAMA_FILE_KUNCI)
        print("--- Kunci diambil dari file JSON lokal ---")

# --- INISIALISASI DATABASE ---
# (Hanya jalankan jika 'cred' berhasil dibuat dan belum ada koneksi)
try:
    if 'db' not in locals(): # Cek apakah 'db' sudah diset (misal jadi None)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("--- Koneksi ke Firebase Berhasil ---")
except firebase_admin.exceptions.AlreadyExistsError:
    # Ini untuk mencegah error jika ter-inisialisasi dua kali
    db = firestore.client()
    print("--- Koneksi Firebase sudah ada (re-used) ---")
except Exception as e:
    print(f"ERROR: Gagal koneksi ke Firebase: {e}")
    st.error(f"Gagal koneksi ke Firebase: {e}")
    db = None