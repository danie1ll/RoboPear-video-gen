import random
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional
from pydantic import BaseModel
import cloudinary
import cloudinary.uploader
from Layer1_Query import Wrapper
from createWebsite import TargetAudienceInsights, create_landing_page
from ml_flows import run_flow, poll_flow
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Cloudinary
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

app = FastAPI()

# Deploy
# BASE_URL = input("Enter the public base URL for this server (e.g. http://localhost:8000): ")
# Debugging
BASE_URL = "http://localhost:8000"

app.mount("/output", StaticFiles(directory="./generatedWebsites"), name="generatedWebsites")

# Define a route for the homepage to upload files
@app.get("/", response_class=HTMLResponse)
async def read_root():
    randomnumber  = random.randint(0, 100000)

    return f"""
    <h2>Upload Image</h2>
    <form action="/upload-image/id{randomnumber}" enctype="multipart/form-data" method="post">
        <input name="image" type="file" accept="image/*" required>
        <button type="submit">Upload Image</button>
    </form>

    <h2>Upload Text</h2>
    <form action="/upload-text/id{randomnumber}" method="post">
        <input name="text" type="text" placeholder="Enter your text" required>
        <button type="submit">Upload Text</button>
    </form>
    """
        # <input name="holiday" type="text" placeholder="Enter holiday" required>
        # <input name="season" type="text" placeholder="Enter season" required>

# Define a route to handle the uploaded image
@app.post("/upload-image/{sessionid}")
async def upload_image(sessionid: str, image: UploadFile = File(...)):
    # Process the uploaded image
    contents = await image.read()

    folder_path = os.path.join("generatedWebsites", sessionid)
    os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, "image.jpg")
    with open(file_path, "wb") as f:
        f.write(contents)
    
    logger.info(f"Stored image: {image.filename}")

    holiday = "Easter"
    season = "winter"
    video_prompt = "light changes slightly"
    scene_prompt = f"A product placed into a center of a composition on a wooden table. The product is surrounded by {holiday} items. Cozy and rustic {season} feeling. 4k. high resolution, 3d. Instagram ready."
    
    try:

        # Upload the image to Cloudinary
        logger.info(f"Trying to upload image to Cloudinary")
        response = cloudinary.uploader.upload(contents)
        image_url = response['secure_url']
        logger.info(f"Image uploaded: {image_url}")

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
                logger.info(f"Video generated: {video_url}")
                return {"message": "Video generated successfully", "video_url": video_url}
            else:
                return {"message": f"Error: Unexpected poll result format {poll_result}"}
        else:
            logger.error(f"Error: Flow not queued")
            return {"message": "Error: Flow not queued"}
    except Exception as e:
        return {"message": f"Error generating video: {str(e)}"}



# THIS IS A DUMMY
def LorenzosStuff(text, image_url):
    return TargetAudienceInsights(
        age_groups=["5-9"],
        gender_distribution=["100% Male", "0% Female"],
        locations=["New York", "Los Angeles", "Chicago"],
        interests=["Football", "Soccer", "Sports"],
        mainimage="image.jpg",
        images=["coke2.jpeg", "coke3.jpeg"],
        product="Funnzball",
        description="A football that can make funny sounds when you shoot it",
    )

# Define a route to handle the uploaded text
@app.post("/upload-text/{sessionid}")
async def upload_text(sessionid: str, text: str = Form(...)):
    # Process the uploaded text
    logger.info(f"Uploading text: {text}")

    #insights = Wrapper(text, BASE_URL + f"/output/{sessionid}/image.jpg")
    
    insights = Wrapper(text, f"./generatedWebsites/{sessionid}/image.jpg", BASE_URL + f"/output/{sessionid}/image.jpg")

    create_landing_page(sessionid, insights)

    # e.g. http://localhost:8000/output/coke/landing_page.html
    ret = {"message": "Text uploaded successfully", "text": text, "url": BASE_URL + f"/output/{sessionid}/landing_page.html"}

    logger.info(ret)
    return ret


