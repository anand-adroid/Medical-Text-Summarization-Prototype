# Medical-Text-Summarization-Prototype

## Overview

This application provides **fast, accurate, and structured summaries** of clinical notes using state-of-the-art **LLM models**. It supports **role-specific summaries** for cardiologists, oncologists, nurses, and general use, highlighting **critical findings** to enhance clinical efficiency.

## Features

- **Role-Based Summarization**  
  Tailored summaries for different clinical roles.
- **Highlight Critical Findings**  
  Automatically tags critical medical issues.
- **Efficient Caching**  
  Utilizes **Redis** to cache summaries and reduce costs.
- **Robust Error Handling**  
  Comprehensive logging and error detection.
- **Innovative LLM Evaluation**  
  Uses **DeepEval** with custom metrics.

## Tech Stack

### Backend
- FastAPI
- OpenAI API (for LLM-based summarization)
- Redis (caching layer)
- Loguru (enhanced logging)
- Docker & Docker Compose (containerization)

### Frontend
- React.js
- Axios (HTTP requests)
- Tailwind CSS

## Setup Instructions

### Prerequisites

- Docker & Docker Compose installed.
- Redis Installed
- OpenAI API key (set in `.env` file).

### Step-by-Step Setup

#### 1. Clone the Repository
```sh
git clone https://github.com/anand-adroid/Medical-Text-Summarization-Prototype.git
cd Medical-Text-Summarization-Prototype 
```
#### 2. Configure Environment Variables Create .env in backend directory:

```
LLM_API_KEY=your_openai_api_key
REDIS_URL=redis://redis:6379/0

```
#### 3. Start the Application with Docker

```
docker-compose build
docker-compose up
```

#### 4. Access the Application  
- **Frontend**: <a href="http://localhost:3000" target="_blank">http://localhost:3000</a>  
- **Backend API Docs**: <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a>

#### 5. Architecture Overview

![Architecture Diagram](https://github.com/anand-adroid/Medical-Text-Summarization-Prototype/blob/564842a48fa954acd3dbb57c2be70744ba4ded4a/Architecture.png)

### **System Components**
- **Frontend (React)**: Sends clinical notes to the FastAPI backend for processing.
- **FastAPI Backend**: Handles requests, processes clinical notes, generates summaries, and evaluates them.
- **OpenAI API (Summarizer)**: The core summarization engine that generates structured summaries using optimized API calls.
- **DeepEval (Evaluation)**: Evaluates summaries for **accuracy, coherence, and entity density** to ensure high-quality output.
- **Redis (Caching)**: Stores previously generated summaries to improve efficiency and reduce API calls.




	
