
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    openssl \
    liblapack-dev \
    libjpeg-dev \
    zlib1g-dev \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
pip uninstall -y uvloop

RUN python -m nltk.downloader punkt
RUN python -m spacy download en_core_web_sm

COPY backend /app/backend

WORKDIR /app/backend

ENV PYTHONPATH="/app"
ENV UVLOOP_DISABLED=1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
