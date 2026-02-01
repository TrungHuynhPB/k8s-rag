import requests
import time
import subprocess
import sys
import os
import signal
from pathlib import Path

def wait_for_server(url: str, max_retries: int = 30, delay: float = 1.0):
    """Wait for the server to be available."""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        if i < max_retries - 1:
            time.sleep(delay)
    return False

def ensure_data_loaded(server_url: str):
    """Ensure the Kubernetes data is loaded into the knowledge base."""
    # Check if data exists by querying
    try:
        response = requests.post(f"{server_url}/query?q=Kubernetes")
        if response.status_code == 200:
            answer = response.json().get("answer", "")
            # If we get a meaningful answer with Kubernetes content, data is likely loaded
            if len(answer) > 10 and "kubernetes" in answer.lower():
                print(f"Data appears to be loaded (answer preview: {answer[:50]}...)")
                return True
    except Exception as e:
        print(f"Warning: Could not verify existing data: {e}")
    
    # Try to load the data
    try:
        with open("inputs/k8s.txt", "r") as f:
            text = f.read()
        
        # Use form data for POST request
        response = requests.post(f"{server_url}/add", data={"text": text})
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("Data loaded into knowledge base")
                # Give it a moment to be indexed
                time.sleep(1)
                return True
            else:
                print(f"Failed to load data: {result}")
    except Exception as e:
        print(f"Warning: Could not load data: {e}")
    
    return False

def start_server():
    """Start the FastAPI server in the background."""
    # Set USE_MOCK_LLM to avoid needing Ollama running
    env = os.environ.copy()
    env["USE_MOCK_LLM"] = "1"
    
    # Start uvicorn server
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "scripts.app:app", "--host", "127.0.0.1", "--port", "8000"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        raise Exception("uvicorn not found. Make sure dependencies are installed: pip install fastapi uvicorn chromadb ollama")
    except Exception as e:
        raise Exception(f"Failed to start server: {e}. Make sure dependencies are installed.")
    
    return process

def test_kubernetes_query():
    server_url = "http://127.0.0.1:8000"
    health_url = f"{server_url}/health"
    server_process = None
    
    # Check if server is already running
    if not wait_for_server(health_url, max_retries=3, delay=0.5):
        print("Server not running, starting it...")
        server_process = start_server()
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still alive
        if server_process.poll() is not None:
            # Process has already terminated, get the output
            stdout, _ = server_process.communicate()
            error_msg = f"Server process exited immediately. Output:\n{stdout}"
            raise Exception(error_msg)
        
        # Wait for server to be ready
        if not wait_for_server(health_url, max_retries=30, delay=1.0):
            # Try to get any error output
            error_output = ""
            try:
                # Check if process died
                if server_process.poll() is not None:
                    # Process has terminated, read all output
                    output, _ = server_process.communicate(timeout=2)
                    error_output = output if output else "No output from server process"
                else:
                    # Process still running but not responding
                    # Try to read available output
                    import select
                    if hasattr(select, 'select') and server_process.stdout:
                        ready, _, _ = select.select([server_process.stdout], [], [], 0.1)
                        if ready:
                            output = server_process.stdout.read(4096)
                            if output:
                                error_output = output
            except Exception as e:
                error_output = f"Could not read server output: {e}"
            
            if server_process:
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()
            
            error_msg = "Failed to start server or server not responding after 30 seconds"
            if error_output:
                error_msg += f"\nServer error output:\n{error_output}"
            raise Exception(error_msg)
        print("Server is ready!")
    
    try:
        # Ensure data is loaded
        ensure_data_loaded(server_url)
        
        response = requests.post(f"{server_url}/query?q=What is Kubernetes?")
        
        if response.status_code != 200:
            raise Exception(f"Server returned {response.status_code}: {response.text}")
        
        answer = response.json()["answer"]
        
        # Validate that we got a meaningful answer
        assert len(answer) > 0, "Answer is empty"
        assert "kubernetes" in answer.lower(), f"Answer should mention Kubernetes. Got: {answer[:200]}"
        
        # Check for key concepts - be flexible since ChromaDB might return different chunks
        # The text contains "orchestration" but the semantic search might return a different chunk
        keywords_found = []
        if "orchestration" in answer.lower():
            keywords_found.append("orchestration")
        if "software" in answer.lower() or "company" in answer.lower():
            keywords_found.append("software/company")
        if "cloud" in answer.lower() or "computing" in answer.lower():
            keywords_found.append("cloud/computing")
        if "israel" in answer.lower() or "israeli" in answer.lower():
            keywords_found.append("israel/israeli")
        
        # At least one relevant keyword should be present
        assert len(keywords_found) > 0, f"Answer should contain relevant keywords. Full answer: {answer}"
        
        print(f"✅ Kubernetes query test passed. Found keywords: {', '.join(keywords_found)}")
        print(f"   Answer preview: {answer[:150]}...")
    finally:
        # Clean up: terminate the server if we started it
        if server_process:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    test_kubernetes_query()
    print("All semantic tests passed!")
