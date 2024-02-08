import React, {useState} from "react";
import Image from 'next/image';

function AnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState({
    waveform_data: null,
    pitch_data: null,
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleStartAnalysis = () => {
    setIsLoading(true);
    // Trigger the recording and analysis process
    fetch('http://localhost:8080/record_and_plot', {
      method: 'POST',
    })
      .then((response) => response.json())
      .then(() => {
        fetch('http://localhost:8080/api/audio_analysis')
          .then((response) => response.json())
          .then((data) => {
            setAnalysisResult(data);
            setIsLoading(false);
          });
      })
      .catch((error) => {
        console.error('Error:', error);
        setIsLoading(false);
      });
  };

  return (
    <div>
        <div className="static-image">
          <Image src="/images/speech.jpeg" alt="Static Image" fill={true} />
        </div>
        <div className="heading-container">
          <div className="btn-record">
            <button onClick={handleStartAnalysis} disabled={isLoading}>
              {isLoading ? 'Recording...' : 'Record and Plot'}
            </button>
          </div>
        </div>
      <div>
        {analysisResult.waveform_data && (
          <Image src={`data:image/png;base64,${analysisResult.waveform_data}`} alt="Waveform" />
        )}
        {analysisResult.pitch_data && (
          <Image src={`data:image/png;base64,${analysisResult.pitch_data}`} alt="Pitch" />
        )}
        {!analysisResult.waveform_data && !analysisResult.pitch_data && !isLoading && (
          <p>No analysis data available. Click the button to start new analysis.</p>
        )}
      </div>
    </div>
  );
}

export default AnalysisPage;