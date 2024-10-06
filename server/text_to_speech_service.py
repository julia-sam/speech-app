from pydub import AudioSegment
from pathlib import Path
from flask import jsonify
from transcribe_and_analyze import transcribe_audio, analyze_pitch
import matplotlib.pyplot as plt
import numpy as np
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import uuid

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_speech(text):
    static_audio_dir = Path(__file__).parent / 'static/audio'
    static_audio_dir.mkdir(parents=True, exist_ok=True)

    speech_file_name = f"speech_{uuid.uuid4()}.mp3"
    speech_file_path = static_audio_dir / speech_file_name
    logging.info(f"Generated speech file path: {speech_file_path}")

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(speech_file_path)
    except Exception as e:
        logging.error(f"Error in speech generation: {e}")
        raise e

    audio_segment = AudioSegment.from_mp3(speech_file_path)
    waveform_plot_path = f"{speech_file_path}_waveform.png"
    pitch_plot_path = f"{speech_file_path}_pitch.png"
    logging.info(f"Waveform plot path: {waveform_plot_path}, Pitch plot path: {pitch_plot_path}")

    result = plot_results(audio_segment, waveform_plot_path, pitch_plot_path)
    transcription = result['transcription']
   
    relative_file_path = f"/static/audio/{speech_file_name}"
    relative_waveform_url = f"/static/audio/{speech_file_name}_waveform.png"
    relative_pitch_url = f"/static/audio/{speech_file_name}_pitch.png"

    return {
        'file_path': relative_file_path,
        'waveform_plot_path': relative_waveform_url,
        'pitch_plot_path': relative_pitch_url,
        'transcription': transcription
    }

def plot_results(audio_segment, waveform_plot_path, pitch_plot_path):
    print("Plotting results...")

    transcription, _ = transcribe_audio(audio_segment)

    samples = np.array(audio_segment.get_array_of_samples())
    duration = len(samples) / audio_segment.frame_rate
    time = np.linspace(0., duration, len(samples))

    plt.figure()
    plt.plot(time, samples)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title("Waveform for: " + transcription)
    plt.savefig(waveform_plot_path)
    plt.close()
    print("Waveform plot saved.")

    # Plot the pitch data
    try:
        time_values, pitch_values = analyze_pitch(audio_segment)
        plt.figure()
        plt.plot(time_values, pitch_values, 'o', markersize=5, color='blue')
        plt.title("Pitch Over Time for: " + transcription)
        plt.xlabel("Time (s)")
        plt.ylabel("Pitch (Hz)")
        plt.grid(True)
        plt.savefig(pitch_plot_path)
        plt.close()
        print("Pitch plot saved.")
    except Exception as e:
        print(f"Error in pitch analysis: {e}")

    return {
        'waveform_plot_path': waveform_plot_path,
        'pitch_plot_path': pitch_plot_path,
        'transcription': transcription
    }
