from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import os

tesseract_cmd = 'tesseract' 
tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Run OCR on the saved image
        text = extract_text(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return render_template('result.html', extracted_text=text)

def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

if __name__ == '__main__':
    app.run(debug=True)