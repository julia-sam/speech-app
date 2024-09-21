from flask_cors import CORS
import base64
from flask import Flask, current_app, jsonify, send_from_directory, url_for, request, send_file, send_from_directory
import threading
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from database import db
from models.audio_metadata import AudioMetadata 
from record_audio import record_audio
from plot_results import plot_results
from werkzeug.utils import secure_filename
from flask import current_app
from exercise_service import fetch_exercises_for_category
from text_to_speech_service import generate_speech
from io import BytesIO

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')
app.config.from_object('config')
db.init_app(app)  
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(app.static_folder + '/build/' + path):
        return send_from_directory('../client/build', path)
    else:
        return send_from_directory('../client/build', 'index.html')
    

@app.route("/api/audio_analysis", methods=['GET'])
def return_audio_analysis():
    with app.app_context():
        result_data = current_app.config.get('result_data', {})
        logging.info("Returning audio analysis data")
        if not result_data:
            logging.warning("Result data is empty")
        return jsonify(result_data)


@app.route('/api/record_and_plot', methods=['POST'])
def start_record_and_plot():
    if not current_app.config.get('processing_started', False):
        current_app.config['processing_started'] = True
        current_app.config['processing_done'] = False
        audio_thread = threading.Thread(target=audio_processing_thread, args=(current_app._get_current_object(),))
        audio_thread.start()
        return jsonify({'message': 'Recording and plotting started'}), 202
    else:
        return jsonify({'message': 'Processing is already in progress'}), 409

@app.route('/api/processing_status', methods=['GET'])
def check_processing_status():
    if current_app.config.get('processing_done', False):
        return jsonify({'status': 'complete', 'result_data': current_app.config.get('result_data', {})})
    else:
        return jsonify({'status': 'processing'}), 202

    
def audio_processing_thread(app):
    with app.app_context():
        app_obj = current_app._get_current_object()
        
        audio_dir = os.path.join(app_obj.root_path, 'static/audio')
        os.makedirs(audio_dir, exist_ok=True)

        audio_wav_path = os.path.join(audio_dir, 'recording.wav')

        recording = record_audio(audio_wav_path=audio_wav_path)

        images_dir = os.path.join(app_obj.root_path, 'static/images')
        os.makedirs(images_dir, exist_ok=True)

        waveform_plot_filename = secure_filename('waveform_plot.png')
        pitch_plot_filename = secure_filename('pitch_plot.png')
        
        waveform_plot_path = os.path.join(images_dir, waveform_plot_filename)
        pitch_plot_path = os.path.join(images_dir, pitch_plot_filename)

        result_data = plot_results(recording, waveform_plot_path, pitch_plot_path)

        with open(waveform_plot_path, 'rb') as waveform_file:
            waveform_data = base64.b64encode(waveform_file.read()).decode('utf-8')

        with open(pitch_plot_path, 'rb') as pitch_file:
            pitch_data = base64.b64encode(pitch_file.read()).decode('utf-8')

        current_app.config['result_data'] = {
            'waveform_data': waveform_data,
            'pitch_data': pitch_data
        }
        current_app.config['processing_done'] = True
        current_app.config['processing_started'] = False

@app.route('/api/pronunciation_practice')
def pronunciation_practice():
    categories = ["The R Sound", "Short I Sound", "Long I Sound", "Phrase"] 
    return jsonify(categories=categories)


@app.route('/api/pronunciation_practice/<category_name>')
def pronunciation_category_data(category_name):
    domain = 'http://localhost:8080'
    exercises = fetch_exercises_for_category(category_name)
    exercises_data = [
        {
            'word_or_phrase': exercise['word_or_phrase'], 
            'pronunciationUrl': domain + url_for('static', filename=exercise['audio_file_path'])
        } for exercise in exercises
    ]
    return jsonify(exercises_data)

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        file_path = generate_speech(text)

        return jsonify({'message': 'Speech created', 'file_path': file_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

if __name__ == "__main__":
    app.run(debug=True, port=8080)

