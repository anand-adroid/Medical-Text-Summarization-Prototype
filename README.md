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
OCKER_REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600
LOG_FILE=logs/summary.log
BROWSER=chrome
REACT_APP_API_URL=http://backend:8000

```

### Docker Setup:

# Docker Compose Override Configuration

To configure environment variables, create a `docker-compose.override.yml` file. This file allows you to customize the default settings of your Docker Compose services without modifying the original `docker-compose.yml` file.

---

## Prerequisites

- Docker installed on your machine.

---

## Step 1: Create `docker-compose.override.yml`

Create a new file named `docker-compose.override.yml` in the same directory as your `docker-compose.yml` file.

---

## Step 2: Define Environment Variables

In the `docker-compose.override.yml` file, define the environment variables under the `environment` section of the service. Below is an example configuration:

```yaml
version: '3.8'

services:
  backend:  
    environment:
      - LLM_API_KEY=your_api_key
      - LLM_MODEL=gpt-4-turbo
      - REDIS_URL=redis://127.0.0.1:6379/0
      - DOCKER_REDIS_URL=redis://redis:6379/0
      - CACHE_TTL=3600
      - LOG_FILE=logs/summary.log

  frontend:
    environment:
      - REACT_APP_API_URL=http://backend:8000 
      - BROWSER=chrome
```

## Step 3: Apply the Override

Run the following command to apply the override and start your Docker Compose services:

```
docker-compose up --build -d --verbose
```

This command will start your services with the environment variables defined in the docker-compose.override.yml file.

## Step 4: Verify Configuration

To verify that the environment variables have been correctly applied, you can inspect the environment of the running container:

```
docker exec -it <container_id> printenv
```
Replace <container_id> with the actual container ID of your service.


#### Architecture Overview

![Architecture Diagram](https://github.com/anand-adroid/Medical-Text-Summarization-Prototype/blob/564842a48fa954acd3dbb57c2be70744ba4ded4a/Architecture.png)

### **System Components**
- **Frontend (React)**: Sends clinical notes to the FastAPI backend for processing.
- **FastAPI Backend**: Handles requests, processes clinical notes, generates summaries, and evaluates them.
- **OpenAI API (Summarizer)**: The core summarization engine that generates structured summaries using optimized API calls.
- **DeepEval (Evaluation)**: Evaluates summaries for **accuracy, coherence, and entity density** to ensure high-quality output.
- **Redis (Caching)**: Stores previously generated summaries to improve efficiency and reduce API calls.




	
