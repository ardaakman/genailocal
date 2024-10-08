from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.websocket("/")  # Changed from "/ws" to "/"
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate loading
            await websocket.send_json({"type": "loading"})
            await asyncio.sleep(2)  # 2 second delay

            # Generate fake data
            sources = ["Twitter", "News", "Reddit", "Blog"]
            memory_data = {
                "type": "memory",
                "source": random.choice(sources),
                "summary": f"This is a summary of event {random.randint(1, 100)}",
                "details": f"These are the details of event {random.randint(1, 100)}. " * 5  # Repeated for length
            }
            
            autocompletion_data = {
                "type": "autocompletion",
                "summary": f"This is an autocompletion of event {random.randint(1, 100)}",
            }

            # Choose between memory_data and autocompletion_data with memory being 5 times more likely
            data = random.choices([memory_data, autocompletion_data], weights=[5, 1])[0]
            
            # Send data
            await websocket.send_json(data) 
            await asyncio.sleep(random.uniform(3, 8))  # Random delay between 3 to 8 seconds
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)