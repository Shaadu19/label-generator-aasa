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

# --- Background ---
def set_background(BGD):
    with open(BGD, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64_img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Paths
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"

# Register font
pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

# Coordinates for 8 labels
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
        for j in range(2):  # Left and right
            x, y = text_entries[i][j]
            c.drawString(x, y, texts[j])

    c.save()
    packet.seek(0)

    background = PdfReader(base_pdf)
    overlay = PdfReader(packet)
    writer = PdfWriter()
    page = background.pages[0]
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

# --- Streamlit UI ---
st.set_page_config(page_title="Label Generator", layout="centered")
set_background("BGD.png")

# Logo and Title
col1, col2 = st.columns([1, 5])
with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    except:
        st.write("")
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>Label Generator</h1>", unsafe_allow_html=True)

st.divider()

# --- Step 1: Select Label Type ---
st.markdown("### Step 1: Choose Label Type")
label_type = st.radio("Select Label Type", ["Dispatch Label", "Scrap Label", "Other"])

# --- Step 2: Show form only after label is selected ---
if label_type == "Dispatch Label":
    st.markdown("### Step 2: Enter Dispatch Label Details")
    
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
            st.success("PDF generated successfully!")
            st.markdown(file_download_link(path, "📄 Download PDF"), unsafe_allow_html=True)

elif label_type == "Scrap Label":
    st.info("Scrap Label feature is under development.")

else:
    st.warning("Please select a supported label type.")
