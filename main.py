from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
import os
import cloudinary
import cloudinary.uploader
from typing import Optional
from pydantic import BaseModel
from ml_flows import run_flow, poll_flow
import logging
from dotenv import load_dotenv

load_dotenv()

# Initialize Cloudinary
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

app = FastAPI()

# Define a route for the homepage to upload files
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <h2>Upload Image</h2>
    <form action="/upload-image/" enctype="multipart/form-data" method="post">
        <input name="image" type="file" accept="image/*" required>
        <button type="submit">Upload Image</button>
    </form>

    <h2>Upload Text</h2>
    <form action="/upload-text/" method="post">
        <input name="text" type="text" placeholder="Enter your text" required>
        <button type="submit">Upload Text</button>
    </form>

    <h2>Generate Video</h2>
    <form action="/generate-video/" method="post" enctype="application/x-www-form-urlencoded">
        <input name="image_url" type="text" placeholder="Enter image URL" required>
        <button type="submit">Generate Video</button>
    </form>
    """
        # <input name="holiday" type="text" placeholder="Enter holiday" required>
        # <input name="season" type="text" placeholder="Enter season" required>

# Define a route to handle the uploaded image
@app.post("/generate-video/")
async def generate_video(image: UploadFile = File(...)):
    
    # Process the uploaded image
    contents = await image.read()
    
    # Save the image in the 'images' folder
    image_path = os.path.join("images", image.filename)
    with open(image_path, "wb") as f:
        f.write(contents)
    
    logging.info(f"Saved image: {image.filename}")
    print(f"Saved image: {image.filename}")
    
    holiday = "Easter"
    season = "winter"
    video_prompt = "light changes slightly"
    scene_prompt = f"A product placed into a center of a composition on a wooden table. The product is surrounded by {holiday} items. Cozy and rustic {season} feeling. 4k. high resolution, 3d. Instagram ready."

    try:
        # Upload the image to Cloudinary
        print(f"Trying to upload image to Cloudinary")
        response = cloudinary.uploader.upload(contents)
        image_url = response['secure_url']
        logging.info(f"Image uploaded: {image_url}")
        print(f"Image uploaded: {image_url}")        
        
        flow = run_flow(image_url, scene_prompt, video_prompt)
        if flow['status'] == "QUEUED":
            poll_result = poll_flow(flow['poll_url'])
            
            if isinstance(poll_result, str):
                import json
                try:
                    poll_result = json.loads(poll_result)
                except json.JSONDecodeError:
                    raise Exception("Failed to parse poll result as JSON")
            
            if isinstance(poll_result, list) and len(poll_result) > 0:
                video_url = poll_result[0]['value']['data']
                logging.info(f"Video generated: {video_url}")
                return {"message": "Video generated successfully", "video_url": video_url}
            else:
                return {"message": f"Error: Unexpected poll result format {poll_result}"}
        else:
            return {"message": "Error: Flow not queued"}
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        return {"message": f"Error generating video: {str(e)}"}

# Define a route to handle the uploaded text
@app.post("/upload-text/")
async def upload_text(text: str = Form(...)):
    # Process the uploaded text
    print(f"Uploaded text: {text}")
    return {"message": "Text uploaded successfully", "text": text}
