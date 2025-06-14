from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

app = Flask(__name__)

pdfmetrics.registerFont(TTFont("ArialBold", "Arial-Bold.ttf"))

TEXT_COORDS = [
    ("LATTAFA PERFUME", (109.33, 781.51)), ("YARA DEO 200 ML", (109.35, 762.71)),
    ("AA53140ADF0001-01", (109.33, 743.10)), ("DEO-09-2024", (109.33, 706.16)),
    ("LATTAFA PERFUME", (407.84, 781.51)), ("YARA DEO 200 ML", (405.16, 762.19)),
    ("AA53140ADF0001-01", (405.15, 743.09)), ("DEO-09-2024", (405.15, 706.16)),
    ("LATTAFA PERFUME", (109.33, 570.31)), ("YARA DEO 200 ML", (109.34, 553.29)),
    ("AA53140ADF0001-01", (109.32, 533.69)), ("DEO-09-2024", (109.33, 496.80)),
    ("LATTAFA PERFUME", (405.15, 570.31)), ("YARA DEO 200 ML", (405.15, 553.29)),
    ("AA53140ADF0001-01", (405.14, 533.69)), ("DEO-09-2024", (405.15, 496.80)),
    ("LATTAFA PERFUME", (109.33, 358.48)), ("YARA DEO 200 ML", (109.33, 341.05)),
    ("AA53140ADF0001-01", (109.32, 321.45)), ("DEO-09-2024", (109.33, 284.93)),
    ("LATTAFA PERFUME", (405.15, 358.48)), ("YARA DEO 200 ML", (405.15, 341.05)),
    ("AA53140ADF0001-01", (405.13, 321.45)), ("DEO-09-2024", (405.15, 284.93)),
    ("LATTAFA PERFUME", (109.33, 150.07)), ("YARA DEO 200 ML", (109.32, 131.64)),
    ("AA53140ADF0001-01", (109.31, 112.04)), ("DEO-09-2024", (109.33, 75.56)),
    ("LATTAFA PERFUME", (405.15, 150.07)), ("YARA DEO 200 ML", (405.14, 131.64)),
    ("AA53140ADF0001-01", (405.12, 112.04)), ("DEO-09-2024", (405.15, 75.56)),
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text1 = request.form["text1"]
        text2 = request.form["text2"]
        text3 = request.form["text3"]
        text4 = request.form["text4"]

        mapping = {
            "LATTAFA PERFUME": text1,
            "YARA DEO 200 ML": text2,
            "AA53140ADF0001-01": text3,
            "DEO-09-2024": text4,
        }

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("ArialBold", 10)

        for original_text, (x, y) in TEXT_COORDS:
            c.drawString(x, y, mapping[original_text])
        c.save()
        buffer.seek(0)

        background = PdfReader("LABELX.pdf")
        overlay = PdfReader(buffer)
        output = PdfWriter()
        page = background.pages[0]
        page.merge_page(overlay.pages[0])
        output.add_page(page)

        final_pdf = BytesIO()
        output.write(final_pdf)
        final_pdf.seek(0)

        filename = text2.strip().replace(" ", "_") + ".pdf"
        return send_file(final_pdf, as_attachment=True, download_name=filename, mimetype="application/pdf")

    return render_template("form.html")
