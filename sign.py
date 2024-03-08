import argparse
import yaml
from pypdf import PdfReader, PdfWriter
from datetime import datetime


parser = argparse.ArgumentParser(description="Fill a PDF form and add a stamp.")
parser.add_argument("input_pdf", help="Path to the input PDF form.")
parser.add_argument("output_pdf", help="Path to the output PDF file.")
args = parser.parse_args()

with open("author_details.yaml", "r") as file:
    author_details = yaml.safe_load(file)

today_date = datetime.now().strftime("%d/%m/%Y")

reader = PdfReader(args.input_pdf)
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

with open(args.output_pdf, "wb") as output_stream:
    writer.write(output_stream)
