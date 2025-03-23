from flask import request, Blueprint, jsonify
from rapidfuzz import fuzz

checking_blueprint = Blueprint('checking', __name__)

@checking_blueprint.route('/check-lyrics', methods=['POST'])
def check():
    try: 
        data = request.json
        actualSong = data["actualSong"]
        userGuess = data["userGuess"]
        result = fuzz.partial_ratio(actualSong, userGuess)
        if result >= 80:
            return jsonify({"message": "Correct"})
        else:
            return jsonify({"message": "Incorrect"})
            
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500