# modules/voice.py
from flask import Blueprint, render_template, jsonify, request
import google.generativeai as genai
import json
import os
import random
from config import Config
from nltk.stem import WordNetLemmatizer

voice_bp = Blueprint('voice', __name__)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')

# Load keywords and responses
with open('keywords.json') as f:
    keywords_data = json.load(f)

with open('responses.json') as f:
    responses_data = json.load(f)

@voice_bp.route('/voice')
def voice():
    return render_template('voice.html')

def normalize_text(text):
    """Normalize text for matching using lemmatization"""
    text = " ".join(text.lower().split())  # Normalize spaces and lowercase
    words = text.split()
    return " ".join([lemmatizer.lemmatize(word) for word in words])

def get_image_and_response(context):
    """Improved keyword matching using lemmatization"""
    normalized_context = normalize_text(context)
    print(f"Normalized input: {normalized_context}")  # Debugging

    for location_id, location_data in keywords_data.items():
        for keyword in location_data["keywords"]:
            normalized_keyword = normalize_text(keyword)
            print(f"Checking: {normalized_keyword}")  # Debugging
            if normalized_keyword in normalized_context:
                print(f"Match found: {normalized_keyword}")
                unique_id = str(location_data["id"])
                image_path = os.path.join('uploads', 'locations', location_data['image'])
                
                responses = responses_data.get(unique_id, [])
                response = random.choice(responses) if responses else "No response available"
                return image_path, response, location_id

    return None, "I couldn't find any matching information.", None

@voice_bp.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'message': 'Empty voice input'})

        # First try direct keyword matching
        image_path, response, location_key = get_image_and_response(text)
        
        # If no direct match, use Gemini for better understanding
        if not location_key:
            prompt = f"""
            Analyze this voice query about locations: "{text}"
            Available locations: {json.dumps({k: v['keywords'] for k, v in keywords_data.items()})}
            Respond ONLY with the matching location key (e.g. "ssos_lab") or "unknown".
            """
            
            response = model.generate_content(prompt)
            location_key = response.text.strip().strip('"')
            
            if location_key != "unknown" and location_key in keywords_data:
                location_info = keywords_data[location_key]
                image_path = os.path.join('uploads', 'locations', location_info['image'])
                responses = responses_data.get(str(location_info['id']), [])
                response = random.choice(responses) if responses else "No response available"
            else:
                return jsonify({
                    'success': False,
                    'message': 'No matching location found'
                })

        return jsonify({
            'success': True,
            'response': response,
            'image_path': image_path,
            'location': location_key
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        })