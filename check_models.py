import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the genai library with your API key
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file.")
    else:
        genai.configure(api_key=api_key)

        print("Available Gemini models for your API key:")
        print("-" * 35)
        
        # List all models and print the ones that support 'generateContent'
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(model.name)
        
        print("-" * 35)
        print("Copy one of the model names from this list and paste it into your query_graph.py script.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure your GOOGLE_API_KEY in the .env file is correct.")