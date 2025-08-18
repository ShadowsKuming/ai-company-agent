import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

load_dotenv()

# API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# LLM Models
def get_gemini_model():
    """Get Gemini Pro model (default)"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment")
    return genai.GenerativeModel('gemini-2.5-pro')

def get_openai_model():
    """Get ChatGPT-4o model (alternative)"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment")
    return OpenAI(api_key=OPENAI_API_KEY)

# Default LLM (Gemini Pro)
try:
    default_llm = get_gemini_model()
    llm_type = "gemini"
except ValueError:
    try:
        default_llm = get_openai_model()
        llm_type = "openai"
    except ValueError:
        raise ValueError("No valid LLM API key found")

# Legacy support for smolagents
HF_TOKEN = os.environ.get("HF_TOKEN")
HF_MODEL = os.environ.get("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

if HF_TOKEN:
    from smolagents import InferenceClientModel
    llm = InferenceClientModel(
        model_id=HF_MODEL,
        token=HF_TOKEN
    )
