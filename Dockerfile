FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y build-essential pkg-config libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

EXPOSE 8501

CMD ["streamlit", "run", "src/chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]