"""
SAKSHI Database Initialization Script
Creates database schema and populates with realistic sample data
"""

from app import app, db
from models import *
from datetime import datetime, timedelta
import random
import json

def init_database():
    """Initialize database with sample data"""
    
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("✓ Database schema created")
        
        # 1. Create Hospitals
        hospitals = create_hospitals()
        print(f"✓ Created {len(hospitals)} hospitals")
        
        # 2. Create Users (Admin, Doctors, Patients)
        admin, doctors, patients = create_users(hospitals)
        print(f"✓ Created 1 admin, {len(doctors)} doctors, {len(patients)} patients")
        
        # 3. Create Appointments
        appointments = create_appointments(patients, doctors)
        print(f"✓ Created {len(appointments)} appointments")
        
        # 4. Create Medical Records
        records = create_medical_records(patients, doctors, appointments)
        print(f"✓ Created {len(records)} medical records")
        
        # 5. Create Disease Outbreaks
        outbreaks = create_disease_outbreaks()
        print(f"✓ Created {len(outbreaks)} disease outbreaks")
        
        # 6. Create Equipment
        equipment = create_equipment(hospitals)
        print(f"✓ Created {len(equipment)} equipment entries")
        
        # 7. Create Medicine Stock
        medicines = create_medicine_stock(hospitals)
        print(f"✓ Created {len(medicines)} medicine stock entries")
        
        # 8. Create Vaccination Campaigns
        campaigns = create_vaccination_campaigns()
        print(f"✓ Created {len(campaigns)} vaccination campaigns")
        
        # 9. Create Health Alerts
        alerts = create_health_alerts()
        print(f"✓ Created {len(alerts)} health alerts")
        
        # 10. Create Health Metrics
        metrics = create_health_metrics()
        print(f"✓ Created {len(metrics)} health metric entries")
        
        db.session.commit()
        print("\n✅ Database initialization completed successfully!")
        print(f"\n🔑 Admin Login Credentials:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"\n🔑 Sample Doctor Login:")
        print(f"   Username: dr.sharma")
        print(f"   Password: doctor123")
        print(f"\n🔑 Sample Patient Login:")
        print(f"   Username: patient001")
        print(f"   Password: patient123")

def create_hospitals():
    """Create sample hospitals"""
    hospitals_data = [
        {
            'name': 'Civil Hospital Solapur',
            'hospital_type': 'District Hospital',
            'zone': 'Zone A',
            'ward_number': 1,
            'phone': '0217-2655500',
            'email': 'civil@solapur.gov.in',
            'address': 'Jule Solapur Road, Solapur',
            'total_beds': 250,
            'available_beds': 62,
            'icu_beds': 25,
            'available_icu_beds': 8,
            'ventilators': 12,
            'available_ventilators': 4,
            'ambulance_count': 5
        },
        {
            'name': 'PHC Vijapur',
            'hospital_type': 'Primary Health Center',
            'zone': 'Zone B',
            'ward_number': 15,
            'phone': '0217-2655501',
            'email': 'phc.vijapur@solapur.gov.in',
            'address': 'Vijapur Road, Solapur',
            'total_beds': 50,
            'available_beds': 18,
            'icu_beds': 5,
            'available_icu_beds': 2,
            'ventilators': 2,
            'available_ventilators': 1,
            'ambulance_count': 2
        },
        {
            'name': 'CHC Ashok Chowk',
            'hospital_type': 'Community Health Center',
            'zone': 'Zone C',
            'ward_number': 28,
            'phone': '0217-2655502',
            'email': 'chc.ashok@solapur.gov.in',
            'address': 'Ashok Chowk, Solapur',
            'total_beds': 100,
            'available_beds': 35,
            'icu_beds': 10,
            'available_icu_beds': 4,
            'ventilators': 5,
            'available_ventilators': 2,
            'ambulance_count': 3
        },
        {
            'name': 'Urban Health Center - Zone D',
            'hospital_type': 'Urban Health Center',
            'zone': 'Zone D',
            'ward_number': 42,
            'phone': '0217-2655503',
            'email': 'uhc.zoned@solapur.gov.in',
            'address': 'West Solapur, Solapur',
            'total_beds': 75,
            'available_beds': 22,
            'icu_beds': 8,
            'available_icu_beds': 3,
            'ventilators': 4,
            'available_ventilators': 1,
            'ambulance_count': 2
        },
        {
            'name': 'SMC Maternity Hospital',
            'hospital_type': 'Specialty Hospital',
            'zone': 'Zone E',
            'ward_number': 25,
            'phone': '0217-2655504',
            'email': 'maternity@solapur.gov.in',
            'address': 'Central Solapur, Solapur',
            'total_beds': 120,
            'available_beds': 40,
            'icu_beds': 15,
            'available_icu_beds': 5,
            'ventilators': 8,
            'available_ventilators': 3,
            'ambulance_count': 3
        }
    ]
    
    hospitals = []
    for h_data in hospitals_data:
        hospital = Hospital(**h_data)
        db.session.add(hospital)
        hospitals.append(hospital)
    
    db.session.flush()
    return hospitals

def create_users(hospitals):
    """Create admin, doctors, and patients"""
    
    # Admin
    admin = User(
        username='admin',
        email='admin@solapur.gov.in',
        user_type='admin',
        phone='9876543210'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Doctors
    doctors_data = [
        {
            'username': 'dr.sharma',
            'email': 'sharma@solapur.gov.in',
            'phone': '9876543211',
            'full_name': 'Dr. Rajesh Sharma',
            'registration_number': 'MH-DOC-2015-001',
            'specialization': 'General Medicine',
            'qualification': 'MBBS, MD',
            'hospital_id': hospitals[0].id
        },
        {
            'username': 'dr.patel',
            'email': 'patel@solapur.gov.in',
            'phone': '9876543212',
            'full_name': 'Dr. Priya Patel',
            'registration_number': 'MH-DOC-2016-002',
            'specialization': 'Pediatrics',
            'qualification': 'MBBS, DCH',
            'hospital_id': hospitals[0].id
        },
        {
            'username': 'dr.deshmukh',
            'email': 'deshmukh@solapur.gov.in',
            'phone': '9876543213',
            'full_name': 'Dr. Amit Deshmukh',
            'registration_number': 'MH-DOC-2017-003',
            'specialization': 'Cardiology',
            'qualification': 'MBBS, DM Cardiology',
            'hospital_id': hospitals[1].id
        },
        {
            'username': 'dr.kulkarni',
            'email': 'kulkarni@solapur.gov.in',
            'phone': '9876543214',
            'full_name': 'Dr. Sneha Kulkarni',
            'registration_number': 'MH-DOC-2018-004',
            'specialization': 'Gynecology',
            'qualification': 'MBBS, MS Gynecology',
            'hospital_id': hospitals[4].id
        },
        {
            'username': 'dr.jadhav',
            'email': 'jadhav@solapur.gov.in',
            'phone': '9876543215',
            'full_name': 'Dr. Vikram Jadhav',
            'registration_number': 'MH-DOC-2019-005',
            'specialization': 'Orthopedics',
            'qualification': 'MBBS, MS Orthopedics',
            'hospital_id': hospitals[2].id
        }
    ]
    
    doctors = []
    for d_data in doctors_data:
        user = User(
            username=d_data['username'],
            email=d_data['email'],
            user_type='doctor',
            phone=d_data['phone']
        )
        user.set_password('doctor123')
        db.session.add(user)
        db.session.flush()
        
        doctor = Doctor(
            user_id=user.id,
            full_name=d_data['full_name'],
            registration_number=d_data['registration_number'],
            specialization=d_data['specialization'],
            qualification=d_data['qualification'],
            hospital_id=d_data['hospital_id'],
            consultation_fee=300.0,
            available_days=json.dumps(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        )
        db.session.add(doctor)
        doctors.append(doctor)
    
    # Patients
    zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    patients = []
    for i in range(1, 21):  # Create 20 patients
        user = User(
            username=f'patient{i:03d}',
            email=f'patient{i:03d}@solapur.gov.in',
            user_type='patient',
            phone=f'98765432{16+i}'
        )
        user.set_password('patient123')
        db.session.add(user)
        db.session.flush()
        
        zone = random.choice(zones)
        patient = Patient(
            user_id=user.id,
            qr_code=f'SAKSHI-PAT{i:05d}',
            full_name=f'Patient {i} Name',
            date_of_birth=datetime.now() - timedelta(days=random.randint(7300, 25550)),  # 20-70 years
            gender=random.choice(['Male', 'Female']),
            blood_group=random.choice(blood_groups),
            address=f'{random.randint(1, 500)}, Street {random.randint(1, 50)}, Solapur',
            ward_number=random.randint(1, 50),
            zone=zone,
            aadhar_number=f'{random.randint(100000000000, 999999999999)}',
            emergency_contact_name=f'Emergency Contact {i}',
            emergency_contact_phone=f'98765432{36+i}',
            allergies=json.dumps(['Penicillin'] if i % 5 == 0 else []),
            chronic_conditions=json.dumps(['Diabetes'] if i % 7 == 0 else []),
            current_medications=json.dumps([]),
            vaccination_records=json.dumps([])
        )
        db.session.add(patient)
        patients.append(patient)
    
    db.session.flush()
    return admin, doctors, patients

def create_appointments(patients, doctors):
    """Create sample appointments"""
    appointments = []
    
    # Past appointments
    for i in range(30):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        days_ago = random.randint(1, 90)
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=datetime.now() - timedelta(days=days_ago),
            status='completed',
            appointment_type=random.choice(['consultation', 'follow-up', 'emergency']),
            symptoms=random.choice([
                'Fever and cough',
                'Headache and body pain',
                'Stomach pain',
                'Breathing difficulty',
                'Joint pain'
            ])
        )
        db.session.add(appointment)
        appointments.append(appointment)
    
    # Upcoming appointments
    for i in range(10):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        days_ahead = random.randint(1, 14)
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=datetime.now() + timedelta(days=days_ahead),
            status='scheduled',
            appointment_type='consultation',
            symptoms='Regular checkup',
            is_telemedicine=random.choice([True, False])
        )
        db.session.add(appointment)
        appointments.append(appointment)
    
    db.session.flush()
    return appointments

def create_medical_records(patients, doctors, appointments):
    """Create medical records for completed appointments"""
    records = []
    
    completed_appointments = [a for a in appointments if a.status == 'completed']
    
    diagnoses = [
        'Viral Fever',
        'Common Cold',
        'Gastroenteritis',
        'Hypertension',
        'Diabetes Type 2',
        'Arthritis',
        'Migraine',
        'Urinary Tract Infection'
    ]
    
    for appointment in completed_appointments:
        record = MedicalRecord(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            visit_date=appointment.appointment_date,
            chief_complaint=appointment.symptoms,
            diagnosis=random.choice(diagnoses),
            symptoms=json.dumps(['Fever', 'Cough', 'Fatigue']),
            temperature=round(random.uniform(97.5, 101.5), 1),
            blood_pressure=f'{random.randint(110, 140)}/{random.randint(70, 90)}',
            pulse_rate=random.randint(60, 100),
            oxygen_saturation=round(random.uniform(95.0, 99.0), 1),
            prescription=json.dumps([
                {'medicine': 'Paracetamol', 'dosage': '500mg', 'frequency': 'Twice daily', 'duration': '5 days'},
                {'medicine': 'Vitamin C', 'dosage': '500mg', 'frequency': 'Once daily', 'duration': '7 days'}
            ]),
            treatment_plan='Rest, medication, follow-up after 1 week',
            lab_tests_ordered=json.dumps(['Blood Test', 'X-Ray'] if random.random() > 0.7 else [])
        )
        db.session.add(record)
        records.append(record)
    
    db.session.flush()
    return records

def create_disease_outbreaks():
    """Create disease outbreak records"""
    outbreaks_data = [
        {
            'disease_name': 'Dengue',
            'disease_type': 'communicable',
            'zone': 'Zone A',
            'ward_number': 5,
            'total_cases': 45,
            'active_cases': 12,
            'recovered_cases': 32,
            'death_cases': 1,
            'alert_level': 'warning',
            'outbreak_status': 'active',
            'predicted_cases': 60,
            'risk_score': 6.5
        },
        {
            'disease_name': 'Malaria',
            'disease_type': 'communicable',
            'zone': 'Zone B',
            'ward_number': 18,
            'total_cases': 28,
            'active_cases': 8,
            'recovered_cases': 20,
            'death_cases': 0,
            'alert_level': 'normal',
            'outbreak_status': 'monitoring',
            'predicted_cases': 35,
            'risk_score': 4.2
        },
        {
            'disease_name': 'Typhoid',
            'disease_type': 'communicable',
            'zone': 'Zone C',
            'ward_number': 30,
            'total_cases': 15,
            'active_cases': 5,
            'recovered_cases': 10,
            'death_cases': 0,
            'alert_level': 'normal',
            'outbreak_status': 'monitoring',
            'predicted_cases': 20,
            'risk_score': 3.5
        },
        {
            'disease_name': 'COVID-19',
            'disease_type': 'communicable',
            'zone': 'Zone D',
            'ward_number': 42,
            'total_cases': 8,
            'active_cases': 3,
            'recovered_cases': 5,
            'death_cases': 0,
            'alert_level': 'normal',
            'outbreak_status': 'contained',
            'predicted_cases': 10,
            'risk_score': 2.8
        }
    ]
    
    outbreaks = []
    for o_data in outbreaks_data:
        o_data['first_reported_date'] = datetime.now() - timedelta(days=random.randint(10, 60))
        outbreak = DiseaseOutbreak(**o_data)
        db.session.add(outbreak)
        outbreaks.append(outbreak)
    
    db.session.flush()
    return outbreaks

def create_equipment(hospitals):
    """Create equipment records"""
    equipment_types = [
        ('X-Ray Machine', 'Diagnostic'),
        ('ECG Machine', 'Diagnostic'),
        ('Ultrasound Machine', 'Diagnostic'),
        ('CT Scan', 'Diagnostic'),
        ('Ventilator', 'Life Support'),
        ('Defibrillator', 'Emergency'),
        ('Infusion Pump', 'Treatment'),
        ('Patient Monitor', 'Monitoring'),
        ('Oxygen Concentrator', 'Respiratory'),
        ('Wheelchair', 'Mobility')
    ]
    
    equipment_list = []
    for hospital in hospitals:
        for equip_name, equip_type in equipment_types:
            quantity = random.randint(2, 10)
            working = int(quantity * 0.85)
            
            equipment = Equipment(
                hospital_id=hospital.id,
                equipment_name=equip_name,
                equipment_type=equip_type,
                quantity=quantity,
                working_condition=working,
                under_maintenance=quantity - working,
                out_of_service=0,
                last_maintenance_date=datetime.now() - timedelta(days=random.randint(30, 90)),
                next_maintenance_date=datetime.now() + timedelta(days=random.randint(30, 90)),
                health_status='good' if working >= quantity * 0.8 else 'warning'
            )
            db.session.add(equipment)
            equipment_list.append(equipment)
    
    db.session.flush()
    return equipment_list

def create_medicine_stock(hospitals):
    """Create medicine stock records"""
    medicines_data = [
        ('Paracetamol 500mg', 'Paracetamol', 'Analgesic', 'tablets'),
        ('Amoxicillin 250mg', 'Amoxicillin', 'Antibiotic', 'capsules'),
        ('Metformin 500mg', 'Metformin', 'Antidiabetic', 'tablets'),
        ('Amlodipine 5mg', 'Amlodipine', 'Antihypertensive', 'tablets'),
        ('Omeprazole 20mg', 'Omeprazole', 'Antacid', 'capsules'),
        ('Azithromycin 500mg', 'Azithromycin', 'Antibiotic', 'tablets'),
        ('Cetirizine 10mg', 'Cetirizine', 'Antihistamine', 'tablets'),
        ('Ibuprofen 400mg', 'Ibuprofen', 'Analgesic', 'tablets'),
        ('Insulin Injection', 'Insulin', 'Antidiabetic', 'units'),
        ('ORS Packets', 'Oral Rehydration Salt', 'Rehydration', 'packets')
    ]
    
    medicines = []
    for hospital in hospitals:
        for med_name, generic, category, unit in medicines_data:
            quantity = random.randint(50, 1000)
            reorder = 100
            
            if quantity == 0:
                status = 'critical'
            elif quantity < reorder:
                status = 'low'
            else:
                status = 'adequate'
            
            medicine = MedicineStock(
                hospital_id=hospital.id,
                medicine_name=med_name,
                generic_name=generic,
                category=category,
                quantity=quantity,
                unit=unit,
                reorder_level=reorder,
                batch_number=f'BATCH{random.randint(1000, 9999)}',
                expiry_date=datetime.now() + timedelta(days=random.randint(180, 730)),
                stock_status=status
            )
            db.session.add(medicine)
            medicines.append(medicine)
    
    db.session.flush()
    return medicines

def create_vaccination_campaigns():
    """Create vaccination campaigns"""
    campaigns_data = [
        {
            'campaign_name': 'COVID-19 Booster Drive 2026',
            'vaccine_name': 'Covishield/Covaxin Booster',
            'target_group': 'All adults 18+',
            'start_date': datetime.now() - timedelta(days=10),
            'end_date': datetime.now() + timedelta(days=20),
            'target_population': 150000,
            'vaccinated_count': 82000,
            'status': 'ongoing',
            'zones': json.dumps(['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'])
        },
        {
            'campaign_name': 'Measles-Rubella Vaccination',
            'vaccine_name': 'MR Vaccine',
            'target_group': 'Children 9 months - 5 years',
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now() + timedelta(days=10),
            'target_population': 25000,
            'vaccinated_count': 18500,
            'status': 'ongoing',
            'zones': json.dumps(['Zone A', 'Zone B', 'Zone C'])
        },
        {
            'campaign_name': 'Tetanus Toxoid for Pregnant Women',
            'vaccine_name': 'TT Vaccine',
            'target_group': 'Pregnant women',
            'start_date': datetime.now() - timedelta(days=5),
            'end_date': datetime.now() + timedelta(days=25),
            'target_population': 5000,
            'vaccinated_count': 2800,
            'status': 'ongoing',
            'zones': json.dumps(['Zone D', 'Zone E'])
        }
    ]
    
    campaigns = []
    for c_data in campaigns_data:
        campaign = VaccinationCampaign(**c_data)
        db.session.add(campaign)
        campaigns.append(campaign)
    
    db.session.flush()
    return campaigns

def create_health_alerts():
    """Create health alerts"""
    alerts_data = [
        {
            'alert_type': 'outbreak',
            'title': 'Dengue Alert in Zone A',
            'message': 'Dengue cases have been reported in Ward 5, Zone A. Citizens are advised to eliminate stagnant water and use mosquito repellents.',
            'message_marathi': 'झोन A मधील वॉर्ड 5 मध्ये डेंग्यूची प्रकरणे नोंदवली गेली आहेत. नागरिकांना साचलेले पाणी काढून टाकण्याचा आणि डासांपासून बचाव करण्याचा सल्ला दिला जातो.',
            'severity': 'warning',
            'zones': json.dumps(['Zone A']),
            'ward_numbers': json.dumps([5, 6, 7]),
            'is_active': True
        },
        {
            'alert_type': 'vaccination',
            'title': 'COVID-19 Booster Camp',
            'message': 'Free COVID-19 booster doses are available at all health centers from 9 AM to 5 PM. Please carry your vaccination certificate.',
            'message_marathi': 'सर्व आरोग्य केंद्रांवर सकाळी 9 ते संध्याकाळ 5 पर्यंत मोफत COVID-19 बूस्टर डोस उपलब्ध आहेत. कृपया आपले लसीकरण प्रमाणपत्र सोबत घेऊन या.',
            'severity': 'info',
            'zones': None,
            'ward_numbers': None,
            'is_active': True
        },
        {
            'alert_type': 'precaution',
            'title': 'Monsoon Health Advisory',
            'message': 'With monsoon season approaching, please take precautions against water-borne diseases. Drink boiled water and maintain hygiene.',
            'message_marathi': 'पावसाळी हंगाम जवळ येत असताना, कृपया पाण्यातून होणाऱ्या रोगांपासून सावधगिरी घ्या. उकळलेले पाणी प्या आणि स्वच्छता राखा.',
            'severity': 'info',
            'zones': None,
            'ward_numbers': None,
            'is_active': True
        }
    ]
    
    alerts = []
    for a_data in alerts_data:
        a_data['created_at'] = datetime.now() - timedelta(days=random.randint(1, 7))
        alert = HealthAlert(**a_data)
        db.session.add(alert)
        alerts.append(alert)
    
    db.session.flush()
    return alerts

def create_health_metrics():
    """Create daily health metrics"""
    zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']
    metrics = []
    
    for days_ago in range(30):  # Last 30 days
        date = datetime.now().date() - timedelta(days=days_ago)
        
        for zone in zones:
            metric = HealthMetrics(
                date=date,
                zone=zone,
                ward_number=random.randint(1, 10),
                total_consultations=random.randint(50, 200),
                emergency_visits=random.randint(5, 30),
                new_disease_cases=random.randint(0, 10),
                vaccinations_given=random.randint(10, 100),
                communicable_diseases=random.randint(0, 5),
                non_communicable_diseases=random.randint(2, 15)
            )
            db.session.add(metric)
            metrics.append(metric)
    
    db.session.flush()
    return metrics

if __name__ == '__main__':
    print("🏥 SAKSHI Database Initialization")
    print("=" * 50)
    init_database()