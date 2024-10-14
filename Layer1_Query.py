import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import requests
import base64
from dotenv import load_dotenv

from createWebsite import TargetAudienceInsights


load_dotenv()

client = OpenAI()
    
def Image_Generation(prompt):
    response = client.images.generate(
    model="dall-e-2",
    prompt=prompt,
    size="512x512"
    )
    image_url = response.data[0].url
    return image_url

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

class AudienceSample(BaseModel):
    age: int
    gender: str
    location: str
    interest: list
    
class TargetAudienceInsightsClass(BaseModel):
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
                response_format=TargetAudienceInsightsClass
            )
            ret = completion.choices[0].message.parsed

            if ret == None:
                raise Exception("Failed to generate target audience insights.")
            
            return ret
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
def ImageToText(image_path):
    print("image path", image_path)
    
    base64image = encode_image(image_path)


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
                "url":  f"data:image/jpeg;base64,{base64image}"
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
    product_images_url: str
    audience: TargetAudienceInsightsClass

    def process_Images(self) -> list:
        img_inputs = []
        img_inputs.append(ImageToText(self.product_images_url))
        return img_inputs
    
    def image_generation_prompt(self) -> str:
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": "Generate a image prompt for the product {self.product_name}, {self.product_description}."}]
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
        
def image_generation_prompt(product_info: ProductInformation) -> str:
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": f"Generate a image prompt for the product {product_info.product_name}, {product_info.product_description}."}]
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
    
def find_product_information(text: str, picture: str) -> ProductInformation:
    # Messages that will be sent to GPT-4 model
    messages = [{"role": "system", "content": "You are a product analysis expert that provides product information. Find out a possible name and description for the product."}]
    
    messages.append({"role": "user", "content": f"Product initial description: {text}"})

    messages.append({"role": "user", "content": f"The following pictures provide visual context for the product: {ImageToText(picture)}"})

    # Generate output with OpenAI's GPT-4 model using structured parsing
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=ProductInformation
        )
        ret = completion.choices[0].message.parsed 
        if ret == None:
            raise Exception("Failed to generate product name.")
        
        return ret
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")




def Wrapper(textInput: str, pictureInput: str, imageurl: str):
    Info = find_product_information(text=textInput, picture=pictureInput)
    Info.audience = TargetAudienceInsightsClass.find_audience(text=textInput, pictures=pictureInput)
    
    #newimg = Image_Generation(image_generation_prompt(Info))

    # if newimg == None:
    #     raise Exception("Failed to generate product images.")
    # else:
    #     Info.product_images_url = newimg

    result = TargetAudienceInsights(
        age_groups = Info.audience.age_groups,
        gender_distribution = Info.audience.gender_distribution,
        locations = Info.audience.locations,
        interests = Info.audience.interests,
        #images = [Info.product_images_url],
        images = [],
        mainimage = imageurl,
        product = Info.product_name,
        description = Info.product_description
    )
    return result
    
