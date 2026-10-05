# test_gemini.py

from google import genai
from config import GEMINI_API_KEY

print("KEY =", GEMINI_API_KEY[:10])

client = genai.Client(
    api_key=GEMINI_API_KEY
)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Hello"
)

print(response.text)