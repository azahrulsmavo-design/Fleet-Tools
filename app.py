import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import zipfile

# Set up the page config
st.set_page_config(
    page_title="Fleet Management Tools",
    layout="wide",
)

# Apply custom CSS for styling tweaks
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
    /* Add a nice banner/header style */
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
    # Open the existing PDF
    doc = fitz.open(template_path)
    page = doc[0]  # Assuming template is 1 page
    
    # Coordinates (Approximate based on earlier extraction)
    # X, Y coordinates need to align with the colons ":"
    x_offset = 200 # Roughly where the colons start
    
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
    # The previous Y values were ~10pts too high, as Y=347 printed above "Nomor Polisi"
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
            page.insert_text(
                point, 
                str(text_string), 
                fontsize=fontsize, 
                fontname=fontname, 
                color=color
            )
            
    # Save to BytesIO
    pdf_bytes = io.BytesIO()
    doc.save(pdf_bytes)
    doc.close()
    pdf_bytes.seek(0)
    return pdf_bytes


# --- Sidebar Navigation ---
st.sidebar.title("Fleet Tools")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Bulk Fill PDF"])

# Load MASTER.csv cache
@st.cache_data
def load_data(filepath="MASTER.csv"):
    try:
        # Menyesuaikan delimiter koma dan engine
        df = pd.read_csv(filepath, sep=",", dtype=str)
        return df
    except Exception as e:
        return None

if page == "Bulk Fill PDF":
    st.markdown('<div class="banner"><h2>Bulk Fill PDF Documents</h2><p>Generate Surat Pernyataan secara massal dari Master Data.</p></div>', unsafe_allow_html=True)
    
    df_master = load_data()
    if df_master is None:
        st.error("Gagal membaca file `MASTER.csv`. Pastikan file berada di folder yang sama.")
        st.stop()
        
    st.info(f"Loaded Master Data with {len(df_master)} records.")
    
    with st.form("bulk_fill_form"):
        st.subheader("Parameter Generate")
        
        # Tanggal Document (e.g. Jakarta, 06 Maret 2026)
        tanggal_input = st.text_input("Tanggal Dokumen (Tampil di bawah PDF)", value="Jakarta, 06 Maret 2026", help="Akan ditulis tepat di bagian bawah sebelum ttd.")
        
        # Nopol input
        nopol_input = st.text_area("Daftar Nomor Polisi (Pisahkan dengan koma)", placeholder="B 9987 TXV, DD 8952 MO, B 9081 TXV", height=100)
        
        # Submit Button
        submitted = st.form_submit_button("Generate PDFs")
        
    if submitted:
        if not nopol_input.strip():
            st.warning("Mohon masukkan minimal satu Nopol.")
        else:
            # Parse Nopols
            nopols = [n.strip() for n in nopol_input.split(',') if n.strip()]
            
            generated_files = {} # dict of filename: bytes
            not_found = []
            success_count = 0
            
            with st.spinner('Generating PDFs... Please wait.'):
                for nopol in nopols:
                    # Find matching row in MASTER.csv (Column 'NOPOL')
                    # Hapus spasi ekstra agar pencocokan akurat
                    match = df_master[df_master['NOPOL'].str.strip().str.upper() == nopol.upper()]
                    
                    if not match.empty:
                        row = match.iloc[0]
                        # Extract requested data
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
                        
                        # Apply to PDF
                        try:
                            pdf_bytes = stamp_pdf("Template.pdf", data_to_stamp)
                            
                            # Sanitize filename (remove spaces, slashes)
                            safe_nopol = str(row.get('NOPOL', '')).replace(" ", "_").replace("/", "-")
                            file_name = f"Surat_Pernyataan_{safe_nopol}.pdf"
                            
                            generated_files[file_name] = pdf_bytes.getvalue()
                            success_count += 1
                        except Exception as e:
                            st.error(f"Error generating PDF for {nopol}: {str(e)}")
                    else:
                        not_found.append(nopol)
            
            # Show results
            if not_found:
                st.warning(f"Nopol berikut tidak ditemukan di data Master: {', '.join(not_found)}")
            
            if success_count > 0:
                st.success(f"Berhasil membuat {success_count} PDF!")
                
                # Create a ZIP file in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for filename, file_bytes in generated_files.items():
                        zip_file.writestr(filename, file_bytes)
                
                zip_buffer.seek(0)
                
                # Download Button for the ZIP
                st.download_button(
                    label="Download All Output as ZIP",
                    data=zip_buffer,
                    file_name="Bulk_Filled_Fleet_PDFs.zip",
                    mime="application/zip",
                )
