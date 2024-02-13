from flask_cors import CORS
import base64
from flask import Flask, current_app, jsonify, url_for
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

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='../client/build', static_url_path='/')
app.config.from_object('config')
db.init_app(app)  
CORS(app)

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
    # Ensure only one audio processing happens at a time
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
        # Get an instance of your application
        app_obj = current_app._get_current_object()
        
        # Ensure the static/audio directory exists
        audio_dir = os.path.join(app_obj.root_path, 'static/audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Define the full path for the audio file
        audio_wav_path = os.path.join(audio_dir, 'recording.wav')

        # Record the audio
        recording = record_audio(audio_wav_path=audio_wav_path)

        # Ensure the static/images directory exists
        images_dir = os.path.join(app_obj.root_path, 'static/images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Define paths for the plots
        waveform_plot_filename = secure_filename('waveform_plot.png')
        pitch_plot_filename = secure_filename('pitch_plot.png')
        
        waveform_plot_path = os.path.join(images_dir, waveform_plot_filename)
        pitch_plot_path = os.path.join(images_dir, pitch_plot_filename)

        # Call the plot_results function
        result_data = plot_results(recording, waveform_plot_path, pitch_plot_path)

        # Store the result_data in the app context using context managers to open files
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


if __name__ == "__main__":
    app.run(debug=True, port=8080)

