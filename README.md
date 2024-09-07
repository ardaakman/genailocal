AGI hackathon project: auto-completion of text based on the GUI window context using local inference on Intel AI machines.

Inference server 
  1. RESTFUL API 
     2. POST screen context /screenshots -> once every 5 seconds 
     3. POST dialog context /dialog -> once every 1 second 
  2. Websocket for memory updated in real-time, stream tokens to the frontend
     1. source: string  
     2. summary: string 
     3. details: string 
   
  UI 
  1. Each component drop down
     1. App Source name 
     2. Press on it to get the details of it. 