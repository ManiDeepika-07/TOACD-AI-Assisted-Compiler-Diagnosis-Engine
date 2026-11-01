import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
   model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Explain what a missing semicolon in C++ means in one simple sentence."
        }
    ]
)

print(response.choices[0].message.content)