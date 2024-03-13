# Filling out declarations for academic papers

I am so fed up of the form-filling nonsense. Especially PDFs. I'm going to automate it all, dammit.

So far this only supports Elsevier Author statements forms (I've only tested it in two different Elsevier forms); and ICMJE forms.

I'll add to it as I go.

# Setting up

Edit `author_details.yaml` to match your details.

Install the requirements with `pip install requirements.txt`



# How to use: Elsevier

To use, first prepare a file called `sigs.pdf` and place it in the root folder. To do this:

* Open `sig_template.pdf` in GIMP
* Position a signature in two places in the form: 
   * The "I agree..." bit near the middle (the line with Highest degree, etc). (It's a good idea to add it to the _second_ line, as the first author will often prefill a supplied template with their own name on the first line; and if they don't, it doesn't matter if the first line is blank)
   * The "Corresponding author declaration" near the bottom
* Save it as `sigs.pdf` 

Now, every time you need to sign a form:

     python sign.py <input_pdf_path> <output_pdf_path>

# How to use: ICMJE

Edit `author_details.yaml`, then:

    python lib/icmje/extract_document.py templates/coi_disclosure.docx

(yes, this is inconsistent with Elsevier and needs refactoring)


