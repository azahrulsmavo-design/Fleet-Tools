import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import zipfile

# Set up the page config first before any other st calls
st.set_page_config(
    page_title="Bulk Fill PDF - Fleet Tools",
    layout="wide",
)

# Apply custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #fefefe;
    }
    .stButton>button {
        background-color: #ffb3b3;
        color: #2b2b2b;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff9999;
        color: white;
    }
    .banner {
        background: linear-gradient(135deg, #e6f0f9 0%, #ffb3b3 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        color: #2b2b2b;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Function for PDF Stamping ---
def stamp_pdf(template_path, data):
    """
    Stamps data onto the existing PDF template using PyMuPDF.
    It preserves the original background, images, and layout.
    """
    # doc = fitz.open(template_path) -> Now accepts a stream directly
    doc = fitz.open(stream=template_path.read(), filetype="pdf")
    page = doc[0]
    
    # Coordinates (Approximate based on earlier extraction)
    x_offset = 200
    
    # Loads Calibri font
    fontname = "calibri"
    fontfile = "C:\\Windows\\Fonts\\calibri.ttf"
    try:
        page.insert_font(fontname=fontname, fontfile=fontfile)
    except:
        fontname = "helv" # fallback just in case
        
    fontsize = 11
    color = (0, 0, 0)  # Black text
    
    # Text positions calculated to match the template blank lines perfectly
    text_insertions = [
        (data['Nopol'], fitz.Point(200, 356)),        # Y: 356
        (data['Merk_Tipe'], fitz.Point(200, 369)),    # Y: 369
        (data['Tahun'], fitz.Point(200, 382)),        # Y: 382
        (data['Warna'], fitz.Point(200, 395)),        # Y: 395
        (data['No_Rangka'], fitz.Point(200, 408)),    # Y: 408
        (data['No_Mesin'], fitz.Point(200, 421)),     # Y: 421
        (data['Tanggal_Location'], fitz.Point(46.4, 510)) # Place it above "Jakarta, Compliance"
    ]
    
    for text_string, point in text_insertions:
        if text_string:
            # We must pass the fontfile keyword specifically otherwise fitz may crash when drawing custom fonts
            page.insert_text(
                point, 
                str(text_string), 
                fontsize=fontsize, 
                fontname=fontname, 
                fontfile=fontfile if fontname == 'calibri' else None,
                color=color
            )
            
    # Save to BytesIO
    pdf_bytes = io.BytesIO()
    doc.save(pdf_bytes)
    doc.close()
    pdf_bytes.seek(0)
    return pdf_bytes

@st.cache_data
def load_data(filepath="MASTER.csv"):
    try:
        df = pd.read_csv(filepath, sep=",", dtype=str)
        return df
    except Exception as e:
        return None

# Page UI
st.markdown('<div class="banner"><h2>Bulk Fill PDF Documents</h2><p>Generate Surat Pernyataan secara massal dari Master Data.</p></div>', unsafe_allow_html=True)

# File Uploaders
col1, col2 = st.columns(2)
with col1:
    csv_file = st.file_uploader("Upload File Master Kendaraan (CSV)", type=['csv'])
with col2:
    pdf_template = st.file_uploader("Upload Template Surat (PDF)", type=['pdf'])

if csv_file is None or pdf_template is None:
    st.info("Silakan unggah file `MASTER.csv` dan `Template.pdf` untuk melanjutkan.")
    st.stop()

# Load Data from uploaded CSV
df_master = load_data(csv_file)
if df_master is None:
    st.error("Gagal membaca file CSV. Pastikan format pemisahnya koma.")
    st.stop()
    
st.success(f"Berhasil memuat Master Data dengan {len(df_master)} baris data.")

with st.form("bulk_fill_form"):
    st.subheader("Parameter Generate")
    
    tanggal_input = st.text_input("Tanggal Dokumen (Tampil di bawah PDF)", value="Jakarta, 06 Maret 2026", help="Akan ditulis tepat di bagian bawah sebelum ttd.")
    
    nopol_input = st.text_area("Daftar Nomor Polisi (Pisahkan dengan koma)", placeholder="B 9987 TXV, DD 8952 MO, B 9081 TXV", height=100)
    
    submitted = st.form_submit_button("Generate PDFs")
    
if submitted:
    if not nopol_input.strip():
        st.warning("Mohon masukkan minimal satu Nopol.")
    else:
        nopols = [n.strip() for n in nopol_input.split(',') if n.strip()]
        
        generated_files = {} 
        not_found = []
        success_count = 0
        
        with st.spinner('Generating PDFs... Please wait.'):
            for nopol in nopols:
                match = df_master[df_master['NOPOL'].str.strip().str.upper() == nopol.upper()]
                
                if not match.empty:
                    row = match.iloc[0]
                    merk = row.get('MERK', '')
                    tipe = row.get('TYPE', '')
                    merk_tipe = f"{merk} / {tipe}" if merk and tipe else str(merk) + str(tipe)
                    
                    data_to_stamp = {
                        'Nopol': row.get('NOPOL', ''),
                        'Merk_Tipe': merk_tipe,
                        'Tahun': row.get('TAHUN PEMBUATAN', ''),
                        'Warna': row.get('WARNA KABIN', ''),  # Asumsikan warna kabin
                        'No_Rangka': row.get('NO RANGKA', ''),
                        'No_Mesin': row.get('NO MESIN', ''),
                        'Tanggal_Location': tanggal_input
                    }
                    
                    try:
                        # Reset template cursor position to beginning before each stamp
                        pdf_template.seek(0)
                        pdf_bytes = stamp_pdf(pdf_template, data_to_stamp)
                        
                        safe_nopol = str(row.get('NOPOL', '')).replace(" ", "_").replace("/", "-")
                        file_name = f"Surat_Pernyataan_{safe_nopol}.pdf"
                        
                        generated_files[file_name] = pdf_bytes.getvalue()
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error generating PDF for {nopol}: {str(e)}")
                else:
                    not_found.append(nopol)
        
        if not_found:
            st.warning(f"Nopol berikut tidak ditemukan di data Master: {', '.join(not_found)}")
        
        if success_count > 0:
            st.success(f"Berhasil membuat {success_count} PDF!")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for filename, file_bytes in generated_files.items():
                    zip_file.writestr(filename, file_bytes)
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="Download All Output as ZIP",
                data=zip_buffer,
                file_name="Bulk_Filled_Fleet_PDFs.zip",
                mime="application/zip",
            )
