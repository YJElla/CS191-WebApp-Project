import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(pdf_path):
    doc = convert_from_path(pdf_path)
    structured_data = {}
    
    # Define regex patterns for capturing data
    patterns = {
        "name": r"Name:\s*([A-Za-z\s]+)",
        "course_degree": r"COLLEGE OF (.+)",
        "course_data": r"(\w+\s*\d+)\s+([\w\s]+)\s+([0-9.]+)",
        "semester": r"(1st Semester|2nd Semester|Midyear)\s*,?\s*(\d{4}-\d{4})",  # Matches semester and year
    }

    for page_number, page_image in enumerate(doc):
        try:
            # Preprocess the image for better OCR results
            processed_image = page_image.convert('L')
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

            # Extract semester and academic year
            semester_match = re.search(patterns["semester"], text)
            if semester_match:
                page_data["Semester"] = semester_match.group(1).strip()
                page_data["Academic Year"] = semester_match.group(2).strip()
            else:
                page_data["Semester"] = "Not found"
                page_data["Academic Year"] = "Not found"

            # Extract course numbers, descriptions, and grades
            courses = []
            for match in re.finditer(patterns["course_data"], text):
                course_no = match.group(1).strip()
                description = match.group(2).strip()
                grade = match.group(3).strip()
                courses.append({
                    "Course No.": course_no,
                    "Description": description,
                    "Grade": grade
                })
            
            page_data["Courses"] = courses  # Add courses list to page data

            # Add page data to structured data
            structured_data[f"Page_{page_number + 1}"] = page_data

        except Exception as e:
            logging.error(f"Error processing page {page_number + 1}: {e}")
            structured_data[f"Page_{page_number + 1}"] = {"Error": str(e)}

    # Convert structured data to JSON format for easy reading
    return json.dumps(structured_data, ensure_ascii=False, indent=4)
