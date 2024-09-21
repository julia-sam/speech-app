import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_speech(text):
    static_audio_dir = Path(__file__).parent / 'static/audio'
    static_audio_dir.mkdir(parents=True, exist_ok=True)

    speech_file_path = static_audio_dir / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",  
        voice="alloy", 
        input=text
    )
    response.stream_to_file(speech_file_path)
    
    return speech_file_path.name