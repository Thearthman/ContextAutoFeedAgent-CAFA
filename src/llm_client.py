from langchain_openai import ChatOpenAI
from src.config import LLM_SERVER_URL, LLM_API_KEY, MODEL_NAME

def get_llm():
    """
    Returns a configured LangChain ChatOpenAI client pointing to the local llama-server.
    """
    llm = ChatOpenAI(
        base_url=LLM_SERVER_URL,
        api_key=LLM_API_KEY,
        model=MODEL_NAME,
        temperature=0.7,
        streaming=True
    )
    return llm
