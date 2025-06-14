import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64
import os

# --- Paths ---
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"

# Register font
pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

# Coordinates for 8 labels (left & right column)
text_entries = [
    ((109.33, 781.51), (407.84, 781.51)),
    ((109.35, 762.71), (405.16, 762.19)),
    ((109.33, 743.10), (405.15, 743.09)),
    ((109.33, 706.16), (405.15, 706.16)),
    ((109.33, 570.31), (405.15, 570.31)),
    ((109.34, 553.29), (405.15, 553.29)),
    ((109.32, 533.69), (405.14, 533.69)),
    ((109.33, 496.80), (405.15, 496.80)),
]

# --- Functions ---
def generate_pdf(texts, output_file, base_pdf):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("ArialBold", 10)

    for i in range(8):
        for j in range(2):  # Left and right
            x, y = text_entries[i][j]
            c.drawString(x, y, texts[j])
    c.save()
    packet.seek(0)

    bg_pdf = PdfReader(base_pdf)
    overlay = PdfReader(packet)
    writer = PdfWriter()
    page = bg_pdf.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(output_file, "wb") as f:
        writer.write(f)
    return output_file

def file_download_link(filepath, label):
    with open(filepath, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filepath)}">{label}</a>'
    return href

def show_logo():
    st.image("https://chatgpt-image-hosting.s3.amazonaws.com/aasa-logo.png", width=100)

# --- Streamlit App ---
st.set_page_config(page_title="Label Generator", layout="centered")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

# --- PAGE 1: Main Menu ---
if st.session_state.page == "home":
    show_logo()
    st.markdown("<h2 style='text-align:center;'>SELECT THE LABEL</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("DISPATCH LABEL"):
            st.session_state.page = "dispatch"
            st.experimental_rerun()
    with col2:
        if st.button("SCRAP LABEL"):
            st.info("Scrap Label page is under construction.")

# --- PAGE 2: Dispatch Form ---
elif st.session_state.page == "dispatch":
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.page = "home"
            st.session_state.pdf_ready = False
            st.experimental_rerun()
    with col2:
        show_logo()

    st.markdown("<h3>Fill the Form Below</h3>", unsafe_allow_html=True)

    if not st.session_state.pdf_ready:
        product_type = st.radio("Select Product Type", ["DEO", "AIR FRESHENER"])
        customer = st.text_input("Customer")
        product = st.text_input("Product")
        litho = st.text_input("Litho Number")
        po = st.text_input("PO Number")

        if st.button("Generate PDF"):
            if not all([customer, product, litho, po]):
                st.error("Please fill all fields.")
            else:
                texts = [customer, product]
                output_name = f"{product.replace(' ', '_')}_{product_type}.pdf"
                base_pdf = INPUT_PDF_DEO if product_type == "DEO" else INPUT_PDF_AF
                path = generate_pdf(texts, output_name, base_pdf)

                st.session_state.generated_path = path
                st.session_state.pdf_ready = True
                st.experimental_rerun()

    # --- Show Preview and Download ---
    if st.session_state.pdf_ready:
        st.success("✅ PDF generated successfully!")

        with open(st.session_state.generated_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                f'width="100%" height="600px" type="application/pdf"></iframe>',
                unsafe_allow_html=True
            )

        st.markdown(file_download_link(st.session_state.generated_path, "📥 Download PDF"), unsafe_allow_html=True)
