import flet as ft
import flet
from pymongo import MongoClient
from cryptography.fernet import Fernet
import random
import hashlib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import cv2
from PIL import Image
import gridfs
from pyfingerprint.pyfingerprint import PyFingerprint

# Database Setup
client = MongoClient("mongodb+srv://User-devwithme:user-devwithme@api-checkup.it4iz.mongodb.net/?retryWrites=true&w=majority")
db = client['officers_Db']
collection = db['officers_database']
File_store_Segment = gridfs.GridFS(db)

# Encryption Setup
key = b'_d9SNtBvMGuEEV2vcC_FfbHzw2BSY9SQzdpNCNtEhXI='
cipher_suite = Fernet(key)

# Global Variables
otp_storage = {}
is_Email_verified = False
officer_id = 0
Photo_Id = None
fingerprint_data = None
uploaded_photo = None

def encrypt_data(data):
    """
    Encrypts the given data using Fernet symmetric encryption.
    """
    if isinstance(data, str):
        data = data.encode()  # Convert string to bytes
    elif isinstance(data, list):
        data = bytes(data)  # Convert list of integers to bytes
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def generate_otp():
    return str(random.randint(100000, 999999))

def send_verification_email(receiver_email, otp):
    try:
        sender_email = "dipayansardar477@gmail.com"
        sender_password = "issq ubqn uipo zfrf"
        subject = "Email Verification"
        body = f"Your OTP for verification is: {otp}\nPlease enter this OTP to verify your email."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def send_registration_confirmation(receiver_email, officer_id,name):
    try:
        sender_email = "dipayansardar477@gmail.com"
        sender_password = "issq ubqn uipo zfrf"
        subject = "Registration Confirmation"
        body = f"Hello {name} your registration for polling officer has been successful\n\n Please don't share this id to anyone,Instruction provided earlier to you must be follow accordingly\n\n your registration Id/Poling Id is {officer_id}"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def generate_officer_id(email, mobile_number):
    username = email.split('@')[0]
    cleaned_mobile_number = re.sub(r'\D', '', mobile_number)
    combined_data = f"{username}_{cleaned_mobile_number}"
    hash_object = hashlib.sha256(combined_data.encode())
    return hash_object.hexdigest()[:8].upper()

def capture_photo():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    if ret:
        while True:
            ret, frame = cap.read()
            if not ret:
                return

            # Display the frame
            cv2.imshow("Capture Photo", frame)

            # Check for key press
            key = cv2.waitKey(1)
            if key == ord('c'):  # Press 'c' to capture
                global uploaded_photo
                uploaded_photo = "captured_photo.jpg"
                global Photo_Id
                Photo_Id=1
                cv2.imwrite(uploaded_photo, frame)
                cv2.destroyAllWindows()
                return("captured_photo.jpg")
                # break               
        
    else:
        cap.release()
        return None
    # Save the captured image temporarily
    


def submit(name, address, email, mobile_number):
    global officer_id, fingerprint_data, Photo_Id, is_Email_verified

    
    if not name or not address or not email or not mobile_number :
        return( "Please fill in all fields (Name, Address, Email, Mobile Number).")
        

    # Step 2: Validate Email Format
    if not is_valid_email(email):
        return( "Invalid email format. Please enter a valid email.")
       
 
    # Step 3: Verify OTP
    if not is_Email_verified:
        return( "Please verify your email with OTP first.")
        

    # Step 4: Validate Fingerprint Data
    if not fingerprint_data:
        return( "Please capture your fingerprint.")
        

    # Step 5: Validate Photo Capture
    if Photo_Id==None :
        return ("Please capture your photo.")
        

    encrypted_name = encrypt_data(name)
    encrypted_address = encrypt_data(address)
    encrypted_email = encrypt_data(email)
    encrypted_mobile_number = encrypt_data(mobile_number)
    encrypted_fingerprint = encrypt_data(fingerprint_data)

    officer_id = generate_officer_id(email, mobile_number)

    with open(uploaded_photo, 'rb') as f:
        Photo_Id = File_store_Segment.put(f, filename=uploaded_photo)

    officer_data = {
        'name': encrypted_name,
        'address': encrypted_address,
        'email': encrypted_email,
        'mobile_number': encrypted_mobile_number,
        'fingerprint': encrypted_fingerprint,
        'photo': Photo_Id,
        'officer_id': officer_id
    }

    try:
        if collection.find_one({'email': encrypted_email}):
            return("Email already exists. Please use a different email.")
        else:
            collection.insert_one(officer_data)
            send_registration_confirmation(email, officer_id,name)
            return f"Officer registered successfully! "
    except Exception as e:
        return f"Database error: {e}"

