import React, { useState } from 'react';
import axios from 'axios';

function App() {
  
  const [notes, setNotes] = useState('');
  const [role, setRole] = useState('general');
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0); // Progress bar state
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [feedbackMessage, setFeedbackMessage] = useState('');

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'; 
 

  
  const handleInputChange = (e) => {
    setNotes(e.target.value);
    setSummary(''); 
    setFeedback('');
    setShowFeedbackForm(false); 
  };

  // Handle Form Submission
  const handleSubmit = async () => {
     
    setSummary("");
    setError("");
    setFeedbackMessage('');

    if (!notes.trim()) {
      setError("Clinical notes cannot be empty.");
      return;
    }
    if (notes.length < 50) {
      setError("Please enter at least 50 characters.");
      return;
    }
    if (/^\d+$/.test(notes)) {
      setError("Clinical notes cannot be just numbers.");
      return;
    }

  const medicalKeywords = ["patient", "diagnosis", "medication", "symptoms", "treatment", "hospital", "doctor", "disease"];
  const containsMedicalTerm = medicalKeywords.some(term => notes.toLowerCase().includes(term));

  if (!containsMedicalTerm) {
    setError("The text does not seem to contain medical information. Please enter valid clinical notes.");
    return;
  }

    try {
      setLoading(true);
      setProgress(10); 

      
      try {
        await axios.get(`${apiUrl}/health`);
      } catch (backendError) {
        setLoading(false);
        setProgress(0);
        setError("Backend is not running! Please start the backend.");
        console.error("Backend is not running!", backendError);
        return; 
      }

      
      const response = await axios.post(`${apiUrl}/summarize`, {
        notes,
        role
      }, {
        onDownloadProgress: (progressEvent) => {
          setProgress(Math.min(90, (progressEvent.loaded / progressEvent.total) * 100)); 
        }
      });

      
      setSummary(response.data.summary);
      setProgress(100);
      setError('');
    } catch (err) {
      
      setError(err.response?.data?.detail || "An error occurred");
      console.error("API Error:", err.response?.data);
    } finally {
      
      setTimeout(() => {
        setLoading(false);
        setProgress(0);
      }, 1000);
    }
  };

  const handleSubmitFeedback = async () => {
    try {
      await axios.post(`${apiUrl}/feedback`, {
        request_id: Date.now().toString(),
        summary,
        feedback,
      });
      setFeedbackMessage('Feedback submitted successfully!');
      
      setSummary('');
      setNotes('');
      setFeedback('');
      setShowFeedbackForm(false);
    } catch (error) {
      setFeedbackMessage('Error submitting feedback.');
    }
  };  

  return (
    <div className="min-h-screen bg-gray-100 p-5">
      <div className="max-w-lg mx-auto bg-white shadow-lg rounded-lg p-5">
        <h1 className="text-2xl font-bold mb-4">Clinical Notes Summarizer</h1>

        <textarea
          className="w-full border p-2 mb-4 rounded"
          placeholder="Paste your clinical notes here..."
          value={notes}
          onChange={handleInputChange}
          rows="5"
        />

        <select
          className="w-full border p-2 mb-4 rounded"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        >
          <option value="general">General</option>
          <option value="cardiologist">Cardiologist</option>
          <option value="nurse">Nurse</option>
          <option value="oncologist">Oncologist</option>
        </select>

        {loading && (
          <div className="w-full bg-gray-300 h-2 rounded mb-4">
            <div className="bg-blue-500 h-2 rounded" style={{ width: `${progress}%` }}></div>
          </div>
        )}

        <button
          className={`w-full py-2 mb-4 rounded ${
            loading ? "bg-gray-400" : "bg-blue-500 hover:bg-blue-600"
          } text-white font-bold`}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Summarizing..." : "Get Summary"}
        </button>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        {summary && (
          <div className="mt-4 p-4 bg-gray-50 border rounded">
            <h2 className="font-bold mb-2">Generated Summary:</h2>
            <p className="whitespace-pre-wrap">{summary}</p>

            {/* Feedback Checkbox */}
            <div className="mt-4">
              <label>
                <input
                  type="checkbox"
                  checked={showFeedbackForm}
                  onChange={() => setShowFeedbackForm(!showFeedbackForm)}
                  className="mr-2"
                />
                Provide feedback?
              </label>
            </div>

            {/* Feedback Form */}
            {showFeedbackForm && (
              <div className="mt-4">
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Provide feedback about the summary..."
                  className="w-full border p-2 mb-2 rounded"
                  rows="3"
                />
                <button
                  onClick={handleSubmitFeedback}
                  className="bg-green-500 text-white p-2 rounded"
                >
                  Submit Feedback
                </button>
                {feedbackMessage && <p className="mt-2">{feedbackMessage}</p>}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;