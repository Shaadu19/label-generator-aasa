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

# === Config ===
st.set_page_config(page_title="Label Generator", layout="centered")

# === Fonts ===
pdfmetrics.registerFont(TTFont("ArialBold", "Arial-bold.ttf"))
pdfmetrics.registerFont(TTFont("MyriadProSemiCondensed", "Myriad Pro Bold SemiCondensed.ttf"))

# === UI Selection ===
st.title("📦 Label Generator")
app_option = st.radio("Choose a Label App", ["Dispatch Label Generator", "Scrap Label Generator"])

# === DISPATCH LABEL GENERATOR ===
if app_option == "Dispatch Label Generator":
    # Background
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

    set_background("BGD.png")

    # Paths
    INPUT_PDF_DEO = "LABELX.pdf"
    INPUT_PDF_AF = "LABELY.pdf"

    # Coordinates (for 8 labels, left and right)
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

    def generate_pdf(texts, output_file, base_pdf):
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.setFont("ArialBold", 10)

        for i in range(len(text_entries)):
            for j in range(2):
                label_index = i % len(texts)
                x, y = text_entries[i][j]
                c.drawString(x, y, texts[label_index])
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

    # Header
    col1, col2 = st.columns([1, 5])
    with col1:
        try:
            logo = Image.open("logo.png")
            st.image(logo, width=120)
        except:
            st.write("COMPANY LOGO")
    with col2:
        st.markdown("<h1 style='margin-top: 10px;'>Dispatch Label Generator</h1>", unsafe_allow_html=True)

    st.divider()

    # Form
    product_type = st.radio("Select Product Type", ["DEO", "AIR FRESHENER"])
    customer = st.text_input("Customer")
    product = st.text_input("Product")
    litho = st.text_input("Litho Number")
    po = st.text_input("PO Number")

    if st.button("Generate Dispatch PDF"):
        if not all([customer, product, litho, po]):
            st.error("Please fill all fields.")
        else:
            text_map = {
                "LATTAFA PERFUME": customer,
                "YARA DEO 200 ML": product,
                "AA53140ADF0001-01": litho,
                "DEO-09-2024": po,
            }
            texts = [text_map[k] for k in text_map]
            output_name = f"{product.replace(' ', '_')}_{product_type}.pdf"
            base_pdf = INPUT_PDF_DEO if product_type == "DEO" else INPUT_PDF_AF
            path = generate_pdf(texts, output_name, base_pdf)
            st.success("PDF generated successfully!")
            st.markdown(file_download_link(path, "📄 Download PDF"), unsafe_allow_html=True)

# === SCRAP LABEL GENERATOR ===
elif app_option == "Scrap Label Generator":
    st.markdown("## ♻️ Scrap Label Generator")

    TEMPLATE_PATH = "label_template.pdf"
    FONT_SIZE = 58
    X_POS = 448.9028
    Y_POSITIONS = [760.057, 560.014, 350.7377, 150.0474]

    def generate_number_range_labels(start, end):
        output = BytesIO()
        writer = PdfWriter()
        numbers = list(range(start, end + 1))

        for page_start in range(0, len(numbers), 4):
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=A4)
            c.setFont("MyriadProSemiCondensed", FONT_SIZE)

            for idx in range(4):
                if page_start + idx < len(numbers):
                    x = X_POS
                    y = Y_POSITIONS[idx]
                    num = numbers[page_start + idx]
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(x - 5, y - 5, 80, 75, fill=1, stroke=0)
                    c.setFillColorRGB(0, 0, 0)
                    c.drawString(x, y, str(num))

            c.save()
            packet.seek(0)

            base_pdf = PdfReader(TEMPLATE_PATH)
            overlay_pdf = PdfReader(packet)
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        writer.write(output)
        output.seek(0)
        return output

    start_num = st.number_input("Start Number", value=1, step=1)
    end_num = st.number_input("End Number", value=4, step=1)

    if st.button("Generate Scrap PDF"):
        if end_num < start_num:
            st.error("End number must be greater than or equal to start number.")
        else:
            pdf_data = generate_number_range_labels(int(start_num), int(end_num))
            st.success("✅ PDF generated with your number range!")
            st.markdown(f"""
                <style>
                .custom-button {{
                    display: inline-block;
                    padding: 0.75em 1.5em;
                    font-size: 16px;
                    font-weight: 600;
                    color: white;
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 8px;
                    text-align: center;
                    text-decoration: none;
                    margin-top: 1em;
                }}
                .custom-button:hover {{
                    background-color: #45a049;
                }}
                </style>
                <a href="data:application/pdf;base64,{base64.b64encode(pdf_data.read()).decode()}"
                   download="scrap_labels_range.pdf"
                   class="custom-button">
                   📄 Download PDF
                </a>
            """, unsafe_allow_html=True)
