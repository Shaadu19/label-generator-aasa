import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64
import os

# Constants
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"

# Coordinates for each label (2 per row × 4 rows = 8 labels = 32 positions)
text_entries = [
    ((109.33, 781.51), (407.84, 781.51)), ((109.35, 762.71), (405.16, 762.19)),
    ((109.33, 743.10), (405.15, 743.09)), ((109.33, 706.16), (405.15, 706.16)),
    ((109.33, 570.31), (405.15, 570.31)), ((109.34, 553.29), (405.15, 553.29)),
    ((109.32, 533.69), (405.14, 533.69)), ((109.33, 496.80), (405.15, 496.80)),
    ((109.33, 358.48), (405.15, 358.48)), ((109.33, 341.05), (405.15, 341.05)),
    ((109.32, 321.45), (405.13, 321.45)), ((109.33, 284.93), (405.15, 284.93)),
    ((109.33, 150.07), (405.15, 150.07)), ((109.32, 131.64), (405.14, 131.64)),
    ((109.31, 112.04), (405.12, 112.04)), ((109.33, 75.56), (405.15, 75.56)),
]

pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

def generate_pdf(text_map, output_file, base_pdf):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("ArialBold", 10)

    # Prepare replacement texts
    keys = ["LATTAFA PERFUME", "YARA DEO 200 ML", "AA53140ADF0001-01", "DEO-09-2024"]
    texts = [text_map[key] for key in keys]

    for i, ((x1, y1), (x2, y2)) in enumerate(text_entries):
        text_value = texts[i % 4]
        c.drawString(x1, y1, text_value)
        c.drawString(x2, y2, text_value)

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

# Streamlit UI
st.set_page_config(page_title="Label Generator", layout="centered")
st.title("Dispatch Label Generator")

product_type = st.radio("Select Product Type", ["DEO", "AIR FRESHENER"])
customer = st.text_input("Customer")
product = st.text_input("Product")
litho = st.text_input("Litho Number")
po = st.text_input("PO Number")

if st.button("Generate PDF"):
    if not all([customer, product, litho, po]):
        st.error("Please fill all fields.")
    else:
        text_map = {
            "LATTAFA PERFUME": customer,
            "YARA DEO 200 ML": product,
            "AA53140ADF0001-01": litho,
            "DEO-09-2024": po,
        }
        output_name = f"{product.replace(' ', '_')}_{product_type.replace(' ', '_')}.pdf"
        base_pdf = INPUT_PDF_DEO if product_type == "DEO" else INPUT_PDF_AF
        path = generate_pdf(text_map, output_name, base_pdf)
        st.success("PDF generated successfully!")
        st.markdown(file_download_link(path, "📄 Download PDF"), unsafe_allow_html=True)
