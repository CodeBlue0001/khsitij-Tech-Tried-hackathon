
# Full code rewrite with "Select Constitution" combobox, gender selection, and layout adjustment

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pymongo
from pyfingerprint.pyfingerprint import PyFingerprint
import cv2
import gridfs
from PIL import Image, ImageTk
import state_districts_library as SDL
import constitution_list as lok_sava_list
import random
import string
import os
import serial.tools.list_ports
from cryptography.fernet import Fernet
from tkcalendar import DateEntry
from tkcalendar import DateEntry
from datetime import datetime

# Connect to the database
# client = MongoClient("mongodb+srv://User-devwithme:user-devwithme@api-checkup.it4iz.mongodb.net/?retryWrites=true&w=majority")
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://User-devwithme:user-devwithme@api-checkup.it4iz.mongodb.net/?retryWrites=true&w=majority")
client = pymongo.MongoClient(mongo_uri)
web_db=client['website_db']
photo_segment=gridfs.GridFS(web_db)

static_db=client['voteing_system']
user_collection=static_db['users']



fingerprint_data = None
Voter_ID=None

key=b'x_uSZbEIVAF2aH11cUM2xtlJIjUa6aDaihVx07ytlv0='
cipher_suite = Fernet(key)

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

def disconnect_fingerprint_sensor(f):
    # Disconnect the fingerprint sensor
    print("Disconnecting fingerprint sensor...")
    f.close()  # Close the connection to the sensor
    print("Fingerprint sensor disconnected.")




root = tk.Tk()


root.geometry("800x700")  # Adjusted for better layout
root.configure(bg='#4E9BE7')
root.resizable(False,False)
# Load the logo image
try:
    logo_image = Image.open("Top_icon.png")
    logo_image = ImageTk.PhotoImage(logo_image)
    root.iconphoto(True, logo_image)
    
except Exception as e:
    print("Error loading logo image:", e)

# Set the window title
root.title("Voter Registration")

# Districts dictionary
districts_dict = {
    'Assam': SDL.assam_districts,
    'Andaman And Nicobar':SDL.andaman_district,
    'Arunachal Pradesh': SDL.arunachal_pradesh_districts,
    'Andhra Pradesh': SDL.andhra_pradesh_districts,
    'Bihar': SDL.bihar_districts,
    'Chandigarh':SDL.chandigarh_districts,
    'Chhattisgarh':SDL.chhattisgarh_districts,
    'Dadra and Nagar Haveli':SDL.dadra_and_nagar_haveli_districts,
    'Delhi':SDL.delhi_districts,

    'Goa': SDL.goa_districts,
    'Gujarat':SDL.gujarat_districts,
    'Haryana': SDL.haryana_districts,
    'Himachal Pradesh': SDL.himachal_pradesh_districts,
    'Jammu and Kashmir':SDL.jammu_kashmir_districts,
    'Jharkhand': SDL.jharkhand_districts,

    'Karnataka': SDL.karnataka_districts,
    'Kerala': SDL.kerala_districts,
    'Ladakh': SDL.ladakh_districts,
    'Lakshadweep': SDL.lakshadweep_districts,
    'Madhya Pradesh':SDL.madhya_pradesh_districts,
    'Maharashtra': SDL.maharashtra_districts,
    'Meghalaya': SDL.meghalaya_districts,
    'Mizoram': SDL.mizoram_districts,
    'Nagaland': SDL.nagaland_districts,
    'Odisha': SDL.odisha_districts,
    'Punjab':SDL.punjab_districts,
    'Puducherry':SDL.puduchery_districts,
    'Rajasthan': SDL.rajasthan_districts,
    'Sikkim': SDL.sikkim_districts,
    'Tamil Nadu': SDL.tamil_nadu_districts,
    'Telangana': SDL.telangana_districts,
    'Tripura': SDL.tripura_districts,
    'Uttar Pradesh':SDL.uttar_pradesh_districts,
    'Uttarakhand': SDL.uttarakhand_districts,
    'West Bengal': SDL.west_bengal_districts,
}

