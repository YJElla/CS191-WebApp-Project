import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract
import json

def extract_text_from_pdf(pdf_path):
    doc = convert_from_path(pdf_path)
    structured_data = {}

    patterns = {
        "date_generated": r"Date Generated\s*\|\s*(.+)",
        "student_info": r"STUDENT NO\s*-\s*NAME\n(\d+-\d+\s+[\w\s,]+)",
        "college_degree_term": r"COLLEGE\s*©\s*DEGREE\s*&\s*MAJOR\s*~\s*TERM&SY\n(.+)",
        "subjects": r"CLASS CODE SUBJECT SECTION UNITS.+",
        "fees": r"TOTAL FEES\s+([0-9,]+\.?\d*)"
    }

    for page_number, page_data in enumerate(doc):
        processed_image = page_data.convert('L')
        processed_image = processed_image.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(2)

        text = pytesseract.image_to_string(processed_image)

        page_data = {
            "Date_Generated": re.search(patterns["date_generated"], text).group(1) if re.search(patterns["date_generated"], text) else None,
            "Student_Info": re.search(patterns["student_info"], text).group(1) if re.search(patterns["student_info"], text) else None,
            "College_Degree_Term": re.search(patterns["college_degree_term"], text).group(1) if re.search(patterns["college_degree_term"], text) else None,
            "Subjects": re.findall(r"\$?\d{4,5}.*", text),
            "Total_Fees": re.search(patterns["fees"], text).group(1) if re.search(patterns["fees"], text) else None
        }

        structured_data[f"Page_{page_number + 1}"] = page_data

    return json.dumps(structured_data, ensure_ascii=False, indent=4)
