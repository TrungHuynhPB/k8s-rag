docker compose up -d
docker exec -it ollama ollama pull tinyllama
docker exec -it ollama ollama run tinyllama
uvicorn scripts.app:app --reload

#test
curl -X POST "http://127.0.0.1:8000/query" -G --data-urlencode "q=What is Kubernetes?"
