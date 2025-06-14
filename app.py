import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from PIL import Image
import base64
import os

# --- Setup ---
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"

pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

# --- PDF Text Coordinates ---
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
        for j in range(2):
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
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filepath)}">{label}</a>'

def show_logo():
    st.image("https://chatgpt-image-hosting.s3.amazonaws.com/aasa-logo.png", width=120)

# --- Page Config ---
st.set_page_config(page_title="Label Generator", layout="centered")
st.markdown("<style>body { background-color: #f8f8f8; }</style>", unsafe_allow_html=True)

# --- Page State ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- PAGE 1: Main Menu ---
if st.session_state.page == "home":
    show_logo()
    st.markdown("<h2 style='text-align:center;'>SELECT LABEL TYPE</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("DISPATCH LABEL"):
            st.session_state.page = "dispatch"
    with col2:
        if st.button("SCRAP LABEL"):
            st.info("Scrap Label page is under construction.")

# --- PAGE 2: Dispatch Form ---
elif st.session_state.page == "dispatch":
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.page = "home"
    with col2:
        show_logo()

    st.markdown("<h3>Fill the Form Below</h3>", unsafe_allow_html=True)
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

            st.success("✅ PDF generated successfully!")

            # Embedded Preview
            with open(path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

            # Download Buttons
            st.markdown(file_download_link(path, "📥 Download PDF"), unsafe_allow_html=True)
