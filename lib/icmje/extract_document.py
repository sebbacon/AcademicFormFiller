from lxml import etree
import zipfile
import os
import sys
from pathlib import Path
import yaml
from datetime import datetime
import shutil

CHECKBOX = "☒"
EMPTY_CHECKBOX = "☐"
today_date = datetime.now().strftime("%d/%m/%Y")
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

ns_strings = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"'


def replace_simple_field_values(root, config):
    replace_first_text_following_fieldname(root, "Date:", today_date)
    replace_first_text_following_fieldname(root, "Your Name:", config["name"])
    replace_first_text_following_fieldname(
        root, "Manuscript Title:", config["manuscript_title"]
    )
    replace_first_text_following_fieldname(
        root, "Manuscript Number (if known):", config["manuscript_number"]
    )
    replace_first_text_following_fieldname(
        root,
        "Please place an “X” next to the following statement to indicate your agreement:",
        CHECKBOX,
    )


def extract_document_xml(docx_path, output_directory, config):
    """Unpack the `document.xml` from the docx. This is the core document content
    we want to play with.
    """
    with zipfile.ZipFile(docx_path, "r") as docx_zip:
        document_xml_content = docx_zip.read("word/document.xml")
        root = etree.XML(document_xml_content)
        replace_simple_field_values(root, config)
        replace_disclosure_tables(root, config)
        formatted_xml_content = etree.tostring(
            root, pretty_print=True, encoding="unicode"
        )
        output_path = os.path.join(output_directory, "document.xml")
        with open(output_path, "w") as output_file:
            output_file.write(formatted_xml_content)
    return output_path


def reinsert_document_xml(docx_path, modified_xml_path, output_docx_path):
    # Temporary directory to store the unzipped files
    temp_dir = os.path.join(os.path.dirname(modified_xml_path), "temp_extracted")
    os.makedirs(temp_dir, exist_ok=True)

    # Unzip the original .docx file
    with zipfile.ZipFile(docx_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Replace the document.xml with the modified version
    modified_document_xml_path = os.path.join(temp_dir, "word", "document.xml")
    with open(modified_xml_path, "rb") as modified_xml_file:
        modified_xml_content = modified_xml_file.read()

    with open(modified_document_xml_path, "wb") as document_xml_file:
        document_xml_file.write(modified_xml_content)

    # Zip the contents back into a new .docx file
    with zipfile.ZipFile(output_docx_path, "w", zipfile.ZIP_DEFLATED) as docx_zip:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                docx_zip.write(file_path, arcname)

    shutil.rmtree(temp_dir)
    return output_docx_path


def replace_first_text_following_fieldname(xml_root, match, replacement):
    # Find all <w:t> elements
    w_t_elements = xml_root.xpath(".//w:t", namespaces=ns)

    # Flag to indicate whether the next <w:t> element should have its text replaced
    replace_next_text = False

    for elem in w_t_elements:
        # If the flag is set, replace the text of this element
        if replace_next_text:
            elem.text = replacement
            break  # Stop after replacing the first occurrence

        # Check if the current element contains the text 'Date:'
        if elem.text and elem.text == match:
            replace_next_text = True


def replace_disclosure_tables(source_elem, config):
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    xpath = xpath = (
        ".//w:tc[w:tcPr/w:tcW[@w:w='8751' and @w:type='dxa'] and w:tcPr/w:tcBorders[not(node())]]"
    )
    source_disclosures_to_replace = source_elem.xpath(xpath, namespaces=ns)

    # This fragment represents a single disclosure row consisting of a tickbox,
    # entity with whom COI exists, and the details.
    #
    # It contains variables in {{ this_format }} for replacement
    # We then insert it once for each disclosure type into the original (root) document
    base_directory = Path(__file__).resolve().parent.parent.parent
    replacement_xml = open(
        base_directory / "templates" / "row_fragment_formatted.xml", "r"
    ).read()

    all_author_disclosures = config["disclosures"]

    assert len(all_author_disclosures) == len(source_disclosures_to_replace)

    # Iterate over each "disclosure" in the yaml, matching
    # it with a corresponding row in the source document (we assume both
    # to be in the same order)
    for i, author_disclosures_for_coi in enumerate(all_author_disclosures.values()):
        generated_disclosure_xml = replacement_xml
        if author_disclosures_for_coi:
            # Tick the box
            generated_disclosure_xml = generated_disclosure_xml.replace(
                "{{ disclosure_checkbox }}", CHECKBOX
            )

        else:
            # It's an empty array; leave the checkbox empty, and add a dummy row
            # so there's empty strings in the text cells
            generated_disclosure_xml = generated_disclosure_xml.replace(
                "{{ disclosure_checkbox }}", EMPTY_CHECKBOX
            )

            author_disclosures_for_coi.append({"entity": "", "comment": ""})
        generated_disclosure_elem = etree.XML(
            f"<root {ns_strings}>{generated_disclosure_xml}</root>"
        )
        declaration_column = generated_disclosure_elem.xpath(
            ".//*[@id='declaration']", namespaces=ns
        )[0]
        declaration_column_str_template = etree.tostring(declaration_column).decode(
            "utf-8"
        )
        for child in list(declaration_column):
            declaration_column.remove(child)

        for individual_disclosure in author_disclosures_for_coi:
            declaration_column_str = declaration_column_str_template
            # get the subfragment with id "declaration" by
            # extracting xpath and converting back to a string so we
            # can do substitutions

            # Do the substitutions
            declaration_column_str = declaration_column_str.replace(
                "{{ declaration.entity }}", individual_disclosure["entity"]
            )
            declaration_column_str = declaration_column_str.replace(
                "{{ declaration.comment }}", individual_disclosure["comment"]
            )
            # add it back in

            new_column = etree.fromstring(
                declaration_column_str,
                etree.XMLParser(ns_clean=True, recover=True, remove_blank_text=True),
            )

            declaration_column.getparent().append(new_column)

        source_disclosure = source_disclosures_to_replace[i]

        fill_key = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill"
        try:
            fill = source_disclosure.find(".//w:shd", ns).get(fill_key)
        except AttributeError:
            # In the source doc, there's just no `shd` tag. We add one with an
            # "auto" value as the template we made needed something for each row.
            fill = "auto"
        generated_disclosure_elem.find(".//w:shd", ns).set(fill_key, fill)

        parent = source_disclosure.getparent()

        for child in list(generated_disclosure_elem):
            parent.insert(parent.index(source_disclosure), child)
        parent.remove(source_disclosure)

    return source_elem


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_docx_file>")
        sys.exit(1)

    docx_path = sys.argv[1]
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory = script_directory
    with open("author_details.yaml", "r") as file:
        config = yaml.safe_load(file)
    modified_xml_path = extract_document_xml(docx_path, output_directory, config)
    output_docx_path = "coi_disclosure.docx"
    modified_document = reinsert_document_xml(
        docx_path, modified_xml_path, output_docx_path
    )
    print("Written new doc to", modified_document)
