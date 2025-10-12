# backend/gemini_client.py
import os
from dotenv import load_dotenv
import logging
from google import genai

# Load .env automatically
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set GOOGLE_API_KEY in the environment or .env file")

genai_client = genai.Client(api_key=API_KEY)

MODEL_DEFAULT = "gemini-2.0-flash-001"

logger = logging.getLogger(__name__)

def chat_send(model: str = MODEL_DEFAULT, prompt: str = "") -> str:
    """
    Sends a prompt to Gemini and returns the text output.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    try:
        chat = genai_client.chats.create(model=model)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        logger.error("Gemini request failed: %s", e)
        return ""  # fallback empty string
