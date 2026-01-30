FROM python:3.13-slim
WORKDIR /app
# ---- env ----
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=http://ollama:11434

ENV PYTHONPATH=/app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# ---- app files ----
COPY scripts ./scripts
COPY inputs ./inputs

RUN pip install fastapi uvicorn chromadb ollama
RUN python -m scripts.embed
EXPOSE 8000
CMD ["uvicorn", "scripts.app:app", "--host", "0.0.0.0", "--port", "8000"]