def main(page: ft.Page):
    page.title = "Officer Registration"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Input Fields
    name_field = ft.TextField(label="Name", width=300)
    address_field = ft.TextField(label="Address", width=300)
    email_field = ft.TextField(label="Email", width=300)
    mobile_field = ft.TextField(label="Mobile Number", width=300)

    otp_field = ft.TextField(label="Enter OTP", width=300, visible=False)
    photo_preview = ft.Image(width=150, height=150)

    global is_Email_verified

    def show_popup(message):
        dialog = ft.AlertDialog(
            title=ft.Text("Notification"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: close_popup(dialog))]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_popup(dialog):
        dialog.open = False
        page.update()

    def send_otp(e):
        global otp_storage
        if not is_valid_email(email_field.value):
            show_popup("Invalid email address.")
            return

        otp = generate_otp()
        otp_storage[email_field.value] = otp
        if send_verification_email(email_field.value, otp):
            otp_field.visible = True
            verify_otp_button.visible=True
            show_popup("OTP sent to email.")
        else:
            show_popup("Failed to send OTP.")
        page.update()

    def verify_otp(e):
        global is_Email_verified
        entered_otp = otp_field.value
        if otp_storage.get(email_field.value) == entered_otp:
            is_Email_verified = True
            show_popup("Email verified successfully!")
            otp_field.visible = False
            verify_otp_button.visible=False
            send_otp_button.visible=False
        else:
            is_Email_verified = False
            show_popup("Invalid OTP.")
        page.update()

    def on_photo_capture(e):
        global uploaded_photo
        photo_path = capture_photo()
        if photo_path:
            uploaded_photo = photo_path
            photo_preview.src = photo_path
            show_popup("Photo captured successfully!")
            page.update()
        else:
            show_popup("Photo capture failed.")

    def fingerprintCollect(e):
        selected_port="COM3"
        global fingerprint_data
        try:
            f = PyFingerprint(selected_port, 57600, 0xFFFFFFFF, 0x00000000)
            if not f.verifyPassword():
                raise ValueError("The given fingerprint sensor password is incorrect!")
        except Exception as e:
            print(f"Error initializing fingerprint scanner: {e}")
            errorMsg = f"Error initializing fingerprint scanner\n Please check your sensor settings.\n Error: {e}"
            show_popup(f"Error\n{errorMsg}")
            return

        try:
            if fingerprint_data ==None:
                show_popup("Place your finger on the scanner...")

            while not f.readImage():
                pass
            f.convertImage(0x01)
            
            fingerprint_data = f.downloadCharacteristics()
            
            print("Fingerprint captured successfully!")
            show_popup("Fingerprint captured successfully!")
            # disconnect_fingerprint_sensor(f)
            
            return
        except Exception as e:
            print(f"Error capturing or storing fingerprint: {e}")
            show_popup(f"Error capturing or storing fingerprint: {e}")
            return
        
    def on_submit(e):
        response = submit(
            name_field.value,
            address_field.value,
            email_field.value,
            mobile_field.value
        )
        show_popup(response)

    send_otp_button = ft.ElevatedButton("Send OTP", on_click=send_otp, width=300)
    verify_otp_button = ft.ElevatedButton("Verify OTP", on_click=verify_otp, width=300, visible=False)
    photo_button = ft.ElevatedButton("Capture Photo", on_click=on_photo_capture, width=300)
    submit_button = ft.ElevatedButton("Submit", on_click=on_submit, width=300)
    add_fingerprint_button = ft.ElevatedButton("Add Fingerprint",on_click=fingerprintCollect,width=300)
    page.add(
        
            ft.Column([
                ft.Text("Officer Registration", size=24, weight="bold"),
                name_field,
                address_field,
                email_field,
                send_otp_button,
                otp_field,
                verify_otp_button,
                mobile_field,
                photo_button,
                photo_preview,
                add_fingerprint_button,
                submit_button,
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        )

ft.app(target=main)