# Constitutions dictionary
constitutions_dict = {
    'Assam': lok_sava_list.assam_lok_sabha_centres,
    'Andaman And Nicobar':lok_sava_list.andaman_nicobar_island_lok_sabha_centers,
    'Arunachal Pradesh': lok_sava_list.arunachal_pradesh_lok_sabha_centres,
    'Andhra Pradesh': lok_sava_list.andhra_pradesh_lok_sabha_centers,
    'Bihar': lok_sava_list.bihar_lok_sabha_centers,
    'Chandigarh':lok_sava_list.chandigarh_lok_sabha_centers,
    'Chhattisgarh':lok_sava_list.chhattisgarh_lok_sabha_centers,
    'Dadra and Nagar Haveli':lok_sava_list.Dadra_nagar_haveli_and_daman_and_diu_lok_sabha_centers,
    'Delhi':lok_sava_list.Delhi_lok_sabha_centers,

    'Goa': lok_sava_list.goa_lok_sabha_centers,
    'Gujarat': lok_sava_list.gujarat_lok_sabha_centers,
    'Haryana': lok_sava_list.haryana_lok_sabha_centers,
    'Himachal Pradesh': lok_sava_list.himachal_pradesh_lok_sabha_centers,
    'Jammu and Kashmir':lok_sava_list.jammu_and_kashmir_lok_sabha_centers,
    'Jharkhand': lok_sava_list.jharkhand_lok_sabha_centers,

    'Karnataka': lok_sava_list.karnataka_lok_sabha_centers,
    'Kerala': lok_sava_list.kerala_lok_sabha_centers,
    'Ladakh': lok_sava_list.ladakh_lok_sabha_centers,
    'Lakshadweep': lok_sava_list.lakshadeep_lok_sabha_centers,
    'Madhya Pradesh':lok_sava_list.madhya_pradesh_lok_sabha_centres,
    'Maharashtra': lok_sava_list.maharashtra_lok_sabha_centers,
    'Meghalaya': lok_sava_list.meghalaya_lok_sabha_centers,
    'Mizoram': lok_sava_list.mizoram_lok_sabha_centers,
    'Nagaland': lok_sava_list.nagaland_lok_sabha_centers,
    'Odisha': lok_sava_list.odisha_lok_sabha_centers,
    'Punjab':lok_sava_list.punjab_lok_sabha_centers,
    'Puducherry':lok_sava_list.puducherry_lok_sabha_centres,
    'Rajasthan': lok_sava_list.rajasthan_lok_sabha_centers,
    'Sikkim': lok_sava_list.sikim_lok_sabha_centers,
    'Tamil Nadu': lok_sava_list.tamil_nadu_lok_sabha_centers,
    'Telangana': lok_sava_list.telengana_lok_sabha_centres,
    'Tripura': lok_sava_list.tripura_lok_sabha_centres,
    'Uttar Pradesh': lok_sava_list.uttar_pradesh_lok_sabha_centers,
    'Uttarakhand': lok_sava_list.uttarakhand_lok_sabha_centres,
    'West Bengal': lok_sava_list.west_bengal_lok_sabha_centers,
    # 'Tamilnadu': lok_sava_list.tamil_nadu_lok_sabha_centers
  

}

# Function to update districts based on selected state
def update_districts(event):
    selected_state = stateSelectbox.get()
    if selected_state in districts_dict:
        districtSelectbox.configure(values=districts_dict[selected_state])
        constitutionSelectbox.configure(values=constitutions_dict[selected_state])
        districtSelectbox.set('Select a district')

# Function to update constitutions based on selected district
def update_constitutions(event):
    selected_state = stateSelectbox.get()
    if selected_state in constitutions_dict:
        constitutionSelectbox.configure(values=constitutions_dict[selected_state])
        constitutionSelectbox.set('Select a constitution')


# Generate a key for encryption (store this securely in production)

