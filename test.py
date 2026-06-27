from dotenv import load_dotenv
from groq import Groq
import os

# Load .env file
load_dotenv()

# Check if key is loaded
api_key = os.getenv("GROQ_API_KEY")

print("API Key Found:", api_key is not None)

if not api_key:
    print("ERROR: GROQ_API_KEY not found in environment")
    exit()

try:
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ]
    )

    print("\nSUCCESS!")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nERROR:")
    print(type(e).__name__)
    print(e)