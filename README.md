# Filling out declarations for academic papers

I am so fed up of the form-filling nonsense. Especially PDFs. I'm going to automate it all, dammit.

So far this only supports Elsevier Author statements forms, and I've only tested it in two. I'll add to it as I go.

# How to use

To use, first prepare a file called `sigs.pdf` and place it in the root folder. To do this:

* Open `sig_template.pdf` in GIMP
* Position a signature in two places in the form: 
   * The "I agree..." bit near the middle (the line with Highest degree, etc). (It's a good idea to add it to the _second_ line, as the first author will often prefill a supplied template with their own name on the first line; and if they don't, it doesn't matter if the first line is blank)
   * The "Corresponding author declaration" near the bottom
* Save it as `sigs.pdf` 

Now, edit `author_details.yaml` to match your details.

Finally, install the requirements with `pip install requirements.txt`

Now, every time you need to sign a form:

     python sign.py <input_pdf_path> <output_pdf_path>
