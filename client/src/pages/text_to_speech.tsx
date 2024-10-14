import React, { useState, useEffect } from 'react';
import Image from "next/image";

function TextToSpeechAndAnalysisPage() {
  const [text, setText] = useState('');
  const [apiKey, setApiKey] = useState(''); // New state for API key
  const [audioUrl, setAudioUrl] = useState('');
  const [waveformUrl, setWaveformUrl] = useState('');
  const [pitchUrl, setPitchUrl] = useState('');
  const [transcription, setTranscription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState({
    waveform_data: null,
    pitch_data: null,
    user_audio: null,
    
  });

  // Load session data for both Text-to-Speech and Analysis when component mounts
  useEffect(() => {
    const sessionId = localStorage.getItem('session_id');
    const analysisSessionId = localStorage.getItem("analysis_session_id");
    if (sessionId) {
      loadSessionData(sessionId);
    }
    if (analysisSessionId) {
      loadAnalysisSessionData(analysisSessionId);
    }
  }, []);

  // Trigger the text-to-speech process
  const handleStartTextToSpeech = () => {
    if (!apiKey) {
      alert("Please provide your OpenAI API key.");
      return;
    }
    setIsLoading(true);
    fetch('http://localhost:8080/api/text-to-speech', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, api_key: apiKey }), // Include the user's API key
    })
      .then(response => response.json())
      .then(data => {
        setAudioUrl(`http://localhost:8080/${data.file_path}`);
        setWaveformUrl(`http://localhost:8080/${data.waveform_plot_path}`);
        setPitchUrl(`http://localhost:8080/${data.pitch_plot_path}`);
        setTranscription(data.transcription);
        setIsLoading(false);

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

  // Trigger the recording and analysis process
  const handleStartAnalysis = () => {
    setIsLoading(true);
    fetch("http://localhost:8080/api/record_and_plot", {
      method: "POST",
    })
      .then(() => {
        checkProcessingStatus();
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
      });
  };

  // Check the analysis processing status
  const checkProcessingStatus = () => {
    fetch("http://localhost:8080/api/processing_status")
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "complete") {
          setAnalysisResult(data.result_data);
          setIsLoading(false);

          saveAnalysisSessionData({
            waveform_data: data.result_data.waveform_data,
            pitch_data: data.result_data.pitch_data,
          });
        } else {
          setTimeout(checkProcessingStatus, 2000);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
      });
  };

  // Save session data for text-to-speech
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
        localStorage.setItem('session_id', data.session_id);
        console.log('Session saved:', data);
      })
      .catch((error) => {
        console.error('Error saving session:', error);
      });
  };

  // Save session data for analysis
  const saveAnalysisSessionData = (sessionData: { waveform_data: string; pitch_data: string }) => {
    fetch("http://localhost:8080/api/save_session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(sessionData),
    })
      .then((response) => response.json())
      .then((data) => {
        localStorage.setItem("analysis_session_id", data.session_id);
        console.log("Analysis session saved:", data);
      })
      .catch((error) => {
        console.error("Error saving session:", error);
      });
  };

  // Load session data for text-to-speech
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

  // Load session data for analysis
  const loadAnalysisSessionData = (sessionId: string) => {
    fetch(`http://localhost:8080/api/load_session/${sessionId}`)
      .then((response) => response.json())
      .then((data) => {
        setAnalysisResult({
          waveform_data: data.waveform_data,
          pitch_data: data.pitch_data,
          user_audio: data.result_data.user_audio,
        });
      })
      .catch((error) => console.error("Error loading analysis session:", error));
  };

  return (
    <div className="container">
  {/* API Key Input */}
  <div>
    <h3>Enter your OpenAI API Key:</h3>
    <input
      type="text"
      value={apiKey}
      onChange={(e) => setApiKey(e.target.value)}
      placeholder="Enter API Key"
    />
  </div>

  {/* Text-to-Speech Section */}
  <div className="text-to-speech-section">
    <textarea
      value={text}
      onChange={(e) => setText(e.target.value)}
      placeholder="Enter text for conversion"
      rows={5}
      cols={40}
    />
    <button onClick={handleStartTextToSpeech} disabled={isLoading || !apiKey}>
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

    <div className="chart-row">
      {waveformUrl && <img className="chart" src={waveformUrl} alt="Waveform" />}
      {pitchUrl && <img className="chart" src={pitchUrl} alt="Pitch" />}
    </div>
  </div>

  {/* Analysis Section */}
  <div className="analysis-section">
    <div className="btn-record">
      <button onClick={handleStartAnalysis} disabled={isLoading}>
        {isLoading ? "Recording..." : "Record and Plot"}
      </button>
    </div>

    <div className="chart-row">
      {analysisResult.waveform_data && (
        <img
          className="chart"
          src={`data:image/png;base64,${analysisResult.waveform_data}`}
          alt="Waveform"
        />
      )}
      {analysisResult.pitch_data && (
        <img
          className="chart"
          src={`data:image/png;base64,${analysisResult.pitch_data}`}
          alt="Pitch"
        />
      )}
    </div>
    {analysisResult.user_audio && (
    <div className="audio-player">
      <audio controls>
        <source src={`http://localhost:8080${analysisResult.user_audio}`} type="audio/wav" />
        Your browser does not support the audio element.
      </audio>
    </div>
  )}
  </div>
  
</div>

  );
}

export default TextToSpeechAndAnalysisPage;
