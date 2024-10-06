import React, { useState, useEffect } from "react";
import Image from "next/image";

function AnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState({
    waveform_data: null,
    pitch_data: null,
  });
  const [isLoading, setIsLoading] = useState(false);

  // Load session data on mount
  useEffect(() => {
    const sessionId = localStorage.getItem("analysis_session_id");
    if (sessionId) {
      loadSessionData(sessionId);
    }
  }, []);

  // Check the processing status
  const checkProcessingStatus = () => {
    fetch("http://localhost:8080/api/processing_status")
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "complete") {
          // Processing is complete, set the results and save session
          setAnalysisResult(data.result_data);
          setIsLoading(false);

          // Save session data to the backend
          saveSessionData({
            waveform_data: data.result_data.waveform_data,
            pitch_data: data.result_data.pitch_data,
          });
        } else {
          // Processing is not yet complete, check again after a delay
          setTimeout(checkProcessingStatus, 2000); // Check every 2 seconds
        }
      })
      .catch((error) => {
        console.error("Error:", error);
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
        // Start checking the processing status
        checkProcessingStatus();
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
      });
  };

  // Save session data to the backend
  const saveSessionData = (sessionData: { waveform_data: string; pitch_data: string }) => {
    fetch("http://localhost:8080/api/save_session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(sessionData),
    })
      .then((response) => response.json())
      .then((data) => {
        // Store session ID in localStorage
        localStorage.setItem("analysis_session_id", data.session_id);
        console.log("Session saved:", data);
      })
      .catch((error) => {
        console.error("Error saving session:", error);
      });
  };

  // Load session data from the backend
  const loadSessionData = (sessionId: string) => {
    fetch(`http://localhost:8080/api/load_session/${sessionId}`)
      .then((response) => response.json())
      .then((data) => {
        setAnalysisResult({
          waveform_data: data.waveform_data,
          pitch_data: data.pitch_data,
        });
      })
      .catch((error) => console.error("Error loading session:", error));
  };

  return (
    <div>
      <div className="static-image">
        <Image src="/images/speech.jpeg" alt="Static Image" fill={true} />
      </div>
      <div className="heading-container">
        <div className="btn-record">
          <button onClick={handleStartAnalysis} disabled={isLoading}>
            {isLoading ? "Recording..." : "Record and Plot"}
          </button>
        </div>
      </div>
      <div className="charts">
        {analysisResult.waveform_data && (
          <img
            src={`data:image/png;base64,${analysisResult.waveform_data}`}
            alt="Waveform"
          />
        )}
        {analysisResult.pitch_data && (
          <img
            src={`data:image/png;base64,${analysisResult.pitch_data}`}
            alt="Pitch"
          />
        )}
      </div>
    </div>
  );
}

export default AnalysisPage;
