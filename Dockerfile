FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential pkg-config libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

# ...existing code...
RUN pip install --upgrade pip
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt
# ...existing code...

RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]