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

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Replace with your DB host
            user="root",  # Replace with your MySQL username
            password="password",  # Replace with your MySQL password
            database="cs191"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def login():
    return render_template('login_page.html')



@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    
    connection = get_db_connection()

    
    if email == "teacher@up.edu.ph" and password == "teacher_password":
        session['user'] = email # Store user in session
        return redirect(url_for('teacherdashboard'))

    if not connection:
        flash('Database connection failed. Please try again later.')
        return redirect(url_for('login'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM student WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()        #fetches result of execute query

        if user:                        #if user is in the database/ already signed up 
            session['user'] = user['email']
            # session['role'] = user['role']
            # if user['role'] == 'student':
            return redirect(url_for('status')) #redirect to status page
            # elif user['role'] == 'teacher':
            #     return redirect(url_for('teacherdashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
    finally:
        cursor.close()
        connection.close()

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/updateinfo')
def updateinfo():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('updateinfo.html')

@app.route('/TOR_page')
def TOR_page():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('TOR_page.html')

@app.route('/teacherdashboard')
def teacherdashboard():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('teacherdashboard.html')

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

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Update session with the latest form data
    form_data = request.form.to_dict()
    session.update(form_data)  # Append new data to the session
    
    # Check which step we are on and redirect accordingly
    if 'first_name' in form_data and 'last_name' in form_data and 'address' in form_data:
        return redirect(url_for('setup2'))  # Redirect to next step
    elif 'birthdate' in form_data and 'sex' in form_data and 'phone_num' in form_data:
        return redirect(url_for('setup3'))
    elif 'email' in form_data and 'password' in form_data and 'confirm_password' in form_data:
        if form_data['password'] != form_data['confirm_password']:
            print(form_data)
            flash("password does not match")
            return redirect(url_for('setup3'))
        else:
            return redirect(url_for('setup4'))
    elif 'university' in form_data and 'degree_title' in form_data and 'years_attended' in form_data and 'idStudent' in form_data:
         # All steps completed: Insert into the database
        
        if all(key in session for key in ['first_name', 'last_name', 'address', 'birthdate', 'sex', 'phone_num', 'email', 'password', 'university', 'degree_title', 'years_attended', 'idStudent']):
            connection = get_db_connection()
            if not connection:
                flash("Database connection failed.")
                return redirect(url_for('setup1'))
            try:
       
                cursor = connection.cursor()
                query = """
                    INSERT INTO student (first_name, last_name, address, birthdate, sex, phone_num, email, password, university, degree_title, years_attended, idStudent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    session['first_name'], session['last_name'], session['address'], 
                    session['birthdate'], session['sex'], session['phone_num'], 
                    session['email'], session['password'], session['university'], 
                    session['degree_title'], session['years_attended'], session['idStudent']
                ))

                connection.commit()
                flash("Signup successful!")
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                flash("Email already exists.")
                return redirect(url_for('setup1'))
            finally:
                cursor.close()
                connection.close()
        else:
            flash("Incomplete data. Please complete all steps.")
            return redirect(url_for('setup1'))  # Redirect to start or an error page


   

    

@app.route('/upload_file', methods=['POST'])
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

@app.route('/student_info')
def student_info():
   # Fetch the student's information from the database or session
    user = session.get('user')  # Assuming the user's ID is stored in the session
    print(user)
    if not user:
        flash("You need to log in to view your information.")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Query the database for student information
    cursor.execute("SELECT * FROM student WHERE email = %s", (user,))
    student_data = cursor.fetchone()

    if not student_data:
        flash("Student information not found.")
        return redirect(url_for(''))  # Redirect to the setup flow if info is missing

    # Pass the retrieved data to the template
    return render_template('student_info.html', student_info=student_data)

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
