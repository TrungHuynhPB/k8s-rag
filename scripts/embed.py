import chromadb

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("docs")

with open("inputs/k8s.txt", "r") as f:
    text = f.read()

collection.add(documents=[text], ids=["k8s"])

print("Embedding inputs.txt stored in Chroma")
