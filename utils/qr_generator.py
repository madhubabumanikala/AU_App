import qrcode
import os
from datetime import datetime
from models.event import EventRegistration
from flask import current_app

def generate_qr_code(registration):
    """Generate QR code for event registration"""
    if not registration:
        return None
    
    # Create QR code data
    qr_data = {
        'registration_id': registration.id,
        'student_id': registration.student_id,
        'event_id': registration.event_id,
        'student_name': registration.student.full_name,
        'event_title': registration.event.title,
        'event_date': registration.event.date.strftime('%Y-%m-%d'),
        'event_time': registration.event.time.strftime('%H:%M'),
        'registration_date': registration.registration_date.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Convert to string
    qr_string = f"AU-EVENT-REG-{registration.id}|{registration.student_id}|{registration.event_id}|{registration.registration_date.strftime('%Y%m%d%H%M%S')}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    filename = f"qr_registration_{registration.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    qr_folder = current_app.config['QR_CODE_FOLDER']
    os.makedirs(qr_folder, exist_ok=True)
    qr_path = os.path.join(qr_folder, filename)
    qr_img.save(qr_path)
    
    # Return relative path for database storage
    return os.path.join('uploads', 'qrcodes', filename).replace('\\', '/')

def validate_qr_code(qr_string):
    """Validate QR code data and return registration info"""
    try:
        if not qr_string.startswith('AU-EVENT-REG-'):
            return None, 'Invalid QR code format'
        
        parts = qr_string.split('|')
        if len(parts) != 4:
            return None, 'Invalid QR code structure'
        
        registration_id = int(parts[0].replace('AU-EVENT-REG-', ''))
        student_id = int(parts[1])
        event_id = int(parts[2])
        
        # Find registration
        registration = EventRegistration.query.get(registration_id)
        
        if not registration:
            return None, 'Registration not found'
        
        if registration.student_id != student_id or registration.event_id != event_id:
            return None, 'QR code data mismatch'
        
        return registration, 'Valid QR code'
    
    except Exception as e:
        return None, f'Error validating QR code: {str(e)}'
