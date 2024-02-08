import React, {useState} from "react";
import Image from 'next/image';

function AnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState({
    waveform_data: null,
    pitch_data: null,
  });
  const [isLoading, setIsLoading] = useState(false);

  const checkProcessingStatus = () => {
    fetch('http://localhost:8080/api/processing_status')
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'complete') {
          // Processing is complete, set the results
          setAnalysisResult(data.result_data);
          setIsLoading(false);
        } else {
          // Processing is not yet complete, check again after a delay
          setTimeout(checkProcessingStatus, 2000); // Check every 2 seconds
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        setIsLoading(false);
      });
  };

  const handleStartAnalysis = () => {
    setIsLoading(true);
    // Trigger the recording and analysis process
    fetch('http://localhost:8080/api/record_and_plot', {
      method: 'POST',
    })
      .then((response) => response.json())
      .then(() => {
        // Start checking the processing status
        checkProcessingStatus();
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
          <img src={`data:image/png;base64,${analysisResult.waveform_data}`} alt="Waveform" />
        )}
        {analysisResult.pitch_data && (
          <img src={`data:image/png;base64,${analysisResult.pitch_data}`} alt="Pitch" />
        )}
      </div>
    </div>
  );
}

export default AnalysisPage;