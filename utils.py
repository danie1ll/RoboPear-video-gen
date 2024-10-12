client = OpenAI(api_key="sk-5bxhWgAQwoyIcLe-bZvNy0HhJhWl8Eu2ii7w5eoWpHT3BlbkFJvu6M8LGXZ9akWmhYEU2rlC8tbetSnCfDCPjmKtOQ8A")

def ImageToText(image_path):
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "What’s in this image? Be very detailed with what the object looks like, what could be its purpose, and what are its shape and peculiarities"},
            {
            "type": "image_url",
            "image_url": {
                "url": image_path,
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )
    return response.choices[0].message.content