# Modify the submit_details function to include the photo
def submit_details():
    # Set up the database collection
    district = str(districtSelectbox.get())
    district = district.strip().replace(" ", "_").lower() 
    print("Database:", district)
    default_db = client[district]
    collection_name = str(constitutionSelectbox.get())
    default_collection = default_db[collection_name]
    web_server = web_db['web_server']
    File_store_Segment = gridfs.GridFS(default_db)

    global Voter_ID, uploaded_photo
    name_value = name.get()
    voter_id_value = Voter_ID
    state_value = stateSelectbox.get()
    district_value = districtSelectbox.get()
    constitution_value = constitutionSelectbox.get()
    gender_value = genderSelectbox.get()
    date_of_birth_value = DoB.get_date()  # `DateEntry` returns a `datetime.date` object

    # Convert date_of_birth_value to a string
    date_of_birth_str = date_of_birth_value.isoformat()  # Alternatively: date_of_birth_value.strftime('%Y-%m-%d')

    # Check for empty fields
    if not name_value or state_value == 'Select a state' or district_value == 'Select a district' or \
            constitution_value == 'Select a constitution' or gender_value == 'Select Gender' or \
            fingerprint_data is None or uploaded_photo is None:
        messagebox.showerror("Error", "Please fill all fields and upload a photo.")
        return

    # Store the photo in MongoDB using GridFS
    try:
        with open(uploaded_photo, 'rb') as f:
            file_id = File_store_Segment.put(f, filename=uploaded_photo)
            photo_id=photo_segment.put(f,filename=uploaded_photo)
            print(f"Photo stored in MongoDB with file_id: {file_id}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to store photo in MongoDB: {e}")
        return

    # Encrypt fingerprint data
    encrypted_name=encrypt_data(name_value)
    encrypted_district=encrypt_data(district_value)
    encrypted_constitution=encrypt_data(constitution_value)
    # Fingerprint_Data = encrypt_data(fingerprint_data)

    # Save data to the database
    data = {
        "name": name_value,
        "voter_id": voter_id_value,
        "state": state_value,
        "district": encrypt_data(district_value),
        "constitution": encrypt_data(constitution_value),
        "gender": gender_value,
        "fingerprint_data": fingerprint_data,
        "photo_file_id": file_id,
        "Date_Of_Birth": date_of_birth_str  # Use the string version of the date
    }
    Data_for_website = {
        "name": encrypted_name,
        "voter_id": voter_id_value,
        "state": state_value,
        "district": encrypted_district,
        "constitution": encrypted_constitution,
        "gender": gender_value,
        "photo_file_id": photo_id
    }

    try:
        web_server.insert_one(Data_for_website)
        default_collection.insert_one(data)
        user_collection.insert_one(data)
        messagebox.showinfo("Success", "Voter details submitted successfully!")

        # Reset fields
        name.delete(0, tk.END)
        voter_id_label.config(text="")
        stateSelectbox.set('Select a state')
        districtSelectbox.set('Select a district')
        constitutionSelectbox.set('Select a constitution')
        genderSelectbox.set('Select Gender')
        Voter_ID = None
        uploaded_photo = None
        photo_label.image = None
        photo_label.configure(image=None)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to submit details: {e}")


#generate 
def generate_voter_id():
    try:
        stateName = str(stateSelectbox.get())
        districtName = str(districtSelectbox.get())
 
        if stateName == 'Select a state' or districtName == 'Select a district':
            messagebox.showerror("Error", "Please select both state and district.")
            return
        # Get the first two letters of the state and district, convert to uppercase
        letters1 = stateName[:2].upper()  
        letters2 = districtName[:2].upper()  
        
        digits1 = ''.join(random.choices(string.digits, k=2))  
        digits2 = ''.join(random.choices(string.digits, k=4))  
        
        # Combine to form the voter ID
        voter_id = letters1 + digits1 + letters2 + digits2
        voter_id_label.config(text=voter_id)
        
        global Voter_ID
        Voter_ID = voter_id
        # print("Voter Id", voter_id)
    except Exception as e:
        messagebox.showerror('please select state and district')

