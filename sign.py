import argparse
import yaml
from pypdf import PdfReader, PdfWriter
from datetime import datetime
from PIL import Image
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os


def sign(input_pdf, output_pdf):
    with open("author_details.yaml", "r") as file:
        author_details = yaml.safe_load(file)

    today_date = datetime.now().strftime("%d/%m/%Y")

    reader = PdfReader(input_pdf)
    stamp = PdfReader("sigs.pdf").pages[0]
    writer = PdfWriter()

    writer.append(reader)

    # Update form fields with data from YAML and today's date
    writer.update_page_form_field_values(
        writer.pages[1],
        {
            "Name 2": author_details["name"],
            "Deg  2": author_details["highest_degree"],
            "Date  2": today_date,
        },
        flags=1,
    )
    writer.pages[1].merge_page(stamp, over=True)

    with open(output_pdf, "wb") as output_stream:
        writer.write(output_stream)


def make_overlay(image_path):
    # A4 dimensions (300dpi)
    a4_width_pts = 595
    a4_height_pts = 842

    a4_width_px = 2480
    a4_height_px = 3507

    coords1 = (216, 3189)  # Corresponding author sig - we blank that out
    coords2 = (1615, 2177)  # Author sig, second row

    sig_image = Image.open(image_path)
    blank_box = Image.new("RGB", (396, 99), (255, 255, 255))

    result_image = Image.new("RGBA", (a4_width_px, a4_height_px), (255, 0, 0, 0))
    result_image.paste(blank_box, coords1)
    result_image.paste(sig_image, coords2)

    temp_png_path = "temp_image.png"
    result_image.save(temp_png_path, format="PNG")

    c = canvas.Canvas("sigs.pdf", pagesize=letter)
    c.drawImage(
        temp_png_path, 0, 0, width=a4_width_pts, height=a4_height_pts, mask="auto"
    )
    c.save()

    os.remove(temp_png_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill a PDF form and add a stamp.")
    parser.add_argument("input_pdf", help="Path to the input PDF form.")
    parser.add_argument("output_pdf", help="Path to the output PDF file.")
    parser.add_argument("sig_png", help="Path to signature image.")
    args = parser.parse_args()
    make_overlay(args.sig_png)
    sign(args.input_pdf, args.output_pdf)
