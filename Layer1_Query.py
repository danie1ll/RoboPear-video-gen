import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import requests
import base64

# Load API key
with open('Lorenzo.txt', 'r') as file:
    api_key = file.read().strip()  # Read the file and strip whitespace 
client = OpenAI(api_key=api_key)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
class AudienceSample(BaseModel):
    age: int
    gender: str
    location: str
    interest: list
    
class TargetAudienceInsights(BaseModel):
    age_groups: List[str]
    gender_distribution: List[str]
    locations: List[str]
    interests: List[str]

    @classmethod
    def find_audience(cls, text: Optional[str] = None, voice: Optional[str] = None, pictures: Optional[str] = None, videos: Optional[str] = None):
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": "You are a product analysis expert that provides target audience insights, market discovery, and video suggestions. Find out the possible audience in terms of age group, gender, geographic location, and interests."}]
        
        # Append product description text, if available
        if text:
            messages.append({"role": "user", "content": f"Product description: {text}"})
        if pictures:
            messages.append({"role": "user", "content": f"The following pictures provide visual context for the product: {pictures}"})
        if videos:
            messages.append({"role": "user", "content": f"The following videos give an overview of the product: {videos}"})
        if voice:
            messages.append({"role": "user", "content": f"The following voice message offers additional product context: {voice}"})

        # Generate output with OpenAI's GPT-4 model using structured parsing
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=TargetAudienceInsights
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            return f"Error generating response: {str(e)}"
def ImageToText(image_path):
    print("image path", image_path)
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "What’s in this image? Be very detailed with what the object looks like, what could be its purpose, and what are its shape and peculiarities"},
            {
            "type": "image_url",
            "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
            },
            },
        ],
        }
    ]
    )
    return response.choices[0].message.content



class ProductInformation(BaseModel):
    product_name: str
    product_description: str
    product_images_url: List[str]
    audience: TargetAudienceInsights

    def process_Images(self) -> list:
        img_inputs = []
        for image in self.product_images_url:
            img_inputs.append(ImageToText(image))
        return img_inputs
    
    def generate_target_product_description(self, AudienceSample) -> str:
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": "Generate a product description targeted to people that are {AudienceSample.gender}, {AudienceSample.age} years old, live in {AudienceSample.location}, and have the following interests: {AudienceSample.interest}."}]
        # Generate output with OpenAI's GPT-4 model using structured parsing
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=ProductInformation
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def find_product_information(self, text: Optional[str] = None, voice: Optional[str] = None, pictures: Optional[str] = None, videos: Optional[str] = None):
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": "You are a product analysis expert that provides product information. Find out a possible name and description for the product."}]
        
        if text:
            messages.append({"role": "user", "content": f"Product initial description: {text}"})
        if pictures:
            for image in pictures:
                print("pic reading")
                messages.append({"role": "user", "content": f"The following pictures provide visual context for the product: {ImageToText(image)}"})

        # Generate output with OpenAI's GPT-4 model using structured parsing
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=ProductInformation
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            return f"Error generating response: {str(e)}"




# Example usage
text_input = "Bubble tea"
# Correctly formatted file path
pictures_input = ["C:\\Users\\botlo\\Desktop\\PEARVC\\RoboPear-video-gen\\generatedWebsites\\imgTest1.jpg"]
print("runnning image to text")
print(ImageToText(pictures_input[0]))
videos_input = None  # Example: URL or file paths for videos.
voice_input = None  # Example: A transcription of the voice message.

# Create a ProductInformation instance
audience = TargetAudienceInsights.find_audience(text=text_input, pictures=pictures_input)

Info = ProductInformation(
    product_name=text_input,
    product_description="A delicious drink made with tea, milk, and tapioca pearls.",  # Provide a description
    product_images_url=pictures_input,  # Pass an empty list
    audience=audience  # Audience is already obtained
)

output = Info.find_product_information(text=text_input, pictures=pictures_input)

# Print the instance to see its contents
print(output.product_name)  # Print the output from the find_product_information method
print(output.product_description)