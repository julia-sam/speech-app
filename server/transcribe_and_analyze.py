import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import os
import parselmouth
import numpy as np

def transcribe_audio(audio_segment, keep_wav=False):
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        temp_wav_path = temp_wav.name
        audio_segment.export(temp_wav_path, format="wav")

    with sr.AudioFile(temp_wav_path) as source:
        try:
            audio = recognizer.record(source)
            transcription = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            transcription = "Speech Recognition could not understand audio"
        except sr.RequestError as e:
            transcription = f"Could not request results from Google Speech Recognition service; {e}"

    if not keep_wav:
        os.remove(temp_wav_path)

    return transcription, temp_wav_path

def analyze_pitch(audio_segment):
    # Convert the PyDub AudioSegment to a NumPy array
    samples = np.array(audio_segment.get_array_of_samples())

    # If the audio_segment is stereo, take only one channel
    if audio_segment.channels == 2:
        samples = samples[::2]

    # Convert the NumPy array to a Praat Sound object
    sound = parselmouth.Sound(samples.astype(float), sampling_frequency=audio_segment.frame_rate)
    pitch = sound.to_pitch()

    # Process and analyze pitch data
    pitch_values = pitch.selected_array['frequency']
    time_values = np.arange(0, len(pitch_values)) * pitch.dt

    return time_values, pitch_values

