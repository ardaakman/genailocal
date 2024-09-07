from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import io
import base64
import requests
import sys

app = FastAPI()

OLLAMA_API_BASE = "http://localhost:11434"  # Adjust if your Ollama API is hosted differently
MODEL_NAME = "llava"  # Adjust based on the model you're using

def encode_image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_image_with_ollama(image: Image.Image, prompt: str) -> str:
    base64_image = encode_image_to_base64(image)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [base64_image]
    }
    
    try:
        response = requests.post(f"{OLLAMA_API_BASE}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")

@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...)):
    # Read the image file
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Process the image with Ollama
    prompt = "Describe in detail what is happening on my screen"
    result = process_image_with_ollama(image, prompt)
    
    return {"result": result}

def test_local_image(image_path: str):
    # Load the local image
    image = Image.open(image_path)
    
    # Process the image with Ollama
    prompt = "Describe in detail what is happening on my screen"
    result = process_image_with_ollama(image, prompt)
    
    print(f"Ollama's description of the image:\n{result}")

if __name__ == "__main__":
    # If run with "python script.py test", it will use the test function
    image_path = "/Users/pawan/Downloads/test-ss.png"  # Replace with your image path
    test_local_image(image_path)