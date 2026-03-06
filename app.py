import streamlit as st

st.set_page_config(
    page_title="Fleet Management Tools Hub",
    layout="wide",
)

st.title("Fleet Management Tools Portal")
st.markdown("---")

st.markdown("""
Welcome to the Fleet Management Tools portal.
Silakan kembangkan tools internal di sini dan gunakan navigasi panel sebelah kiri untuk berpindah-pindah.

### Tersedia Saat Ini:
- **Bulk Fill PDF**: Mengisi form PDF secara massal berdasarkan data kendaraan `MASTER.csv`. Ambil Template PDF, baca file Master, dan proses jadi berkas ZIP terpadu.

### Untuk Pengembangan Selanjutnya:
Anda dapat menambahkan fitur-fitur baru dengan menambahkan skrip python baru di dalam map `pages/`.
""")
