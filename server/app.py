from flask_cors import CORS
import base64
from flask import Flask, current_app, jsonify
import threading
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from database import db
from models.audio_metadata import AudioMetadata 
from record_audio import record_audio
from plot_results import plot_results

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='../client/build', static_url_path='/')
app.config.from_object('config')
db.init_app(app)  
CORS(app)

from models.audio_metadata import AudioMetadata

@app.route("/api/audio_analysis", methods=['GET'])
def return_audio_analysis():
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
        audio_thread = threading.Thread(target=audio_processing_thread)
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

    
def audio_processing_thread():
    with app.app_context():
        app_obj = current_app._get_current_object()
        audio_wav_path = os.path.join(app_obj.root_path, 'static/audio', 'recording.wav')

        # Record the audio
        recording = record_audio(audio_wav_path=audio_wav_path)

        # Define paths for the plots
        waveform_plot_path = os.path.join(current_app.static_folder, 'images', 'waveform_plot.png')
        pitch_plot_path = os.path.join(current_app.static_folder, 'images', 'pitch_plot.png')

        # Call the plot_results function
        result_data = plot_results(recording, waveform_plot_path, pitch_plot_path)

        # Store the result_data in the app context
        current_app.config['result_data'] = {
            'waveform_data': base64.b64encode(open(waveform_plot_path, 'rb').read()).decode('utf-8'),
            'pitch_data': base64.b64encode(open(pitch_plot_path, 'rb').read()).decode('utf-8')
        }
        current_app.config['processing_done'] = True
        current_app.config['processing_started'] = False


if __name__ == "__main__":
    app.run(debug=True, port=8080)

