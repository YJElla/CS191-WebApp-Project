import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract
import json

# Define the file path
filePath = 'C:/Users/yanni/OneDrive/Pictures/OCRTesting/tor.pdf'
doc = convert_from_path(filePath)
path, fileName = os.path.split(filePath)
fileBaseName, fileExtension = os.path.splitext(fileName)

# Dictionary to store structured OCR data
structured_data = {}

# Regex patterns to capture key information
patterns = {
    "date_generated": r"Date Generated\s*\|\s*(.+)",
    "student_info": r"STUDENT NO\s*-\s*NAME\n(\d+-\d+\s+[\w\s,]+)",
    "college_degree_term": r"COLLEGE\s*©\s*DEGREE\s*&\s*MAJOR\s*~\s*TERM&SY\n(.+)",
    "subjects": r"CLASS CODE SUBJECT SECTION UNITS.+",
    "fees": r"TOTAL FEES\s+([0-9,]+\.?\d*)"
}

# Process each page in the PDF
for page_number, page_data in enumerate(doc):
    # Preprocess the image (grayscale and enhanced for OCR)
    processed_image = page_data.convert('L')
    processed_image = processed_image.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(processed_image)
    processed_image = enhancer.enhance(2)

    # Extract text using Tesseract
    text = pytesseract.image_to_string(processed_image)

    # Extract specific data using regex
    page_data = {
        "Date_Generated": re.search(patterns["date_generated"], text).group(1) if re.search(patterns["date_generated"], text) else None,
        "Student_Info": re.search(patterns["student_info"], text).group(1) if re.search(patterns["student_info"], text) else None,
        "College_Degree_Term": re.search(patterns["college_degree_term"], text).group(1) if re.search(patterns["college_degree_term"], text) else None,
        "Subjects": re.findall(r"\$?\d{4,5}.*", text),  # Matches each line with subject information
        "Total_Fees": re.search(patterns["fees"], text).group(1) if re.search(patterns["fees"], text) else None
    }

    # Save page data into structured data
    structured_data[f"Page_{page_number + 1}"] = page_data

# Save or print structured OCR data in JSON format
json_output_path = os.path.join(path, f"{fileBaseName}_structured_ocr_output.json")
with open(json_output_path, 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=4)

print(f"Structured OCR results saved to {json_output_path}")
