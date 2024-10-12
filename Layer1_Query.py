from openai import OpenAI
client = OpenAI(api_key="sk-5bxhWgAQwoyIcLe-bZvNy0HhJhWl8Eu2ii7w5eoWpHT3BlbkFJvu6M8LGXZ9akWmhYEU2rlC8tbetSnCfDCPjmKtOQ8A")
import os
from pydantic import BaseModel
from pydantic import BaseModel
from typing import List, Optional

class TargetAudienceInsights(BaseModel):
    age_groups: List[str]
    gender_distribution: List[str]
    locations: List[str]
    interests: List[str]
    
    def find_audience(text: Optional[str] = None, voice: Optional[str] = None, pictures: Optional[str] = None, videos: Optional[str] = None):
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": "You are a product analysis expert that provides target audience insights, market discovery, and video suggestions. Find out the possible audience in terms of age group, gender, geographic location, and interests."}]
        # Append product description text, if available
        if text:
            messages.append({"role": "user", "content": f"Product description: {text}"})
        # Append other inputs like voice, pictures, and videos with appropriate context
        if pictures:
            messages.append({"role": "user", "content": f"The following pictures provide visual context for the product: {pictures}"})
        if videos:
            messages.append({"role": "user", "content": f"The following videos give an overview of the product: {videos}"})
        if voice:
            messages.append({"role": "user", "content": f"The following voice message offers additional product context: {voice}"})

        # Generate output with OpenAI's GPT-4 model using structured parsing
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",  # Use the correct model name
                messages=messages,
                response_format=TargetAudienceInsights  # Use your structured output model
            )
            
            # Extract the parsed response
            return completion.choices[0].message.parsed  # This will be of type TargetAudienceInsights
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
class ProductInformation(BaseModel):
    product_name: str
    product_description: str
    product_url: str
    product_images_url: list
    product_videos_url: list
    audience : TargetAudienceInsights
    
    def find_product_information(text: Optional[str] = None, voice: Optional[str] = None, pictures: Optional[str] = None, videos: Optional[str] = None):
    

class TargetAudienceInsights(BaseModel):
    age_groups: List[str]
    gender_distribution: List[str]
    locations: List[str]
    interests: List[str]
    
    def find_audience(text: Optional[str] = None, voice: Optional[str] = None, pictures: Optional[str] = None, videos: Optional[str] = None):
        # Messages that will be sent to GPT-4 model
        messages = [{"role": "system", "content": "You are a product analysis expert that provides target audience insights, market discovery, and video suggestions. Find out the possible audience in terms of age group, gender, geographic location, and interests."}]
        
        # Append product description text, if available
        if text:
            messages.append({"role": "user", "content": f"Product description: {text}"})
        # Append other inputs like voice, pictures, and videos with appropriate context
        if pictures:
            messages.append({"role": "user", "content": f"The following pictures provide visual context for the product: {pictures}"})
        if videos:
            messages.append({"role": "user", "content": f"The following videos give an overview of the product: {videos}"})
        if voice:
            messages.append({"role": "user", "content": f"The following voice message offers additional product context: {voice}"})

        # Generate output with OpenAI's GPT-4 model using structured parsing
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",  # Use the correct model name
                messages=messages,
                response_format=TargetAudienceInsights  # Use your structured output model
            )
            
            # Extract the parsed response
            return completion.choices[0].message.parsed  # This will be of type TargetAudienceInsights
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
class IsEnoughData(BaseModel):
    is_enough_data: bool
    reason: str
    suggestions: Optional[List[str]]

    def Checkmarck(self)


# Example usage:
text_input = "Bubble tea"
pictures_input = None  # Example: URL or file paths for pictures.
videos_input = None  # Example: URL or file paths for videos.
voice_input = None  # Example: A transcription of the voice message.

TargetAudienceInsights.analyze_product_and_generate_outputs(text=text_input, pictures=pictures_input, videos=videos_input, voice=voice_input)
print(output)
