import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract
import json

def extract_text_from_pdf(pdf_path):
    doc = convert_from_path(pdf_path)
    structured_data = {}
    
    # Define regex patterns for capturing data
    patterns = {
        "name": r"Name:\s*([A-Za-z\s]+)",  # Extracts name after "Name:"
        "course_degree": r"COLLEGE OF (.+)",  # Captures the college or course/degree title
        "course_data": r"(\w+\s*\d+)\s+([\w\s]+)\s+([0-9.]+)"  # Extracts course no., description, and grade
    }

    for page_number, page_data in enumerate(doc):
        # Preprocess the image for better OCR results
        processed_image = page_data.convert('L')
        processed_image = processed_image.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(2)

        # Extract text from the processed image
        text = pytesseract.image_to_string(processed_image)

        # Create a dictionary to store extracted data for each page
        page_data = {}

        # Extract the student's name
        name_match = re.search(patterns["name"], text)
        page_data["Name"] = name_match.group(1).strip() if name_match else "Not found"

        # Extract the course/degree
        degree_match = re.search(patterns["course_degree"], text)
        page_data["Course/Degree"] = degree_match.group(1).strip() if degree_match else "Not found"

        # Extract course numbers, descriptions, and grades
        courses = []
        for match in re.finditer(patterns["course_data"], text):
            course_no = match.group(1).strip()
            description = match.group(2).strip()
            grade = match.group(3).strip()
            courses.append({"Course No.": course_no, "Description": description, "Grade": grade})
        
        page_data["Courses"] = courses  # Add courses list to page data

        # Add page data to structured data
        structured_data[f"Page_{page_number + 1}"] = page_data

    # Convert structured data to JSON format for easy reading
    return json.dumps(structured_data, ensure_ascii=False, indent=4)