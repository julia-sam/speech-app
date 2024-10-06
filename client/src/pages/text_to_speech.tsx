import React, { useState, useEffect } from 'react';

function TextToSpeechPage() {
  const [text, setText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [waveformUrl, setWaveformUrl] = useState('');
  const [pitchUrl, setPitchUrl] = useState('');
  const [transcription, setTranscription] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Load session data from the backend when the component mounts
  useEffect(() => {
    const sessionId = localStorage.getItem('session_id');
    if (sessionId) {
      loadSessionData(sessionId);
    }
  }, []);

  const handleStartTextToSpeech = () => {
    setIsLoading(true);
    fetch('http://localhost:8080/api/text-to-speech', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    })
      .then(response => response.json())
      .then(data => {
        setAudioUrl(`http://localhost:8080/${data.file_path}`);
        setWaveformUrl(`http://localhost:8080/${data.waveform_plot_path}`);
        setPitchUrl(`http://localhost:8080/${data.pitch_plot_path}`);
        setTranscription(data.transcription);
        setIsLoading(false);

        // Save session data to backend
        saveSessionData({
          text,
          audio_url: `http://localhost:8080/${data.file_path}`,
          waveform_url: `http://localhost:8080/${data.waveform_plot_path}`,
          pitch_url: `http://localhost:8080/${data.pitch_plot_path}`,
        });
      })
      .catch((error) => {
        console.error('Error:', error);
        setIsLoading(false);
      });
  };

  // Save session data to the backend
  const saveSessionData = (sessionData: { text: string, audio_url: string, waveform_url: string, pitch_url: string }) => {
    fetch('http://localhost:8080/api/save_session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sessionData),
    })
      .then(response => response.json())
      .then(data => {
        // Store session ID in localStorage
        localStorage.setItem('session_id', data.session_id);
        console.log('Session saved:', data);
      })
      .catch((error) => {
        console.error('Error saving session:', error);
      });
  };

  // Load session data from the backend
  const loadSessionData = (sessionId: string) => {
    fetch(`http://localhost:8080/api/load_session/${sessionId}`)
      .then(response => response.json())
      .then(data => {
        setText(data.text);
        setAudioUrl(data.audio_url);
        setWaveformUrl(data.waveform_url);
        setPitchUrl(data.pitch_url);
      })
      .catch(error => console.error('Error loading session:', error));
  };

  return (
    <div className="container">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text for conversion"
        rows={5}
        cols={40}
      />
      <button onClick={handleStartTextToSpeech} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Convert to Speech'}
      </button>

      {audioUrl && (
        <div>
          <audio controls>
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}

      {waveformUrl && <img src={waveformUrl} alt="Waveform" />}
      {pitchUrl && <img src={pitchUrl} alt="Pitch" />}
    </div>
  );
}

export default TextToSpeechPage;
