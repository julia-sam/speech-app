import React, { useState } from 'react';

function TextToSpeechPage() {
  const [text, setText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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
        setAudioUrl(`http://localhost:8080/static/audio/${data.file_path.split('/').pop()}`);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error:', error);
        setIsLoading(false);
      });
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
    </div>
  );
}

export default TextToSpeechPage;
