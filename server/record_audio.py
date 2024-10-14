from pydub import AudioSegment, silence
import sounddevice as sd
import numpy as np
import os
import uuid

def record_audio(audio_wav_path="static/audio/recording.wav", silence_thresh=-50, silence_duration=300, chunk_duration=2):
    os.makedirs(os.path.dirname(audio_wav_path), exist_ok=True)
    print("Recording audio...")

    # audio recording parameters
    sample_rate = 44100  
    channels = 1  # Mono recording

    # Record audio chunks until silence longer than `silence_duration` is detected
    full_audio = AudioSegment.empty()
    silence_detected = False
    
    while not silence_detected:
        # Record in chunks of `chunk_duration` seconds
        audio_data = sd.rec(int(sample_rate * chunk_duration), samplerate=sample_rate, channels=channels, dtype=np.int16)
        sd.wait()

        # Convert recorded data to PyDub AudioSegment
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            sample_width=audio_data.dtype.itemsize,
            channels=channels
        )

        full_audio += audio_segment

        # Detect silence in the chunk
        silent_ranges = silence.detect_silence(audio_segment, min_silence_len=silence_duration, silence_thresh=silence_thresh)
        if silent_ranges:
            silence_detected = True
    
    # Split the full audio on silence and remove silence
    non_silent_parts = silence.split_on_silence(full_audio, min_silence_len=silence_duration, silence_thresh=silence_thresh, keep_silence=200)

    # Concatenate non-silent audio segments
    if non_silent_parts:
        trimmed_audio = non_silent_parts[0]  # Start with the first non-silent segment
        for part in non_silent_parts[1:]:  # Append the rest of the non-silent parts
            trimmed_audio += part
    else:
        trimmed_audio = full_audio  # If no silence was found, keep the full audio

    # Save the trimmed audio
    trimmed_audio.export(audio_wav_path, format="wav")

    # Calculate and print the duration of the user's voice
    voice_duration = len(trimmed_audio) / 1000.0  # Convert to seconds
    print(f"User voice duration: {voice_duration} seconds")

    print("Audio recorded successfully.")
    return trimmed_audio, voice_duration
