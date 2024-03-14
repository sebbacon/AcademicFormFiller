# Filling out declarations for academic papers

I am so fed up of the form-filling nonsense. Especially PDFs. I'm going to automate it all, dammit.

So far this only supports Elsevier Author statements forms (I've only tested it in two different Elsevier forms); and ICMJE forms.

I'll add to it as I go.

# Setting up

Edit `author_details.yaml` to match your details.

Install the requirements with `pip install requirements.txt`



# How to use: Elsevier

Create a 396x99 pixel image of your signature, with a transparency background, and save it as a PNG. (There's an example at `example_sig.png`)

Now, every time you need to sign a form:

    python sign.py <input_pdf_path> <output_pdf_path> <signature_png_path>

# How to use: ICMJE

Edit `author_details.yaml`, then:

    python lib/icmje/extract_document.py templates/coi_disclosure.docx

(yes, this is inconsistent with Elsevier and needs refactoring)


