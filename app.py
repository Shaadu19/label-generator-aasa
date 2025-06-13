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
import tempfile

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

# Coordinates for 8 labels (text positions, already in points)
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

# Signature positions (8 labels, in points)
signature_positions = [
    (160.5532, 188.8262),  # left 1
    (160.5532, 398.273),   # left 2
    (160.5532, 610.0177),  # left 3
    (160.5532, 819.7198),  # left 4
    (458.0851, 188.8262),  # right 1
    (458.0851, 398.273),   # right 2
    (458.0851, 610.0177),  # right 3
    (458.0851, 819.7198),  # right 4
]

def generate_pdf(texts, output_file, base_pdf, signature_img=None):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("ArialBold", 10)

    # Prepare signature
    sig_path = None
    if signature_img:
        sig = Image.open(signature_img).convert("RGB").resize((60, 30))
        sig_path = tempfile.mktemp(suffix=".jpg")
        sig.save(sig_path)

    for i in range(8):
        for j in range(2):  # Left and right columns
            x, y = text_entries[i][j]
            c.drawString(x, y, texts[j])  # Only 2 texts: left/right

    # Draw signature in each of the 8 positions
    if sig_path:
        for x, y in signature_positions:
            c.drawImage(sig_path, x, y, width=60, height=30, mask='auto')

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

# Logo and title
col1, col2 = st.columns([1, 5])
with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    except:
        st.write("")
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>Dispatch Label Generator</h1>", unsafe_allow_html=True)

st.divider()

# Product form
product_type = st.radio("Select Product Type", ["DEO", "AIR FRESHENER"])
customer = st.text_input("Customer")
product = st.text_input("Product")
litho = st.text_input("Litho Number")
po = st.text_input("PO Number")

# Signature input
st.markdown("### Add Signature (Optional)")
sig_method = st.radio("Choose Signature Input", ["Upload", "Draw"])
signature_img = None

if sig_method == "Upload":
    uploaded = st.file_uploader("Upload signature image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded:
        signature_img = uploaded
elif sig_method == "Draw":
    drawn = st.canvas(draw_mode="freedraw", stroke_width=2, stroke_color="#000000", background_color="#ffffff", height=100, width=300, key="canvas")
    if drawn and drawn.image_data is not None:
        img = Image.fromarray((drawn.image_data * 255).astype("uint8")).convert("RGB")
        temp_sig = BytesIO()
        img.save(temp_sig, format="PNG")
        temp_sig.seek(0)
        signature_img = temp_sig

if st.button("Generate PDF"):
    if not all([customer, product, litho, po]):
        st.error("Please fill all fields.")
    else:
        texts = [customer, product]  # Only 2 fields used per label: left/right
        output_name = f"{product.replace(' ', '_')}_{product_type}.pdf"
        base_pdf = INPUT_PDF_DEO if product_type == "DEO" else INPUT_PDF_AF
        path = generate_pdf(texts, output_name, base_pdf, signature_img)
        st.success("PDF generated successfully!")
        st.markdown(file_download_link(path, "📄 Download PDF"), unsafe_allow_html=True)
