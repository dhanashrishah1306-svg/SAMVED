from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import *
from datetime import datetime, timedelta
import os
import json
import random
import string

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sakshi-solapur-2024-secure-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sakshi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ==================== UTILITY FUNCTIONS ====================

def generate_patient_qr():
    """Generate unique QR code for patient"""
    return 'SAKSHI-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def login_required(user_type=None):
    """Decorator to check if user is logged in"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to continue', 'warning')
                return redirect(url_for('login_page'))
            if user_type and session.get('user_type') != user_type:
                flash('Unauthorized access', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ==================== PUBLIC ROUTES ====================

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
def login_page(user_type='patient'):
    return render_template('login.html', user_type=user_type)

@app.route('/register/<user_type>')
def register_page(user_type='patient'):
    return render_template('register.html', user_type=user_type)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    user_type = request.form.get('user_type')
    
    user = User.query.filter_by(username=username, user_type=user_type).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['user_type'] = user.user_type
        
        if user_type == 'patient':
            return redirect(url_for('patient_dashboard'))
        elif user_type == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
    
    flash('Invalid credentials', 'danger')
    return redirect(url_for('login_page', user_type=user_type))

@app.route('/register_user', methods=['POST'])
def register_user():
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        user_type = request.form.get('user_type')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register_page', user_type=user_type))
        
        # Create user
        user = User(username=username, email=email, phone=phone, user_type=user_type)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create profile based on user type
        if user_type == 'patient':
            patient = Patient(
                user_id=user.id,
                qr_code=generate_patient_qr(),
                full_name=request.form.get('full_name'),
                date_of_birth=datetime.strptime(request.form.get('dob'), '%Y-%m-%d'),
                gender=request.form.get('gender'),
                blood_group=request.form.get('blood_group'),
                address=request.form.get('address'),
                ward_number=request.form.get('ward_number'),
                zone=request.form.get('zone'),
                aadhar_number=request.form.get('aadhar_number'),
                allergies=json.dumps([]),
                chronic_conditions=json.dumps([]),
                current_medications=json.dumps([]),
                vaccination_records=json.dumps([])
            )
            db.session.add(patient)
        
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login_page', user_type=user_type))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'danger')
        return redirect(url_for('register_page', user_type=user_type))

# ==================== PATIENT ROUTES ====================

@app.route('/patient/dashboard')
@login_required('patient')
def patient_dashboard():
    user = User.query.get(session['user_id'])
    patient = Patient.query.filter_by(user_id=user.id).first()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='scheduled'
    ).filter(Appointment.appointment_date >= datetime.now()).order_by(Appointment.appointment_date).limit(5).all()
    
    # Get recent medical records
    recent_records = MedicalRecord.query.filter_by(
        patient_id=patient.id
    ).order_by(MedicalRecord.visit_date.desc()).limit(5).all()
    
    # Get active health alerts for patient's zone
    alerts = HealthAlert.query.filter_by(is_active=True).filter(
        (HealthAlert.expires_at == None) | (HealthAlert.expires_at > datetime.now())
    ).all()
    
    zone_alerts = [a for a in alerts if not a.zones or patient.zone in json.loads(a.zones or '[]')]
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         appointments=upcoming_appointments,
                         medical_records=recent_records,
                         alerts=zone_alerts)

@app.route('/patient/qr-code')
@login_required('patient')
def view_qr_code():
    user = User.query.get(session['user_id'])
    patient = Patient.query.filter_by(user_id=user.id).first()
    qr_image = patient.generate_qr_code()
    
    return render_template('patient/qr_code.html', patient=patient, qr_image=qr_image)

@app.route('/patient/book-appointment', methods=['GET', 'POST'])
@login_required('patient')
def book_appointment():
    if request.method == 'POST':
        try:
            user = User.query.get(session['user_id'])
            patient = Patient.query.filter_by(user_id=user.id).first()
            
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=request.form.get('doctor_id'),
                appointment_date=datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%dT%H:%M'),
                appointment_type=request.form.get('appointment_type'),
                symptoms=request.form.get('symptoms'),
                is_telemedicine=request.form.get('is_telemedicine') == 'on'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking appointment: {str(e)}', 'danger')
    
    # Get available doctors
    doctors = Doctor.query.all()
    return render_template('patient/book_appointment.html', doctors=doctors)

@app.route('/patient/medical-history')
@login_required('patient')
def medical_history():
    user = User.query.get(session['user_id'])
    patient = Patient.query.filter_by(user_id=user.id).first()
    
    records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(
        MedicalRecord.visit_date.desc()
    ).all()
    
    return render_template('patient/medical_history.html', patient=patient, records=records)

@app.route('/patient/precautions')
@login_required('patient')
def view_precautions():
    # Get disease outbreaks in user's zone
    user = User.query.get(session['user_id'])
    patient = Patient.query.filter_by(user_id=user.id).first()
    
    outbreaks = DiseaseOutbreak.query.filter_by(
        zone=patient.zone,
        outbreak_status='active'
    ).all()
    
    return render_template('patient/precautions.html', outbreaks=outbreaks, patient=patient)

@app.route('/patient/vaccination-status')
@login_required('patient')
def vaccination_status():
    user = User.query.get(session['user_id'])
    patient = Patient.query.filter_by(user_id=user.id).first()
    
    # Get active vaccination campaigns
    campaigns = VaccinationCampaign.query.filter_by(status='ongoing').all()
    
    return render_template('patient/vaccination.html', patient=patient, campaigns=campaigns)

# ==================== DOCTOR ROUTES ====================

@app.route('/doctor/dashboard')
@login_required('doctor')
def doctor_dashboard():
    user = User.query.get(session['user_id'])
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    
    # Today's appointments
    today_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id
    ).filter(
        db.func.date(Appointment.appointment_date) == datetime.now().date()
    ).all()
    
    # Pending appointments
    pending = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status='scheduled'
    ).count()
    
    # Total patients treated
    total_patients = MedicalRecord.query.filter_by(doctor_id=doctor.id).distinct(
        MedicalRecord.patient_id
    ).count()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         today_appointments=today_appointments,
                         pending_count=pending,
                         total_patients=total_patients)

@app.route('/doctor/appointments')
@login_required('doctor')
def doctor_appointments():
    user = User.query.get(session['user_id'])
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('doctor/appointments.html', appointments=appointments, doctor=doctor)

@app.route('/doctor/treat-patient/<int:appointment_id>', methods=['GET', 'POST'])
@login_required('doctor')
def treat_patient(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = appointment.patient
    
    if request.method == 'POST':
        try:
            # Create medical record
            record = MedicalRecord(
                patient_id=patient.id,
                doctor_id=appointment.doctor_id,
                appointment_id=appointment_id,
                chief_complaint=request.form.get('chief_complaint'),
                diagnosis=request.form.get('diagnosis'),
                symptoms=request.form.get('symptoms'),
                temperature=request.form.get('temperature'),
                blood_pressure=request.form.get('blood_pressure'),
                pulse_rate=request.form.get('pulse_rate'),
                oxygen_saturation=request.form.get('oxygen_saturation'),
                prescription=request.form.get('prescription'),
                treatment_plan=request.form.get('treatment_plan'),
                lab_tests_ordered=request.form.get('lab_tests')
            )
            
            # Update appointment status
            appointment.status = 'completed'
            
            db.session.add(record)
            db.session.commit()
            
            flash('Treatment record saved successfully!', 'success')
            return redirect(url_for('doctor_appointments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving record: {str(e)}', 'danger')
    
    # Get patient's medical history
    history = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(
        MedicalRecord.visit_date.desc()
    ).limit(5).all()
    
    return render_template('doctor/treat_patient.html',
                         appointment=appointment,
                         patient=patient,
                         history=history)

@app.route('/doctor/scan-qr', methods=['POST'])
@login_required('doctor')
def scan_patient_qr():
    """Scan patient QR code to get medical history"""
    qr_data = request.json.get('qr_data')
    
    try:
        patient_data = json.loads(qr_data)
        patient = Patient.query.filter_by(qr_code=patient_data['qr_code']).first()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get medical history
        records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(
            MedicalRecord.visit_date.desc()
        ).limit(10).all()
        
        return jsonify({
            'patient': {
                'id': patient.id,
                'name': patient.full_name,
                'dob': str(patient.date_of_birth),
                'blood_group': patient.blood_group,
                'allergies': json.loads(patient.allergies or '[]'),
                'chronic_conditions': json.loads(patient.chronic_conditions or '[]'),
                'current_medications': json.loads(patient.current_medications or '[]')
            },
            'records': [{
                'date': str(r.visit_date),
                'diagnosis': r.diagnosis,
                'prescription': r.prescription
            } for r in records]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/doctor/analytics')
@login_required('doctor')
def healthcare_analytics():
    user = User.query.get(session['user_id'])
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    
    # Get analytics data
    # Disease distribution
    records = MedicalRecord.query.filter_by(doctor_id=doctor.id).all()
    
    # Zone-wise patient distribution
    zone_data = db.session.query(
        Patient.zone,
        db.func.count(Patient.id)
    ).join(MedicalRecord).filter(
        MedicalRecord.doctor_id == doctor.id
    ).group_by(Patient.zone).all()
    
    # Monthly consultations
    monthly_data = db.session.query(
        db.func.strftime('%Y-%m', MedicalRecord.visit_date).label('month'),
        db.func.count(MedicalRecord.id).label('count')
    ).filter(
        MedicalRecord.doctor_id == doctor.id
    ).group_by('month').order_by('month').all()
    
    return render_template('doctor/analytics.html',
                         zone_data=zone_data,
                         monthly_data=monthly_data,
                         doctor=doctor)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    # Overall statistics
    total_hospitals = Hospital.query.count()
    total_beds = db.session.query(db.func.sum(Hospital.total_beds)).scalar() or 0
    available_beds = db.session.query(db.func.sum(Hospital.available_beds)).scalar() or 0
    
    # Equipment status
    critical_equipment = Equipment.query.filter_by(health_status='critical').count()
    
    # Medicine stock alerts
    low_stock_medicines = MedicineStock.query.filter(
        MedicineStock.stock_status.in_(['low', 'critical'])
    ).count()
    
    # Active disease outbreaks
    active_outbreaks = DiseaseOutbreak.query.filter_by(outbreak_status='active').count()
    
    # Recent alerts
    hospitals = Hospital.query.all()
    
    return render_template('admin/dashboard.html',
                         total_hospitals=total_hospitals,
                         total_beds=total_beds,
                         available_beds=available_beds,
                         bed_occupancy=round((total_beds - available_beds) / total_beds * 100, 1) if total_beds > 0 else 0,
                         critical_equipment=critical_equipment,
                         low_stock_medicines=low_stock_medicines,
                         active_outbreaks=active_outbreaks,
                         hospitals=hospitals)

@app.route('/admin/beds')
@login_required('admin')
def manage_beds():
    hospitals = Hospital.query.all()
    return render_template('admin/beds.html', hospitals=hospitals)

@app.route('/admin/update-beds/<int:hospital_id>', methods=['POST'])
@login_required('admin')
def update_beds(hospital_id):
    try:
        hospital = Hospital.query.get_or_404(hospital_id)
        
        hospital.available_beds = request.form.get('available_beds', type=int)
        hospital.available_icu_beds = request.form.get('available_icu_beds', type=int)
        hospital.available_ventilators = request.form.get('available_ventilators', type=int)
        
        db.session.commit()
        flash('Bed availability updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating beds: {str(e)}', 'danger')
    
    return redirect(url_for('manage_beds'))

@app.route('/admin/equipment')
@login_required('admin')
def manage_equipment():
    equipment = Equipment.query.all()
    hospitals = Hospital.query.all()
    return render_template('admin/equipment.html', equipment=equipment, hospitals=hospitals)

@app.route('/admin/add-equipment', methods=['POST'])
@login_required('admin')
def add_equipment():
    try:
        equipment = Equipment(
            hospital_id=request.form.get('hospital_id'),
            equipment_name=request.form.get('equipment_name'),
            equipment_type=request.form.get('equipment_type'),
            quantity=request.form.get('quantity', type=int),
            working_condition=request.form.get('working_condition', type=int),
            health_status=request.form.get('health_status')
        )
        
        db.session.add(equipment)
        db.session.commit()
        flash('Equipment added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding equipment: {str(e)}', 'danger')
    
    return redirect(url_for('manage_equipment'))

@app.route('/admin/medicine')
@login_required('admin')
def manage_medicine():
    medicines = MedicineStock.query.all()
    hospitals = Hospital.query.all()
    return render_template('admin/medicine.html', medicines=medicines, hospitals=hospitals)

@app.route('/admin/add-medicine', methods=['POST'])
@login_required('admin')
def add_medicine():
    try:
        # Determine stock status
        quantity = request.form.get('quantity', type=int)
        reorder_level = request.form.get('reorder_level', type=int)
        
        if quantity == 0:
            stock_status = 'critical'
        elif quantity < reorder_level:
            stock_status = 'low'
        else:
            stock_status = 'adequate'
        
        medicine = MedicineStock(
            hospital_id=request.form.get('hospital_id'),
            medicine_name=request.form.get('medicine_name'),
            generic_name=request.form.get('generic_name'),
            category=request.form.get('category'),
            quantity=quantity,
            unit=request.form.get('unit'),
            reorder_level=reorder_level,
            batch_number=request.form.get('batch_number'),
            expiry_date=datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d') if request.form.get('expiry_date') else None,
            stock_status=stock_status
        )
        
        db.session.add(medicine)
        db.session.commit()
        flash('Medicine added to inventory!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding medicine: {str(e)}', 'danger')
    
    return redirect(url_for('manage_medicine'))

@app.route('/admin/disease-surveillance')
@login_required('admin')
def disease_surveillance():
    outbreaks = DiseaseOutbreak.query.order_by(DiseaseOutbreak.last_updated.desc()).all()
    
    # Zone-wise outbreak summary
    zone_summary = db.session.query(
        DiseaseOutbreak.zone,
        db.func.count(DiseaseOutbreak.id).label('outbreak_count'),
        db.func.sum(DiseaseOutbreak.active_cases).label('total_cases')
    ).group_by(DiseaseOutbreak.zone).all()
    
    return render_template('admin/disease_surveillance.html',
                         outbreaks=outbreaks,
                         zone_summary=zone_summary)

@app.route('/admin/health-alerts')
@login_required('admin')
def health_alerts():
    alerts = HealthAlert.query.order_by(HealthAlert.created_at.desc()).all()
    return render_template('admin/health_alerts.html', alerts=alerts)

@app.route('/admin/create-alert', methods=['POST'])
@login_required('admin')
def create_alert():
    try:
        alert = HealthAlert(
            alert_type=request.form.get('alert_type'),
            title=request.form.get('title'),
            message=request.form.get('message'),
            severity=request.form.get('severity'),
            zones=request.form.get('zones'),
            ward_numbers=request.form.get('ward_numbers'),
            message_marathi=request.form.get('message_marathi')
        )
        
        db.session.add(alert)
        db.session.commit()
        flash('Health alert created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating alert: {str(e)}', 'danger')
    
    return redirect(url_for('health_alerts'))

# ==================== API ENDPOINTS ====================

@app.route('/api/bed-availability')
def api_bed_availability():
    """Real-time bed availability API"""
    hospitals = Hospital.query.all()
    
    data = [{
        'hospital_id': h.id,
        'name': h.name,
        'zone': h.zone,
        'total_beds': h.total_beds,
        'available_beds': h.available_beds,
        'icu_beds': h.icu_beds,
        'available_icu_beds': h.available_icu_beds,
        'ventilators': h.ventilators,
        'available_ventilators': h.available_ventilators
    } for h in hospitals]
    
    return jsonify(data)

@app.route('/api/disease-stats')
def api_disease_stats():
    """Disease outbreak statistics"""
    outbreaks = DiseaseOutbreak.query.filter_by(outbreak_status='active').all()
    
    data = [{
        'disease_name': o.disease_name,
        'zone': o.zone,
        'total_cases': o.total_cases,
        'active_cases': o.active_cases,
        'alert_level': o.alert_level
    } for o in outbreaks]
    
    return jsonify(data)

# ==================== LOGOUT ====================

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            return
        
        # Create sample admin
        admin_user = User(username='admin', email='admin@solapur.gov.in', user_type='admin', phone='9876543210')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create sample hospitals
        hospitals_data = [
            {
                'name': 'Civil Hospital Solapur',
                'hospital_type': 'District Hospital',
                'zone': 'Zone A',
                'ward_number': 1,
                'total_beds': 200,
                'available_beds': 45,
                'icu_beds': 20,
                'available_icu_beds': 5,
                'ventilators': 10,
                'available_ventilators': 3
            },
            {
                'name': 'PHC Vijapur',
                'hospital_type': 'Primary Health Center',
                'zone': 'Zone B',
                'ward_number': 5,
                'total_beds': 50,
                'available_beds': 12,
                'icu_beds': 5,
                'available_icu_beds': 2,
                'ventilators': 2,
                'available_ventilators': 1
            },
            {
                'name': 'CHC Ashok Chowk',
                'hospital_type': 'Community Health Center',
                'zone': 'Zone C',
                'ward_number': 10,
                'total_beds': 100,
                'available_beds': 28,
                'icu_beds': 10,
                'available_icu_beds': 3,
                'ventilators': 5,
                'available_ventilators': 2
            }
        ]
        
        for h_data in hospitals_data:
            hospital = Hospital(**h_data)
            db.session.add(hospital)
        
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)