# Create and pack the labels and entries*****************************frames***********************************
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)  # Allow main_frame to expand

# Configure rows and columns in main_frame to be flexible
main_frame.grid_rowconfigure(0, weight=1)  # Row 0 (left and right frames)
main_frame.grid_rowconfigure(1, weight=0)  # Row 1 (mid frame)
main_frame.grid_columnconfigure(0, weight=1)  # Column 0 (left frame)
main_frame.grid_columnconfigure(1, weight=1)  # Column 1 (right and mid frames)

# Left frame
left_frame = tk.Frame(main_frame, bg='#2C3E50',height=220)
left_frame.grid(row=0, column=0, sticky='nsew')  # Expand in all directions



# Right frame
right_frame = tk.Frame(main_frame, bg='#2C3E50')
right_frame.grid(row=0, column=1, sticky='nsew') 





# scanner selection ***************************************************
label = tk.Label(right_frame, text="Select Scanner Port", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)

scannerSelectbox = ttk.Combobox(right_frame, state="readonly", font=("Helvetica", 12))
scannerSelectbox.pack(pady=5)
scannerSelectbox.set('Select a scanner port')
# scannerSelectbox.bind("<<ComboboxSelected>>",list_connected_scanners)
# list_connected_scanners() 



def list_connected_scanners():
    ports = serial.tools.list_ports.comports()
    scanner_ports = [port.device for port in ports]
    scannerSelectbox.configure(values=scanner_ports)
    # print("Connected scanners:", scanne r_ports)


list_connected_scanners()
# Connect to the fingerprint sensor
def fingerprintCollect():
    selected_port=scannerSelectbox.get()
    try:
        f = PyFingerprint(selected_port, 57600, 0xFFFFFFFF, 0x00000000)
        if not f.verifyPassword():
            raise ValueError("The given fingerprint sensor password is incorrect!")
    except Exception as e:
        print(f"Error initializing fingerprint scanner: {e}")
        errorMsg = f"Error initializing fingerprint scanner\n Please check your sensor settings.\n Error: {e}"
        messagebox.showerror("Error", errorMsg)
        return

    try:
        print("Place your finger on the scanner...")
        while not f.readImage():
            pass
        f.convertImage(0x01)
        global fingerprint_data
        fingerprint_data = f.downloadCharacteristics()
        # fingerprint_data=encrypt_data(fingerprint_data)
        # print("fingerprint:",fingerprint_data)
        print("Fingerprint captured successfully!")
        messagebox.showinfo("Fingerprint", "Fingerprint captured successfully!")
        disconnect_fingerprint_sensor(f)
        return
    except Exception as e:
        print(f"Error capturing or storing fingerprint: {e}")
        return





# Add this global variable to store the uploaded photo path
uploaded_photo = None

# voter photograph
def capture_photo():
    # Access the camera
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open camera.")
        return
    
    
    # Capture a frame
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image.")
            return

        # Display the frame
        cv2.imshow("Capture Photo", frame)

        # Check for key press
        key = cv2.waitKey(1)
        if key == ord('c'):  # Press 'c' to capture
            cv2.destroyAllWindows()
            break
    
    # Release the camera
    cap.release()

    # Save the captured image temporarily
    global uploaded_photo
    uploaded_photo = "captured_photo.jpg"
    cv2.imwrite(uploaded_photo, frame)

    # Display the captured image in the GUI
    image = Image.open(uploaded_photo)
    image = image.resize((150, 150))  # Resize the image
    photo = ImageTk.PhotoImage(image)
    photo_label.config(image=photo)
    photo_label.image = photo  # Keep a reference to avoid garbage collection
     # Store the photo in MongoDB using GridFS
    
    # try:
    #     with open(uploaded_photo, 'rb') as f:
    #         file_id = File_store_Segment.put(f, filename=uploaded_photo)
    #         print(f"Photo stored in MongoDB with file_id: {file_id}")
    # except Exception as e:
    #     messagebox.showerror("Error", f"Failed to store photo in MongoDB: {e}")
