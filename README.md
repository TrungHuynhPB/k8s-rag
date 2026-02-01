docker compose up -d
docker exec -it ollama ollama pull tinyllama
docker exec -it ollama ollama run tinyllama
uvicorn scripts.app:app --reload

#test
curl -X POST "http://127.0.0.1:8000/query" -G --data-urlencode "q=What is Kubernetes?"

https://learn.nextwork.org/projects/static/ai-devops-kubernetes/unframed/architecture-diagram-eraser.png

Part 3

kubectl exec -it ollama-fdf769cb-rzzdq -- ollama pull tinyllama
kubectl apply -f deployment.yaml
kubectl rollout restart deployment rag-app-deployment
kubectl get pods
curl -X POST "http://<KUBECTL_IP>:30816/query" \
  -G --data-urlencode "q=What is Kubernetes?"
