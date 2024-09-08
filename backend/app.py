import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import json
import base64
import requests
import os
import sys
import asyncio
import random
from typing import List

from model import GeneralistModel, ConversationModel

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

general_agent = GeneralistModel()
ConversationModel = ConversationModel()

HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
print(HISTORY_PATH)
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
        return "Test response for image processing"
    
    try:
        response = requests.post(f"{OLLAMA_API_BASE}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {str(e)}")

def process_image_and_text_local_llm(image: Image.Image, prompt: str, ) -> str:
    base64_image = encode_image_to_base64(image)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [base64_image]
    }
    if TEST:
        return "Test response for image and text processing"
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
    
    # result = process_image_and_text_local_llm(image, prompt)
    encoded_image = encode_image_to_base64(image)
    result = json.loads(general_agent.forward(encoded_image))
    data = {
        "type": "autocomplete",
        "source": source,
        "summary": result[:100] if len(result) > 100 else result,
        "details": result
    }
    # Write to history.json
    with open(HISTORY_PATH, "w") as file:
        json.dump(data, file)

    # This endpoint actually has to return information to the caller.
    return {"result": result}

@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...), source: str = Body(...)):
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name
    
    result = general_agent.forward(tmp_file_path)
    print("Result: ", result)
    # image = Image.open(tmp_file_path)
    # result = await process_image_with_local_llm(image)
    # data = {
    #     "type": "memory",
    #     "source": source,
    #     "summary": result[:100] if len(result) > 100 else result,
    #     "details": result
    # }
    # Write to history.json still. No need to return anything.
    with open(HISTORY_PATH, "w") as file:
        json.dump(result, file)
    return

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    counter = 0
    try:
        while True:
            # Simulate loading
            await manager.send_personal_message({"token": "loading"}, websocket)

            # Check if history.json exists
            if os.path.exists(HISTORY_PATH):
                try:
                    with open(HISTORY_PATH, "r") as file:
                        data = json.loads(file)
                    if not TEST:
                        os.remove(HISTORY_PATH)  # Delete the file after reading
                except json.JSONDecodeError:
                    data = {"error": "Invalid or empty data file"}
                except Exception as e:
                    data = {"error": f"Error reading data: {str(e)}"}
            else:
                data = {
                    "type": "memory",
                    "source": "twitter",
                    "summary": "hello hello",
                    "details": "hello hello hello hello",
                }
                counter += 1

            # Send data
            await manager.send_personal_message(data, websocket)

            # Wait for a random time between 3 to 8 seconds before the next iteration
            await asyncio.sleep(random.uniform(3, 8))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    # If test is specified, make the global "test" flag true.
    if "test" in sys.argv:
        TEST = True
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)