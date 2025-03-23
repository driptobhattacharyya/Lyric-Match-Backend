import random
from google import genai
from flask import Blueprint, request, jsonify
import json
import re

import os

client = genai.Client(api_key=os.environ.get("API_KEY"))



genai_blueprint = Blueprint('genai', __name__)

@genai_blueprint.route('/test', methods=['GET'])
def test():
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Explain how AI works",
    )
    print(response.text)
    return jsonify({"message": response.text})



# Function to read songs from text file
def read_songs_from_file(file_path):
    songs = ""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and '|' in line:
                    song_title, artist = line.split('|', 1)
                    songs = songs + song_title.strip() + " by " + artist.strip() + ", "
    except Exception as e:
        print(f"Error reading song file: {e}")
    return songs[:-1]

cached_songs = ""
past_songs = []
# Endpoint to generate lyric snippet
@genai_blueprint.route('/generate-lyrics', methods=['GET'])
def generate_lyrics():
    try:
        # Read songs from file
        if len(cached_songs) > 0:
            songs = cached_songs
        else:
            songs = read_songs_from_file('song_list.txt')  # Make sure to put your file path here
        # print("Songs collected", songs)

        if not songs:
            return jsonify({"error": "No songs available"}), 500
        
        exclusion = "Exclude these songs:"
        
        # Prepare prompt for Gemini
        prompt = f"""
        Choose a song randomly from among the following songs: {songs}.
        Generate exactly 2-4 lines of lyrics from the song.
        These should be consecutive lines from the song, recognizable but not too obvious.
        Include the title of the song and the artist, in the json format:
        {{
            "lyrics": "the 2-4 lines of lyrics here",
            "song": "song title here",
            "artist": "artist name here"
        }}
        Only return the lyrics, song name and artist name. No additional text, introduction, or explanation.
        """
        
        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Try to extract JSON if wrapped in code blocks or has extra text
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            # If no code blocks, try to extract just the JSON object
            json_match = re.search(r'({.*})', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        # Parse the JSON
        try:
            result = json.loads(response_text)
            
            # Validate that the result has the expected structure
            required_keys = ["lyrics", "song", "artist"]
            for key in required_keys:
                if key not in result:
                    return jsonify({"error": f"Missing required field: {key}"}), 500

            return jsonify(result)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            return jsonify({
                "error": "Failed to parse response from AI",
                "raw_response": response_text
            }), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500