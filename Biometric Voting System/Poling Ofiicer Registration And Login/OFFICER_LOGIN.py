import flet as ft
from pymongo import MongoClient
from cryptography.fernet import Fernet
from pyfingerprint.pyfingerprint import PyFingerprint
import random
import cv2
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gridfs
from bson import ObjectId

# MongoDB client and encryption setup
client = MongoClient("mongodb+srv://User-devwithme:user-devwithme@api-checkup.it4iz.mongodb.net/?retryWrites=true&w=majority")
db = client['officers_Db']
collection = db['officers_database']
File_store_Segment = gridfs.GridFS(db)

# Encryption setup
key = b'_d9SNtBvMGuEEV2vcC_FfbHzw2BSY9SQzdpNCNtEhXI='
cipher_suite = Fernet(key)

# global veriables
fingerprint_data = None
polling_id = ""
# uploaded_photo = None
season_data = None
otp_storage = {}


def make_json_serializable(data):
    """Recursively convert non-serializable types to serializable types."""
    if isinstance(data, ObjectId):
        return str(data)  # Convert ObjectId to string
    elif isinstance(data, bytes):
        return data.decode()  # Convert bytes to string
    elif isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    else:
        return data
    
def redirect(data):
    import webbrowser
    import requests

    update_url = "http://127.0.0.1:5000/search_page"

    if not data:
        print("Error: No data provided for the POST request.")
        return

    try:
        print(f"Sending POST request with data: {data}")
        response = requests.post("http://127.0.0.1:5000", json=data, timeout=10)

        if response.status_code == 200:
            print("Redirecting to search page...")
            webbrowser.open_new_tab(update_url)
        else:
            print(f"POST request failed with status code: {response.status_code}")
            print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the POST request: {e}")



def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using Fernet symmetric encryption.
    """
    decrypted_data = cipher_suite.decrypt(encrypted_data)    
    
    try:
        return decrypted_data.decode()  # Convert bytes back to string if possible
    except Exception as e:
        print("Error decoding decrypted data:", e)
        return list(encrypted_data)  # Convert bytes back to list of integers if string conversion fails

def decrypt_fingerprint(encrypted_fingerprint):
    try: 
        decrypted_data = cipher_suite.decrypt(encrypted_fingerprint) # Try to decode as UTF-8 
        try: 
            return decrypted_data.decode('utf-8')
        except UnicodeDecodeError: # Handle decoding error, return raw bytes or handle as needed 
            return decrypted_data 
    except Exception as e: 
        print(f"Error decrypting data: {e}") 
        return None
    
def generate_otp():
        return str(random.randint(100000, 999999))

def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

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

# Flet page
def main(page: ft.Page):
    page.title = "Polling Officer Registration"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # Dummy data
    
    # Functions for OTP generation, email verification, etc.
    

    
    # Widgets for page layout
    polling_id_entry=ft.TextField(label="Enter Polling ID", width=300)    
    email_field = ft.TextField(label="Enter Email", width=300)
    # otp_label = ft.Text("Enter OTP", visible=False)
    otp_field = ft.TextField(label="Enter OTP",visible=False,width=300)
    verify_otp_button = ft.ElevatedButton("Verify OTP", visible=False,width=300)
    verify_ID_button = ft.ElevatedButton("Verify Email and poling Id")
    # result_label = ft.Text("")

    # Function to verify email
    def verify_email(e):
        global polling_id
        polling_id=polling_id_entry.value
        if not polling_id:
            show_popup("Please enter a polling ID.")
            return
        email = email_field.value.strip()
        
        if not email:
            show_popup("Please enter your email.")
            return
        
        if not email or not is_valid_email(email):
            # page.add(ft.Text("Invalid email. Please enter a valid email."))
            show_popup("Invalid email. Please enter a valid email.")
            return
        
        global season_data
        season_data=collection.find_one({"officer_id":polling_id})
        if not season_data:
            show_popup("Polling ID not found.")
            return
        encrypted_email=season_data['email']
        decrypted_email=decrypt_data(encrypted_email)
       

        if decrypted_email==email and polling_id==season_data['officer_id']:
            # page.add(ft.Text("Polling ID verified successfully!"))
            show_popup("Polling ID verified successfully!")            
            send_otp(e)
        else:            
            show_popup("Poling ID not verified with the email")
        

    # Function to verify OTP
    def verify_otp(e):
        email = email_field.value.strip()
        entered_otp = otp_field.value.strip()

        if entered_otp == otp_storage.get(email):
            
            show_popup("OTP verified successfully!")
        else:
            show_popup("Invalid OTP. Please try again.")

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
            verify_ID_button.visible=False
            biometric_button.visible=True
            # send_otp_button.visible=False
        else:
            is_Email_verified = False
            show_popup("Invalid OTP.")
        page.update()

    def match_fingerprint(e):
        global season_data
        encrypted_fingerprint =season_data['fingerprint']
        template=decrypt_fingerprint(encrypted_fingerprint)

        port="COM3"
        if port == 'Select a scanner port':
            # messagebox.showerror("Error", "Please select connected port.")
            show_popup("Please select connected port.")
        try:
            # Initialize the fingerprint sensor
            f = PyFingerprint(port, 57600)

            # Check if the fingerprint sensor is connected
            if not f.verifyPassword():
                show_popup("Fingerprint sensor not connected or password incorrect.")
                return

            # Upload the template to the fingerprint sensor
            f.uploadCharacteristics(0x01, template)

            # Capture the first fingerprint image
            show_popup("Place your finger on the sensor...")
            while not f.readImage():
                pass
            
            try:
                # Preprocess the image
                f.convertImage(0x02)
            except Exception as e:
                 if str(e) == 'The image contains too few feature points':
                     show_popup("Fingerprint quality is too low. Please try again.")

            # Extract features from the image
            new_template = f.downloadCharacteristics(0x02)

            # Compare the templates
            score = f.compareCharacteristics()
            if score > 40:
                show_popup("Identitiy Verified!\n redirecting to webserver")
                
                Data={
                    "id":polling_id,
                    "email":decrypt_data(season_data['email']),
                    # "season":decrypt_data(season_data['season']),
                    # "fingerprint":decrypt_data(season_data['fingerprint'])
                }
                Data=make_json_serializable(Data)
                print("json serializable",Data)
                redirect(Data)
            else:
                show_popup("Fingerprints do not match.")

        except Exception as e:
            show_popup("Operation failed!")
            
            print("Exception message: " + str(e))
            exit(1)

    # UI elements for email verification
    verify_ID_button.on_click = verify_email
    verify_otp_button.on_click = verify_otp

    # UI elements for fingerprint verification
    biometric_button = ft.ElevatedButton("Verify Biometric",visible=False
    ,on_click=match_fingerprint)

    # Layout structure
    page.add(
         ft.Column([
              ft.Text("officer login",size=24,weight="bold"),
                polling_id_entry,
                email_field,
                verify_ID_button,
                otp_field,                
                verify_otp_button,
                biometric_button,
                        
         ])
        
    )

ft.app(target=main)
