import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
from ocr_pdf import extract_text_from_pdf  # Import the PDF processing function
import mysql.connector


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'C:/Users/yanni/OneDrive/Desktop/1sr Sem [Year 3]/CS165/web_app' #Specify folder directory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB

app.secret_key = "my_secret_key" 


# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def login():
    return render_template('login_page.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    # Replace with actual usernames
    if username == 'Yanni' and password == 'password':  # Dummy credentials
        session['user'] = username  # Store user in session
        return redirect(url_for('TOR_page'))  # Redirect to upload page
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('login'))


@app.route('/TOR_page')
def TOR_page():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('TOR_page.html')

@app.route('/setup1')
def setup1():
    return render_template('setup1.html')

@app.route('/setup2')
def setup2():
    return render_template('setup2.html')

@app.route('/setup3')
def setup3():
    return render_template('setup3.html')

@app.route('/setup4')
def setup4():
    return render_template('setup4.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    form_data = request.form.to_dict()
    session.update(form_data)  # Store form data in session

    if 'first_name' in form_data and 'last_name' in form_data and 'address' in form_data:
        return redirect(url_for('setup2'))
    elif 'birthdate' in form_data and 'sex' in form_data and 'phone' in form_data:
        return redirect(url_for('setup3'))
    elif 'email' in form_data and 'role' in form_data and 'password' in form_data and 'confirm_password' in form_data:
        return redirect(url_for('setup4'))
    elif 'university_attended' in form_data and 'degree_title' in form_data and 'years_attended' in form_data and 'student_id' in form_data:
        return redirect(url_for('TOR_page'))
    else:
        # All data is collected, so insert into the database
        try:
            insert_user_data(session)
            flash("Your data has been successfully saved!")
        except Exception as e:
            flash(f"An error occurred: {e}")
        return redirect(url_for('setup1'))  # Redirect to start or a confirmation page

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

        # Check file type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(file_path)

        # Clean up uploaded file
        os.remove(file_path)

        return render_template('result.html', extracted_text=text)

def extract_text_from_image(image_path):
    with Image.open(image_path) as img:
        text = pytesseract.image_to_string(img)
    return text

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status' : 404,
        'message' : 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp 

if __name__ == '__main__':
    app.run(debug=True)
