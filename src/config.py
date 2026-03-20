import os

# Configuration for the LLM Server
LLM_SERVER_URL = os.getenv("LLM_SERVER_URL", "http://localhost:8080/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-no-key-required") # llama-server doesn't strictly require one usually

# Model Name (can be anything for llama-server usually, but good to be specific if needed)
MODEL_NAME = "local-model"

# Vector Store Path
VECTOR_STORE_PATH = os.path.join(os.getcwd(), "chroma_db")
