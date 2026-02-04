from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'helloworld'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login/<user_type>')
def login(user_type):
    return render_template('login.html', user_type=user_type)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    user_type = request.form.get('user_type')
    session['user_type'] = user_type
    
    if user_type == 'user':
        return redirect(url_for('citizen_dashboard'))
    elif user_type == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif user_type == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('index'))

@app.route('/citizen/dashboard')
def citizen_dashboard():
    return render_template('citizen/dashboard.html')

@app.route('/citizen/book-appointment')
def book_appointment():
    return render_template('citizen/book_appointment.html')

@app.route('/citizen/precautions')
def view_precautions():
    return render_template('citizen/precautions.html')


@app.route('/doctor/dashboard')
def doctor_dashboard():
    return render_template('doctor/dashboard.html')

@app.route('/doctor/appointments')
def doctor_appointments():
    return render_template('doctor/appointments.html')

@app.route('/doctor/treat-patient')
def treat_patient():
    return render_template('doctor/treat_patient.html')

@app.route('/doctor/analytics')
def healthcare_analytics():
    return render_template('doctor/analytics.html')

@app.route('/doctor/cure_code_creation')
def healthcare_cure_code_creation():
    return render_template('doctor/cure_code_creation.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/beds')
def manage_beds():
    return render_template('admin/beds.html')

@app.route('/admin/equipment')
def manage_equipment():
    return render_template('admin/equipment.html')

@app.route('/admin/medicine')
def manage_medicine():
    return render_template('admin/medicine.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
