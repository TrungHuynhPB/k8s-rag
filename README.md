# K8s RAG - Kubernetes RAG API Project

A comprehensive project demonstrating how to build, containerize, and deploy a Retrieval-Augmented Generation (RAG) API using FastAPI, Docker, and Kubernetes. This project follows a multi-part tutorial that progresses from local development to production deployment.

## Project Overview

This project implements a RAG (Retrieval-Augmented Generation) API that:
- Uses **ChromaDB** for vector storage and document retrieval
- Uses **Ollama** with the `tinyllama` model for LLM inference
- Provides a **FastAPI** REST API for querying the knowledge base
- Supports adding new content to the knowledge base dynamically

## Architecture

The project uses a **two-container architecture**:
1. **Ollama Container**: Runs the Ollama service for LLM inference
2. **RAG API Container**: Runs the FastAPI application that handles queries and manages the vector database

## Project Structure

```
k8s-rag/
├── scripts/
│   ├── app.py              # FastAPI application with /query and /add endpoints
│   ├── embed.py            # Script to embed documents into ChromaDB
│   └── chroma_connection.py
├── inputs/
│   └── k8s.txt            # Knowledge base content (Kubernetes documentation)
├── db/                    # ChromaDB persistent storage
├── Dockerfile             # Container image for RAG API
├── docker-compose.yml     # Docker Compose configuration (Part 2)
├── deployment.yaml        # Kubernetes deployment for RAG API (Part 3)
├── service.yaml           # Kubernetes service for RAG API (Part 3)
├── ollama-deployment.yaml # Kubernetes deployment for Ollama (Part 3)
├── ollama-service.yaml    # Kubernetes service for Ollama (Part 3)
└── pyproject.toml         # Python dependencies

```

## Part 1: Build a RAG API with FastAPI

In this part, we built the RAG API locally using FastAPI.

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

2. Start Ollama locally:
   ```bash
   docker compose up -d
   docker exec -it ollama ollama pull tinyllama
   ```

3. Embed documents into ChromaDB:
   ```bash
   python -m scripts.embed
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn scripts.app:app --reload
   ```

### Testing

Test the API:
```bash
curl -X POST "http://127.0.0.1:8000/query" -G --data-urlencode "q=What is Kubernetes?"
```

### API Endpoints

- `GET /health` - Health check endpoint
- `POST /query?q=<question>` - Query the knowledge base
- `POST /add?text=<content>` - Add new content to the knowledge base

## Part 2: Containerize a RAG API with Docker

In this part, we containerized the application using **Docker Compose with 2 containers**:
- **Ollama container**: Runs the Ollama service
- **RAG API container**: Runs the FastAPI application

### Architecture

The `docker-compose.yml` defines two services:
- `ollama`: Official Ollama image, exposed on port 11434
- `api`: Custom-built RAG API image, exposed on port 8000

The RAG API container connects to Ollama via the service name `ollama` using the environment variable `OLLAMA_HOST=http://ollama:11434`.

### Usage

1. Build and start containers:
   ```bash
   docker compose up -d
   ```

2. Pull the LLM model in the Ollama container:
   ```bash
   docker exec -it ollama ollama pull tinyllama
   ```

3. Test the API:
   ```bash
   curl -X POST "http://127.0.0.1:8000/query" -G --data-urlencode "q=What is Kubernetes?"
   ```

### Dockerfile

The `Dockerfile`:
- Uses Python 3.13-slim base image
- Installs dependencies (FastAPI, Uvicorn, ChromaDB, Ollama)
- Copies application files and input documents
- Runs the embedding script during build
- Exposes port 8000 and runs the FastAPI server

## Part 3: Deploy a RAG API to Kubernetes

In this part, we deployed the application to Kubernetes using **separate deployments for each container**:
- **Ollama Deployment**: Kubernetes deployment for the Ollama service
- **RAG API Deployment**: Kubernetes deployment for the FastAPI application

### Architecture

The Kubernetes setup includes:
- `ollama-deployment.yaml`: Deployment for Ollama container
- `ollama-service.yaml`: Service exposing Ollama internally
- `deployment.yaml`: Deployment for RAG API container
- `service.yaml`: NodePort service exposing RAG API externally

### Prerequisites

- Kubernetes cluster running
- `kubectl` configured to access your cluster
- Docker image `k8s-rag-api:0.1.0` built and available (or use `imagePullPolicy: Never` for local images)

### Deployment Steps

1. Deploy Ollama:
   ```bash
   kubectl apply -f ollama-deployment.yaml
   kubectl apply -f ollama-service.yaml
   ```

2. Pull the LLM model in the Ollama pod:
   ```bash
   kubectl exec -it <ollama-pod-name> -- ollama pull tinyllama
   ```

3. Deploy the RAG API:
   ```bash
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

4. Check deployment status:
   ```bash
   kubectl get pods
   kubectl get services
   ```

5. Get the NodePort for the RAG API service:
   ```bash
   kubectl get service rag-app-service
   ```

6. Test the API (replace `<KUBECTL_IP>` and port with your cluster's IP and NodePort):
   ```bash
   curl -X POST "http://<KUBECTL_IP>:<NODE_PORT>/query" \
     -G --data-urlencode "q=What is Kubernetes?"
   ```

### Restart Deployment

To restart the RAG API deployment after changes:
```bash
kubectl rollout restart deployment rag-app-deployment
```

## Part 4: Automate Testing with GitHub Actions

This part covers setting up CI/CD pipelines with GitHub Actions for automated testing and deployment.

## Key Features

- **Vector Search**: Uses ChromaDB for semantic search over documents
- **LLM Integration**: Integrates with Ollama for generating answers
- **RESTful API**: FastAPI provides clean REST endpoints
- **Containerized**: Fully containerized with Docker
- **Kubernetes Ready**: Deployed and orchestrated with Kubernetes
- **Persistent Storage**: ChromaDB data persists across container restarts

## Environment Variables

- `OLLAMA_HOST`: URL of the Ollama service (default: `http://ollama:11434`)
- `CHROMA_TELEMETRY`: Disable ChromaDB telemetry (set to `false`)
- `MODEL_NAME`: Ollama model to use (default: `tinyllama`)
- `USE_MOCK_LLM`: Set to `1` to use mock mode (returns context directly without LLM)

## Dependencies

- Python 3.13+
- FastAPI
- Uvicorn
- ChromaDB
- Ollama Python client
- Docker & Docker Compose
- Kubernetes (for Part 3)

## Notes

- The embedding script (`scripts/embed.py`) runs during Docker build to pre-populate the vector database
- ChromaDB data is stored in the `./db` directory and persists in the container
- The two-container architecture allows for independent scaling and management of the LLM service and API
