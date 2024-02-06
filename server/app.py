from flask_cors import CORS
import base64
from flask import Flask, send_from_directory, Response, send_file, current_app, jsonify, stream_with_context, url_for, Response
from record_audio import record_audio
from transcribe_and_analyze import *
# from audio_processing.exercise_service import *
from plot_results import plot_results
import threading
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='../client/build', static_url_path='/')
CORS(app)
app.config['recording_lock'] = threading.Lock()
app.config['processing_done'] = False
app.config['result_data'] = {}

@app.route("/api/home", methods=['GET'])
def return_home():
    return jsonify({
        'message': "Hello World!",
        'people': ['Jack', 'Betty', 'Harry']
    })

def audio_processing_thread():
    with app.app_context():
        if not current_app.config['processing_done']:
            app_obj = current_app._get_current_object()
            audio_wav_path = os.path.join(app_obj.root_path, 'static/audios/user_recordings', 'recording.wav')

            # Record the audio
            recording = record_audio(audio_wav_path=audio_wav_path)

            # Define paths for the plots
            waveform_plot_path = os.path.join(current_app.static_folder, 'images', 'waveform_plot.png')
            pitch_plot_path = os.path.join(current_app.static_folder, 'images', 'pitch_plot.png')

            # Call the plot_results function
            result_data = plot_results(recording, waveform_plot_path, pitch_plot_path)

            # Update the result_data dictionary and set processing_done flag
            current_app.config['result_data'] = result_data
            current_app.config['processing_done'] = True

@app.route("/api/audio_analysis", methods=['GET'])
def return_audio_analysis():
    result_data = current_app.config.get('result_data', {})
    logging.info("Returning audio analysis data")
    if not result_data:
        logging.warning("Result data is empty")
    return jsonify(result_data)


@app.route('/api/record_and_plot', methods=['POST'])
def return_record_and_plot():
    # Start the audio processing in a background thread as before
    audio_thread = threading.Thread(target=audio_processing_thread)
    audio_thread.start()
    audio_thread.join()

    # Fetch result data
    result_data = current_app.config.get('result_data', {})
    if result_data:
        # Prepare your response data
        response_data = {
            'waveform_data': None,
            'pitch_data': None,
            **result_data  
        }
        
        if 'waveform_plot_path' in result_data and os.path.exists(result_data['waveform_plot_path']):
            with open(result_data['waveform_plot_path'], 'rb') as image_file:
                response_data['waveform_data'] = base64.b64encode(image_file.read()).decode('utf-8')

        if 'pitch_plot_path' in result_data and os.path.exists(result_data['pitch_plot_path']):
            with open(result_data['pitch_plot_path'], 'rb') as image_file:
                response_data['pitch_data'] = base64.b64encode(image_file.read()).decode('utf-8')

        return jsonify(response_data)
    else:
        return jsonify({'message': 'No data available yet.'})


if __name__ == "__main__":
    app.run(debug=True, port=8080)

