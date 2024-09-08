import base64
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from prompting import conversation_prompt, generalist_prompt

# Load environment variables from .env file
load_dotenv()

# Set the API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


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
