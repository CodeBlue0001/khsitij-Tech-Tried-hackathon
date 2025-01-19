from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from pymongo import MongoClient
import gridfs
from bson import ObjectId
import io
from cryptography.fernet import Fernet

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Secret key for session encryption

# MongoDB connection
client = MongoClient("mongodb+srv://User-devwithme:user-devwithme@api-checkup.it4iz.mongodb.net/?retryWrites=true&w=majority")
db = client['website_db']
collection = db['web_server']
fs = gridfs.GridFS(db)

key = b'_d9SNtBvMGuEEV2vcC_FfbHzw2BSY9SQzdpNCNtEhXI='
cipher_suite = Fernet(key)

data_store = {}

def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using Fernet symmetric encryption.
    """
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    try:
        return decrypted_data.decode()  # Convert bytes back to string if possible
    except Exception as e:
        print("Error decoding decrypted data:", e)
        return list(encrypted_data)


def get_image_from_gridfs(photo_file_id):
    """
    Retrieve an image file from GridFS using its ObjectId.
    """
    try:
        image_file = fs.get(ObjectId(photo_file_id))
        return image_file.read()
    except Exception as e:
        print(f"Error retrieving image: {e}")
        return None


def get_voter_data(voter_id):
    """
    Retrieve voter data by voter_id from MongoDB.
    """
    try:
        voter = collection.find_one({"voter_id": voter_id})
        print(voter)
        if voter:
            # Retrieve image if photo_file_id exists
            image_data = None
            
            image_data = get_image_from_gridfs(voter["photo_file_id"])
            return {
                "id": str(voter["_id"]),
                "name": voter["name"],
                "voter_id": voter["voter_id"],
                "state": voter["state"],
                "district": voter["district"],
                "constitution": voter["constitution"],
                "gender": voter["gender"],
                "photo": image_data,
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving voter data: {e}")
        return None


@app.route("/", methods=["POST"])
def handle_redirect():
   
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # global user_id
    # Extract data from the request
    USER_ID = data.get("id")
    USER_EMAIL = data.get("email")
    # email=decrypt_data(encrypted_email)
    # Store data in Flask session
    session['USER_ID'] = USER_ID
    session['USER_EMAIL'] = USER_EMAIL
    # user_id=decrypt_data(encrypted_user_id)

    if not USER_ID or not USER_EMAIL:
        return jsonify({"error": "Missing id or email"}), 400

    # Store data temporarily
    data_store["id"] =USER_ID
    data_store["email"] = USER_EMAIL

    # # Generate a redirect URL to the search page
    # redirect_url = f"http://127.0.0.1:5000/search"
    # return jsonify({"redirect_url": redirect_url}), 200
    return redirect(url_for('search_page'))


@app.route("/search_page", methods=["GET", "POST"])
def search_page():
    # print("Session data:", dict(session))
    # session_data = dict(session) # Extracting values 
    # user_email = session_data['USER_EMAIL'] 
    # user_id = session_data['USER_ID'] 
    # print('User Email:', user_email) # Output: dipsardar554@gmail.com 
    # print('User ID:', user_id)
    
    # if not user_id and not user_email:
    #     return "User ID or Email not provided", 400
            
    # print("Session data retrieved:", user_id, user_email)

    # Handle GET request to show the search page
    if request.method == "GET":
        return render_template("search.html")

    # Handle POST request to process voter data
    if request.method == "POST":
        voter_id = request.form.get("voter_id")
        print(voter_id)
        voter_data = get_voter_data(voter_id)

        if voter_data:
            # Return voter data as JSON for the frontend to process
            return jsonify(voter_data)
        else:
            return jsonify({"error": "Voter not found"}), 404

    return render_template("search.html")

@app.route("/image/<photo_file_id>")
def serve_image(photo_file_id):
    """
    Serve the image from GridFS by photo_file_id.
    """
    image_data = get_image_from_gridfs(photo_file_id)
    if image_data:
        return send_file(
            io.BytesIO(image_data),
            mimetype="image/jpeg",
            as_attachment=False,
            download_name=f"{photo_file_id}.jpg",
        )
    return "Image not found", 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
