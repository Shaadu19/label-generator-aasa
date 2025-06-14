import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64
import os

# === CONFIG ===
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"
BG_IMAGE = "BGD.PNG"

# === REGISTER FONT ===
pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

# === COORDINATES FOR LABELS ===
text_entries = [
    ((109.33, 781.51), (407.84, 781.51)),
    ((109.35, 762.71), (405.16, 762.19)),
    ((109.33, 743.10), (405.15, 743.09)),
    ((109.33, 706.16), (405.15, 706.16)),
    ((109.33, 570.31), (405.15, 570.31)),
    ((109.34, 553.29), (405.15, 553.29)),
    ((109.32, 533.69), (405.14, 533.69)),
    ((109.33, 496.80), (405.15, 496.80)),

        data = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# === GENERATE PDF FUNCTION ===
def generate_pdf(texts, output_file, base_pdf):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("ArialBold", 10)

    for i in range(8):
        for j in range(2):  # Left & right columns
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

# === EMBED PDF PREVIEW ===
def show_pdf_preview(pdf_file):
    with open(pdf_file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>
        <br><a href="data:application/pdf;base64,{base64_pdf}" download="{os.path.basename(pdf_file)}" style="font-size:16px;">📥 Download PDF</a>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

# === PAGE CONFIG ===
st.set_page_config(page_title="Label Generator", layout="centered")

# === SESSION STATE ===
if "page" not in st.session_state:
    st.session_state.page = "home"
if "pdf_generated" not in st.session_state:
    st.session_state.pdf_generated = False
if "generated_pdf_path" not in st.session_state:
    st.session_state.generated_pdf_path = None

# === PAGE 1: MAIN MENU ===
if st.session_state.page == "home":
    st.markdown("<h2 style='text-align:center;'>SELECT LABEL TYPE</h2>", unsafe_allow_html=True)
    col1, _ = st.columns([1, 1])
    with col1:
        if st.button("DISPATCH LABEL"):
            st.session_state.page = "dispatch"
            st.experimental_rerun()

# === PAGE 2: DISPATCH LABEL FORM ===
elif st.session_state.page == "dispatch":

    # Back button
    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.session_state.pdf_generated = False
        st.experimental_rerun()

    # Logo + Title
    st.image("logo.png", width=120)  # Replace with your logo file if needed
    st.markdown("<h2>Dispatch Label</h2>", unsafe_allow_html=True)
    st.divider()

    if not st.session_state.pdf_generated:
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
                st.session_state.pdf_generated = True
                st.session_state.generated_pdf_path = path
                st.experimental_rerun()

    else:
        st.success("✅ PDF Generated Successfully!")
        show_pdf_preview(st.session_state.generated_pdf_path)
        st.markdown(
            f'<a href="{st.session_state.generated_pdf_path}" download="{os.path.basename(st.session_state.generated_pdf_path)}">📥 Download PDF</a>',
            unsafe_allow_html=True,
        )
