import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64
import os
from PIL import Image

# --- ACCESS KEYS ---
VALID_KEYS = {
    "shadT9fX3LpZ",
    "XshadL2mP9vQ",
    "K7shadR8t1zW",
    "Lp2Xshad7mQc",
    "D9TzshadX1wE"
}

# --- PAGE CONFIG ---
st.set_page_config(page_title="Login | Label Generator", layout="centered", initial_sidebar_state="collapsed")

# --- SET BACKGROUND ---
def set_background(image_file):
    with open(image_file, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .login-box {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 15px;
            max-width: 400px;
            margin: auto;
            margin-top: 10%;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("BGD.png")

# --- LOGIN SCREEN ---
def login_ui():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("logo.png", width=200)
    st.markdown("### 🔐 Login to Continue")

    key_input = st.text_input("Enter Access Key", type="password", placeholder="Enter your access code")

    whatsapp_number = "971565690659"
    help_url = f"https://wa.me/{whatsapp_number}?text=Hello,+I+need+help+accessing+the+app"
    st.markdown(f"<small>Need help? <a href='{help_url}' target='_blank'>Contact via WhatsApp</a></small>", unsafe_allow_html=True)

    access_granted = False

    if key_input:
        if key_input in VALID_KEYS:
            st.success("✅ Access granted!")
            access_granted = True
        else:
            st.error("❌ Invalid access key.")
    st.markdown('</div>', unsafe_allow_html=True)
    return access_granted

if not login_ui():
    st.stop()

# --- MAIN APP STARTS AFTER LOGIN ---
# --- Configuration ---
FONT_PATH = "Arial-bold.ttf"
INPUT_PDF_DEO = "LABELX.pdf"
INPUT_PDF_AF = "LABELY.pdf"
pdfmetrics.registerFont(TTFont("ArialBold", FONT_PATH))

# --- Text Layout ---
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

# --- PDF Generator ---
def generate_pdf(texts, output_file, base_pdf):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("ArialBold", 10)

    for i in range(len(text_entries)):
        for j in range(2):
            index = (i * 2 + j) % len(texts)
            label = texts[index % len(texts)]
            x, y = text_entries[i][j]
            c.drawString(x, y, label)
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

# --- Download Link ---
def file_download_link(filepath, label):
    with open(filepath, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filepath)}">{label}</a>'
    return href

# --- UI ---
st.title("📦 Dispatch Label Generator")

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
        texts = [
            text_map["LATTAFA PERFUME"],
            text_map["YARA DEO 200 ML"],
            text_map["AA53140ADF0001-01"],
            text_map["DEO-09-2024"]
        ]
        output_name = f"{product.replace(' ', '_')}_{product_type}.pdf"
        base_pdf = INPUT_PDF_DEO if product_type == "DEO" else INPUT_PDF_AF
        path = generate_pdf(texts, output_name, base_pdf)
        st.success("PDF generated successfully!")
        st.markdown(file_download_link(path, "📄 Download PDF"), unsafe_allow_html=True)
