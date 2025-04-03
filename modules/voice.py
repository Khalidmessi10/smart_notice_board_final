# modules/voice.py
from flask import Blueprint, render_template, jsonify, request
import json
import os
import random
from config import Config

voice_bp = Blueprint('voice', __name__)

# Load keywords and responses
with open('keywords.json') as f:
    keywords_data = json.load(f)

with open('responses.json') as f:
    responses_data = json.load(f)

@voice_bp.route('/voice')
def voice():
    return render_template('voice.html')

@voice_bp.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        data = request.get_json()
        text = data.get('text', '').lower()
        
        # Find matching keyword
        matched_id = None
        for key, value in keywords_data.items():
            if any(keyword in text for keyword in value['keywords']):
                matched_id = str(value['id'])
                image_path = os.path.join('uploads', 'locations', value['image'])
                break
        
        if not matched_id:
            return jsonify({
                'success': False,
                'message': 'No matching location found'
            })
        
        # Get random response
        responses = responses_data.get(matched_id, [])
        if not responses:
            return jsonify({
                'success': False,
                'message': 'No responses available for this location'
            })
        
        response = random.choice(responses)
        
        return jsonify({
            'success': True,
            'response': response,
            'image_path': image_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })