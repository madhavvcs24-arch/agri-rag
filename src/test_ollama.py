
from ollama import chat

MODEL = "qwen2.5:3b-instruct"

print("Testing Ollama connection...")
print(f"Model: {MODEL}")

response = chat(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful agricultural assistant."
        },
        {
            "role": "user",
            "content": "Explain in two simple sentences why farmers need to manage weeds in rice fields."
        }
    ],
    options={
        "temperature": 0.2,
        "num_predict": 150
    }
)

print("\nMODEL RESPONSE")
print("=" * 50)
print(response.message.content)

print("\nOllama generation successful!")
