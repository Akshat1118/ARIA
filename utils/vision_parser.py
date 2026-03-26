"""
ARIA — Vision Parser Utility (Phase 3)
Extracts rich clinical text findings from raw medical scans using Gemini Vision.
This allows the multimodal image data to be consumed smoothly by text-only
downstream agents (like the local DeepSeek model in the uncertainty layer).
"""

import google.generativeai as genai
from PIL import Image
import io

def analyze_medical_image(image_bytes: bytes, model_name: str = "gemini-2.5-flash") -> str:
    """
    Takes raw image bytes, converts to a PIL Image, and uses Gemini
    to extract a structured text report of clinical findings.
    
    Returns:
        A Markdown-formatted string describing the image findings.
    """
    try:
        # Convert raw bytes into a PIL Image format Gemini understands
        img = Image.open(io.BytesIO(image_bytes))
        
        # Initialize the specific model selected by the user in the UI
        model = genai.GenerativeModel(model_name)
        
        prompt = (
            "You are an expert radiologist, dermatologist, and medical image analyst. "
            "Examine this medical scan/image and list all visible clinical findings, "
            "abnormalities, and diagnostic impressions in a clear, structured text format. "
            "If the image is NOT a medical scan, state that clearly and briefly describe what it is."
        )
        
        # Multimodal inference: Pass both the prompt and the PIL Image
        response = model.generate_content([prompt, img])
        return response.text
        
    except Exception as e:
        return f"Error analyzing visual scan: {str(e)}"
