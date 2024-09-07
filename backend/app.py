from fastapi import FastAPI, File, UploadFile, HTTPException, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import json
import base64
import requests
import os
import asyncio
import random
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_API_BASE = "http://localhost:11434"
MODEL_NAME = "llava"
TEST = False

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

manager = ConnectionManager()

def encode_image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

async def process_image_with_local_llm(image: Image.Image) -> str:
    base64_image = encode_image_to_base64(image)
    payload = {
        "model": MODEL_NAME,
        "prompt": "Describe in detail what is happening on my screen",
        "images": [base64_image]
    }
    if TEST:
        return 
    
    try:
        response = requests.post(f"{OLLAMA_API_BASE}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")

def process_image_and_text_local_llm(prompt: str, image: Image.Image) -> str:
    base64_image = encode_image_to_base64(image)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [base64_image]
    }
    if TEST:
        return {"source": "test", "summary": "test", "details": "test"}
    try:
        response = requests.post(f"{OLLAMA_API_BASE}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")

@app.post("/inference")
async def process_prompt(file: UploadFile = File(...), prompt: str = Body(...), source: str = Body(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    result = process_image_and_text_local_llm(prompt, image)
    # Write to history.json
    with open("history.json", "w") as file:
        json.dump({"source": result.source, "summary": result.summary, "details": result.details}, file)

    # This endpoint actually has to return information to the caller.
    return {"result": result}
@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...), source: str = Body(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    result = await process_image_with_local_llm(image)
    # Write to history.json still. No need to return anything.
    with open("history.json", "w") as file:
        json.dump({"source": result.source, "summary": result.summary, "details": result.details}, file)
    return

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Simulate loading
            await manager.send_personal_message({"token": "loading"}, websocket)

            # Check if history.json exists
            if os.path.exists("history.json"):
                with open("history.json", "r") as file:
                    data = json.load(file)
                if not(TEST):
                    os.remove("history.json")  # Delete the file after reading
            else:
                await asyncio.sleep(2)  # Sleep for 2 seconds if file doesn't exist
                continue  # Skip to next iteration of the loop

            # Send data
            await manager.send_personal_message(data, websocket)
            await asyncio.sleep(random.uniform(3, 8))  # Random delay between 3 to 8 seconds

    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    # If test is specified, make the global "test" flag true.
    if "test" in sys.argv:
        TEST = True
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)