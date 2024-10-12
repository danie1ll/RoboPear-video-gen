from openai import OpenAI
from PIL import Image
import requests
import base64
OPENAI_API_KEY = 'x'
client = OpenAI(api_key=OPENAI_API_KEY)


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def understand_product(image_path):
  # Function to encode the image

  # Getting the base64 string
  base64_image = encode_image(image_path)

  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
  }

  payload = {
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Analyze the given advertisement image and generate a suitable background based on the following criteria: Theme: Identify the overall theme or industry of the advertisement (e.g., food and beverage, technology, fashion, etc.). "
                    "Mood: Determine the emotional tone the image conveys (e.g., energetic, calm, luxurious, eco-friendly)."
                    "Color Palette: Analyze the dominant colors used in the original image."
                    "Setting: Identify the environment or setting implied by the advertisement (e.g., urban, nature, abstract)."
                    "Key Visual Elements: Note any significant visual motifs or symbols present."
                    "Target Audience: Infer the likely target demographic based on the image style and content."
                    "Brand Identity: Identify any visual cues that reflect the brand's identity or values."
                    
                    "Based on this analysis, generate a background image that:"
                    
                    "Scene: Creates an appropriate setting that complements the identified theme and mood."
                    "Lighting: Incorporates lighting effects that enhance the desired atmosphere."
                    "Color Scheme: Uses a color palette that aligns with the original image but focuses on tones suitable for a background."
                    "Focal Area: Includes a balanced composition with areas where product images or text can be overlaid without obstruction."
                    "Texture and Depth: Adds subtle textures or depth to create visual interest without overpowering potential foreground elements. "
                    "Style Consistency: Matches the overall style (e.g., realistic, illustrated, minimalist) of the original advertisement."
                    "Versatility: Ensures the background is adaptable for various media formats (web, print, mobile)."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
  print(response["choices"][0]['message']['content'])
  return response["choices"][0]['message']['content']

#prompt = "Create a vibrant advertisement image featuring a Guayaki Organic Yerba Mate can. The can should be bright yellow with green accents, placed in a lush, misty rainforest setting. Rays of sunlight filter through the canopy, illuminating the can. Around the can, show energetic young people engaged in outdoor activities like hiking or yoga. Include elements that suggest vitality and enlightenment, such as a radiant glow around the can or floating tea leaves. Use a color palette dominated by greens and golds to evoke nature and energy. The overall mood should be invigorating and refreshing, capturing the 'Enlighten Mint' flavor and organic essence of the product."

def create_image(prompt_text):
  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt_text,
    size="1024x1024",
    quality="standard",
    n=1,
  )
  image_url=response.data[0].url
  return image_url

def download_image(url):
  # Download the image
  response = requests.get(url)

  # Check if the request was successful
  if response.status_code == 200:
    # Open a file in binary write mode
    with open("background_image4.png", "wb") as file:
      # Write the content of the response to the file
      file.write(response.content)
    print("Image downloaded successfully.")
  else:
    print("Failed to download the image.")

prompt = understand_product(image_path="yerba_mate_mint.png")
url_image = create_image(prompt_text=prompt)
download_image(url=url_image)