# Medical-Text-Summarization-Prototype
 Overview
This application provides fast, accurate, and structured summaries of clinical notes using state-of-the-art LLM models. It supports role-specific summaries for cardiologists, oncologists, nurses, and general use, highlighting critical findings to enhance clinical efficiency.
Features
	• Role-Based Summarization: Tailored summaries for different clinical roles.
	• Highlight Critical Findings: Automatically tags critical medical issues.
	• Efficient Caching: Utilizes Redis to cache summaries and reduce costs.
	• Robust Error Handling: Comprehensive logging and error detection.
	• Innovative LLM Evaluation: Uses DeepEval with custom metrics.

Tech Stack
Backend
	• FastAPI
	• OpenAI API (for LLM-based summarization)
	• Redis (caching layer)
	• Loguru (enhanced logging)
	• Docker & Docker Compose (containerization)
Frontend
	• React.js
	• Axios (HTTP requests)
	• Tailwind CSS

Setup Instructions
Prerequisites
	• Docker & Docker Compose installed.
	• OpenAI API key (set in .env file).
Step-by-Step Setup
	1. Clone the Repository

bash
git clone <repository_link>
cd medical_text_summarizer

	2. Configure Environment Variables Create .env in backend directory:

ini
LLM_API_KEY=your_openai_api_key
REDIS_URL=redis://redis:6379/0

	3. Start the Application with Docker

bash

docker-compose build
docker-compose up

	4. Access the Application
		• Frontend: http://localhost:3000
		• Backend API Docs: http://localhost:8000/docs