# Set up periodic refreshing
def periodic_refresh():
    list_connected_scanners()
    root.after(5000, periodic_refresh)  # Refresh every 5 seconds

# Start periodic refreshing
periodic_refresh() 

# def check():
#     date_of_Birth=DoB.get_date()
#     print(date_of_Birth)

#*******************************************************************************
label = tk.Label(left_frame, text="Enter your name", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)
name = tk.Entry(left_frame, font=("Helvetica", 14), width=22)

name.pack(pady=5)

label=tk.Label(left_frame ,text="Enter yor date of birth", font=("Helvetica", 14),bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)
DoB=DateEntry(left_frame, font=("Helvetica", 14), width=15,date_pattern="YYYY-MM-DD")
DoB.pack(pady=5)

# dob_check=tk.Button(left_frame, text="check", font=("Helvetica", 12), command=check)

# dob_check.pack(pady=5)

# ***************************

# Add this section to the GUI layout
# label = tk.Label(left_frame, text="Upload Photo", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
# label.pack(pady=5)

# upload_button = tk.Button(left_frame, text="Upload Photo", font=("Helvetica", 12), command=upload_photo)
# upload_button.pack(pady=5)

photo_label = tk.Label(left_frame, bg="#2C3E50")
photo_label.pack(pady=5)



# Add this section to the GUI layout
camera_button = tk.Button(left_frame, text="Take Photo", font=("Helvetica", 12), command=capture_photo)
camera_button.pack(pady=5)
# ************************************

label = tk.Label(left_frame, text="Select your state", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)
stateSelectbox = ttk.Combobox(left_frame, values=list(districts_dict.keys()), state="readonly", font=("Helvetica", 12))
stateSelectbox.pack(pady=5)
stateSelectbox.set('Select a state')
stateSelectbox.bind("<<ComboboxSelected>>", update_districts)

label = tk.Label(right_frame, text="Select district", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)
districtSelectbox = ttk.Combobox(right_frame, state="readonly", font=("Helvetica", 12))
districtSelectbox.pack(pady=5)
districtSelectbox.set('Select a district')
districtSelectbox.bind("<<ComboboxSelected>>", update_constitutions)

label = tk.Label(right_frame, text="Select Constitution", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)
constitutionSelectbox = ttk.Combobox(right_frame, state="readonly", font=("Helvetica", 12))
constitutionSelectbox.pack(pady=5)
constitutionSelectbox.set('Select a constitution')

# voter id 
label = tk.Label(right_frame, text="Your Voter ID", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)

# generated_voterId = generate_voter_id()
get_Voter_Id=tk.Button(right_frame, text="Get Voter ID",font=("Helvetica", 12), command=lambda: generate_voter_id())

get_Voter_Id.pack(pady=5)
voter_id_label = tk.Label(right_frame,  font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
voter_id_label.pack(pady=5)



label = tk.Label(left_frame, text="Select Gender", font=("Helvetica", 14), bg="#2C3E50", fg="#BDC3C7")
label.pack(pady=5)
genderSelectbox = ttk.Combobox(left_frame, values=["Male", "Female", "Other"], state="readonly", font=("Helvetica", 12))
genderSelectbox.pack(pady=5)
genderSelectbox.set('Select Gender')

# Add buttons
add_fingerprint_button = tk.Button( right_frame,text="Add Fingerprint", bg="light blue", fg="black", font=("Helvetica", 12), command=fingerprintCollect)
add_fingerprint_button.pack(pady=5)

submit_button = tk.Button(right_frame,text="Submit", bg="light green", fg="black", font=("Helvetica", 12), command=submit_details)

submit_button.pack(pady=5, anchor='center',side="left")

root.mainloop()
