import os
import google.generativeai as genai

# Retrieve the API key from the environment variable
api_key = os.getenv("GEMINI_API_KEY")
print(api_key)
if not api_key:
    raise ValueError("API key not found. Ensure GEMINI_API_KEY is set as an environment variable.")

# Configure the Generative AI client
genai.configure(api_key=api_key)

# Use the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)
