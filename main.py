from fastapi import FastAPI

app = FastAPI(title="My First API")

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"Hello {name}!"}
