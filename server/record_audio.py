from pydub import AudioSegment
import sounddevice as sd
import numpy as np

def record_audio(duration=5, audio_wav_path="audio/recording.wav"):
    print("Recording audio...")

    # audio recording parameters
    sample_rate = 44100  
    channels = 1  # Mono recording

    # Record audio using sounddevice
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=channels, dtype=np.int16)
    sd.wait()

    # Convert recorded data to PyDub AudioSegment
    audio_segment = AudioSegment(
        audio_data.tobytes(),
        frame_rate=sample_rate,
        sample_width=audio_data.dtype.itemsize,
        channels=channels
    )

    # Save audio as WAV file
    audio_segment.export(audio_wav_path, format="wav")

    print("Audio recorded successfully.")
    return audio_segment
