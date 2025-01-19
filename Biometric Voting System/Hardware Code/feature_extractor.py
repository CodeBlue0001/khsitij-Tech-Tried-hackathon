from flask import Flask, request, jsonify
from pymongo import MongoClient
from fingerprint_feature_extractor import FingerprintFeatureExtractor
import numpy as np
import logging
from threading import Lock

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB setup
client = MongoClient("mongodb+srv://User-devwithme:user-devwithme@api-checkup.it4iz.mongodb.net/?retryWrites=true&w=majority&appName=API-checkup")
db = client['voteing_system']
users_collection = db['users']
votes_collection = db['votes']

# Initialize fingerprint extractor
fingerprint_extractor = FingerprintFeatureExtractor()

# Session state
session_state = {"active": False, "user_id": None}
session_lock = Lock()


@app.route('/vote', methods=['POST'])
def vote():
    global session_state

    try:
        data = request.get_json()

        # Validate request
        if not data or not 'fingerprint' in data or 'party' not in data:
            return jsonify({"message": "Invalid request. 'fingerprint' and 'party' are required."}), 500


        fingerprint_data = data['fingerprint']
        print(fingerprint_data)  # Array of fingerprint data
        party = data['party']  # Party name determined by ESP8266

        logging.info("Received fingerprint for party: %s", party)

        with session_lock:
            # Check if a session is already active
            if session_state["active"]:
                logging.warning("Another fingerprint matching session is active.")
                return jsonify({"message": "Fingerprint processing is already in progress. Please wait."}), 409

            # Start the session
            session_state["active"] = True

        # Find the user by fingerprint
        user = find_user_by_fingerprint(fingerprint_data)
        if not user:
            logging.warning("No matching user found for the fingerprint.")
            reset_session() 
            return jsonify({"message": "No match found"}), 404

        # Check if the user has already voted
        if user.get('has_voted', False):
            logging.warning(f"User {user['_id']} has already voted.")
            reset_session()
            return jsonify({"message": "user has already voted "}), 400

        # Update vote count for the party
        votes_collection.update_one(
            {"party": party},
            {"$inc": {"vote_count": 1}},
            upsert=True
        )

        # Mark the user as having voted
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"has_voted": True}}
        )

        logging.info(f"Vote cast successfully for user {user['_id']} and party {party}.")
        reset_session()
        return jsonify({"message": "Vote cast successfully"}), 200

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        reset_session()
        return jsonify({"message": "An internal error occurred"}), 600


def find_user_by_fingerprint(fingerprint_data):
    """
    Find a user in the database whose fingerprint template matches the given data.
    """
    try:
        # Convert the hexadecimal string (fingerprint_data) to a numpy array of integers (binary format)
        fingerprint_data_array = np.array([int(fingerprint_data[i:i+2], 16) for i in range(0, len(fingerprint_data), 2)])

        for user in users_collection.find():
            stored_template = np.array(user['fingerprint_template'])

            # Compare the stored template with the fingerprint data from the ESP8266
            match_score = fingerprint_extractor.compare_templates(stored_template, fingerprint_data_array)

            if match_score >= 0.45:
                logging.info(f"Match found with score: {match_score} for user {user['_id']}")
                return user

        return None
    except Exception as e:
        logging.error(f"Error during fingerprint comparison: {str(e)}")
        return None



def reset_session():
    """
    Reset the session state to allow new fingerprint submissions.
    """
    global session_state
    with session_lock:
        session_state = {"active": False, "user_id": None}
    logging.info("Session state reset.")


if __name__ == '__main__':
    logging.info("Starting the voting server...")
    app.run(host='0.0.0.0', port=3000)
# this prototype is made with the collaboration of Techtraid Hackathon group (Admin:Dipayan Sardar)
#this protype code has still so many vulnarabilities,more improvents and solutions are on the way,for hardware interaction please chec simplified c++ arduino code