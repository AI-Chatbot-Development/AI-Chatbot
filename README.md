# AI Agent Chatbot

This is an AI agent chatbot built with Streamlit and containerized with Docker.

## Prerequisites

- Docker

## How to run

1. **Build and run the Docker container with Docker Compose:**

   ```bash
   docker-compose up --build
   ```

   You can then access the chatbot at `http://localhost:8501`.

## Managing Dependencies

To add a new package, add it to the `requirements.txt` file. Then, rebuild the Docker image:

```bash
docker-compose up --build
```

### With Docker Engine

1. **Build the Docker image:**

   ```bash
   docker build -t ai-chatbot .
   ```

2. **Run the Docker container:**

   ```bash
   docker run -p 8501:8501 ai-chatbot
   ```
