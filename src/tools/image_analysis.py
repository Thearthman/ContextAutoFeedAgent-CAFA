import base64
import mimetypes
import os
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from src.llm_client import get_llm

def encode_image(image_path):
    """Encodes a local image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path: str) -> str:
    """
    Analyzes an image file and returns a description.
    """
    print(f"\n[Tool: analyze_image] Analyzing image at: {image_path}...")
    try:
        # Handle potential quotes in path
        image_path = image_path.strip('"').strip("'")
        
        if not os.path.exists(image_path):
            return f"Error: Image file '{image_path}' not found."
            
        # Determine mime type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg" # Default fallback
            
        base64_image = encode_image(image_path)
        
        llm = get_llm()
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Please provide a detailed description of this image. Capture all text, objects, and layout details."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    },
                },
            ]
        )
        
        response = llm.invoke([message])
        return response.content
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def get_image_analysis_tool():
    return Tool(
        name="analyze_image",
        description="Analyze an image file. Input should be the absolute path to the local image file. Use this when the user asks to look at, describe, or analyze an image.",
        func=analyze_image
    )
