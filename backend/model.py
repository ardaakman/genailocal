import base64
import os

import requests
import torch
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from prompting import conversation_prompt, generalist_prompt
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer

# Load environment variables from .env file
load_dotenv()

class ChatMessage(BaseModel):
    sender: str
    message: str


class Conversation(BaseModel):
    person_we_are_corresponding_to: str
    messages: list[ChatMessage]


class GeneralistReasoning(BaseModel):
    source: str
    summary: str
    details: str


class OllamaModel:
    def __init__(self, *, model_name, ollama_endpoint):
        self.model_name = model_name
        self.endpoint = ollama_endpoint

    def forward(self, prompt: str) -> str:
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        try:
            response = requests.post(f"{self.endpoint}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            raise Exception(f"Error communicating with Ollama: {str(e)}")


class PhiVLMModel:
    def __init__(self):
        self.model_name = "microsoft/Phi-3.5-vision-instruct"

    def load(self):
        # Load model directly
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            _attn_implementation="eager",
        )

        self.processor = AutoProcessor.from_pretrained(
            self.model_name, trust_remote_code=True, torch_dtype=torch.float16
        )

        self.generation_args = {
            "max_new_tokens": 2000,
            "temperature": 0.0,
            "do_sample": False,
        }

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def format_inputs_to_message(self, image: str, text_prompt: str):
        messages = [{"role": "user", "content": f"<|image_1|>\n{text_prompt}"}]
        prompt = self.processor.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image = Image.open(image)
        inputs = self.processor(prompt, [image], return_tensors="pt").to(self.device)

        return inputs

    def forward(self, image):
        inputs = self.format_inputs_to_message(image, generalist_prompt)
        generate_ids = self.model.generate(
            **inputs,
            eos_token_id=self.processor.tokenizer.eos_token_id,
            **self.generation_args,
        )

        # remove input tokens
        generate_ids = generate_ids[:, inputs["input_ids"].shape[1] :]
        response = self.processor.batch_decode(
            generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        return response

# Set the API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class GPTModel:
    def __init__(self):
        # self.model = "gpt-4o-mini-2024-07-18"
        self.model = "gpt-4o-2024-08-06"
        self.client = OpenAI()

    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def format_inputs_to_message(self, image, prompt):
        formatted_image = (
            image
            if image.startswith("http")
            else f"data:image/jpeg;base64,{self.encode_image(image)}"
        )
        image_dict = {"url": formatted_image}
        prompt_dict = {"type": "text", "text": prompt}
        image_dict = {"type": "image_url", "image_url": image_dict}
        user_content = [prompt_dict, image_dict]
        messages = [{"role": "user", "content": user_content}]
        return messages

    def forward(self, image, prompt):
        messages = self.format_inputs_to_message(image, prompt)
        response = self.client.beta.chat.completions.parse(
            model=self.model, messages=messages
        )
        return response.choices[0]


class GeneralistModel(GPTModel):
    def forward(self, image):
        messages = self.format_inputs_to_message(image, generalist_prompt)
        response = self.client.beta.chat.completions.parse(
            model=self.model, response_format=GeneralistReasoning, messages=messages
        )
        return response.choices[0].message.content


class ConversationModel(GPTModel):
    def __init__(self):
        super().__init__()
        self.model = "gpt-4o-2024-08-06"

    def forward(self, image):
        messages = self.format_inputs_to_message(image, conversation_prompt)
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            response_format=Conversation,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content
