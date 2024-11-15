import mysql.connector
from flask import Flask, jsonify, request, render_template
#change if need
CONFIG = {
 'user': 'root',
 'password': 'password',
 'host': 'localhost',
 'database': 'cs191',
 'port': '3306' 
}
app = Flask(__name__)

@app.route('/') #Display All Students
def display():
    res = None
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student")
        rows = cursor.fetchall()
        res = jsonify(rows)
        res.status_code = 200
    
        return res
    except Exception as e:
        print(e)
    finally:
        if res is None:
            return "Error"
        else:
            cursor.close()
            conn.close()
 
@app.route('/student/search-profile/<who>') #Search specific student
def search(who):
    res = None
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor here too
        # Use parameterized queries to prevent SQL injection
        cursor.execute("SELECT * FROM student WHERE first_name LIKE %s", ('%' + who + '%',))
        rows = cursor.fetchall()

        if rows:
            res = jsonify(rows)
        else:
            res = jsonify([])

        res.status_code = 200
        return res
    except Exception as e:
        print(e)
    finally:
        if res is None:
            return "Error"
        else:
            cursor.close()
            conn.close()

@app.route('/student/insert-profile', methods=['POST'])  # Insert specific student
def insert():
    idStudent = request.form.get('idStudent')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    address = request.form.get('address')
    phone_area = request.form.get('phone_area')
    phone_num = request.form.get('phone_num')
    sex = request.form.get('sex')
    birthdate = request.form.get('birthdate')

    # Define the required fields
    required_fields = ["idStudent", "first_name", "last_name", "address", "phone_area", "phone_num", "sex", "birthdate"]

    # Check if all required fields are present
    missing_fields = [field for field in required_fields if not request.form.get(field)]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()

        # Insert the new student record using parameterized query to prevent SQL injection
        cursor.execute(
            "INSERT INTO student (idStudent, last_name, first_name, address, phone_area, phone_num, sex, birthdate) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (idStudent, last_name, first_name, address, phone_area, phone_num, sex, birthdate)
        )
        conn.commit()  # Commit the transaction to the database

        # Return a success response with the ID of the newly inserted student
        return jsonify({"message": "Student inserted successfully", "student_id": idStudent}), 201

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to insert student"}), 500

    finally:
        cursor.close()
        conn.close()

# Route to delete a student by idStudent
@app.route('/student/delete/<idStudent>', methods=['DELETE'])
def deleteStudent(idStudent):
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()

        # Execute the DELETE query with the given idStudent
        cursor.execute("DELETE FROM student WHERE idStudent = %s", (idStudent,))
        conn.commit()  # Commit the transaction to apply changes

        # Check if any rows were affected (i.e., student exists and was deleted)
        if cursor.rowcount > 0:
            return jsonify({"message": f"Student with id {idStudent} deleted successfully"}), 200
        else:
            return jsonify({"error": f"Student with id {idStudent} not found"}), 404

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to delete student"}), 500
    finally:
        cursor.close()
        conn.close()
    
# Route to render the update form (to display it on the browser)
@app.route('/student/edit/<idStudent>', methods=['GET'])
def edit_student_form(idStudent):
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Get the student data from the database to pre-fill the form
        cursor.execute("SELECT * FROM student WHERE idStudent = %s", (idStudent,))
        student = cursor.fetchone()

        if student:
            return render_template('edit_student.html', student=student)
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to retrieve student data"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to update student details from the form submission
@app.route('/student/update', methods=['POST'])
def update_student():
    # Get the form data from the POST request
    idStudent = request.form.get('idStudent')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    address = request.form.get('address')
    phone_area = request.form.get('phone_area')
    phone_num = request.form.get('phone_num')
    sex = request.form.get('sex')
    birthdate = request.form.get('birthdate')

    # Ensure all fields are provided
    if not all([idStudent, first_name, last_name, address, phone_area, phone_num, sex, birthdate]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Connect to the database
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()

        # Prepare the SQL query to update the student's information
        update_query = """
            UPDATE student
            SET first_name = %s, last_name = %s, address = %s, phone_area = %s, phone_num = %s, sex = %s, birthdate = %s
            WHERE idStudent = %s
        """

        # Execute the update query with the form data
        cursor.execute(update_query, (
            first_name,
            last_name,
            address,
            phone_area,
            phone_num,
            sex,
            birthdate,
            idStudent
        ))

        # Commit the changes to the database
        conn.commit()

        # Check if the update was successful
        if cursor.rowcount > 0:
            return jsonify({"message": f"Student with id {idStudent} updated successfully"}), 200
        else:
            return jsonify({"error": f"Student with id {idStudent} not found"}), 404

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to update student"}), 500
    finally:
        cursor.close()
        conn.close()
######################################### TOR PART ###############################################

@app.route('/TOR') #Display All Students
def TORdisplay():
    res = None
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tor")
        rows = cursor.fetchall()
        res = jsonify(rows)
        res.status_code = 200
    
        return res
    except Exception as e:
        print(e)
    finally:
        if res is None:
            return "Error"
        else:
            cursor.close()
            conn.close()

@app.route('/TOR/search-course/<what>') #Search course
def TORsearch(what):
    res = None
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)  
        
        cursor.execute("SELECT * FROM tor WHERE course_descrip LIKE %s", ('%' + what + '%',))
        rows = cursor.fetchall()

        if rows:
            res = jsonify(rows)
        else:
            res = jsonify([])

        res.status_code = 200
        return res
    except Exception as e:
        print(e)
    finally:
        if res is None:
            return "Error"
        else:
            cursor.close()
            conn.close()


@app.route('/TOR/insert-course', methods=['POST'])
def TORinsert():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the relevant fields from JSON data
    idStudent = data.get('idStudent')
    course_code = data.get('course_code')
    course_descrip = data.get('course_descrip')
    grade = data.get('grade')

    # Define the required fields
    required_fields = ["idStudent", "course_code", "course_descrip", "grade"]

    # Check if all required fields are present
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        # Connect to the database
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()

        # Insert the new student course record using parameterized query
        cursor.execute(
            "INSERT INTO tor (idStudent, course_code, course_descrip, grade) "
            "VALUES (%s, %s, %s, %s)",
            (idStudent, course_code, course_descrip, grade)
        )
        conn.commit()

        # Return success response
        return jsonify({"message": "Student course inserted successfully", "student_id": idStudent}), 201

    except mysql.connector.Error as err:
        app.logger.error(f"Error: {err}")
        return jsonify({"error": "Failed to insert student course", "details": str(err)}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False in production