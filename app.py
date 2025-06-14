import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64
import os

# --- Setup ---
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"

pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

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

def show_pdf_preview(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""
    <iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>
    <br>
    <a href="data:application/octet-stream;base64,{base64_pdf}" download="{os.path.basename(file_path)}">
    📥 Download PDF
    </a>
    """
    st.components.v1.html(pdf_display, height=550)

# --- Streamlit App ---
st.set_page_config(page_title="Label Generator", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "home"

# --- PAGE 1 ---
if st.session_state.page == "home":
    st.image("logo.png", width=150)  # Change to your logo path
    st.markdown("<h2 style='text-align:center;'>Select Label Type</h2>", unsafe_allow_html=True)
    if st.button("Dispatch Label"):
        st.session_state.page = "dispatch"
        st.experimental_rerun()

# --- PAGE 2 ---
elif st.session_state.page == "dispatch":
    # Back button
    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.experimental_rerun()

    st.image("logo.png", width=150)  # Logo again
    st.markdown("### Fill the Form Below")

    # Inputs
    product_type = st.radio("Select Product Type", ["DEO", "AIR FRESHENER"])
    customer = st.text_input("Customer")
    product = st.text_input("Product")
    litho = st.text_input("Litho Number")
    po = st.text_input("PO Number")

    # PDF Gen
    if st.button("Generate PDF"):
        if not all([customer, product, litho, po]):
            st.error("Please fill all fields.")
        else:
            texts = [customer, product]
            base_pdf = INPUT_PDF_DEO if product_type == "DEO" else INPUT_PDF_AF
            output_name = f"{product.replace(' ', '_')}_{product_type}.pdf"
            path = generate_pdf(texts, output_name, base_pdf)
            st.success("PDF generated successfully!")
            show_pdf_preview(path)  # Embedded preview + download
