from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import os
from typing import Optional
from pydantic import BaseModel
from createWebsite import TargetAudienceInsights, create_landing_page
from ml_flows import run_flow, poll_flow
import logging


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
@app.post("/upload-image/{sessionid}")
async def upload_image(sessionid: str, image: UploadFile = File(...)):
    # Process the uploaded image
    contents = await image.read()

    folder_path = os.path.join("generatedWebsites", sessionid)
    os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, image.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    print(f"Uploaded image: {image.filename}")
    return {"message": "Image uploaded successfully", "filename": file_path}

# Define a route to handle the uploaded text
@app.post("/upload-text/{sessionid}")
async def upload_text(sessionid: str, text: str = Form(...)):
    # Process the uploaded text
    print(f"Uploaded text: {text}")

    # call Lorenzos Stuff
    insights = TargetAudienceInsights(
        age_groups=["5-9"],
        gender_distribution=["100% Male", "0% Female"],
        locations=["New York", "Los Angeles", "Chicago"],
        interests=["Football", "Soccer", "Sports"],
        mainimage="coke.jpeg",
        images=["coke2.jpeg", "coke3.jpeg"],
        product="Funnzball",
        description="A football that can make funny sounds when you shoot it",
    )

    create_landing_page(sessionid, insights)


    return {"message": "Text uploaded successfully", "text": text}

# # Define a model for the request body
# class VideoGenerationRequest(BaseModel):
#     image_url: str

@app.post("/generate-video/")
async def generate_video(image_url: str = Form(...)):
    holiday = "Easter"
    season = "winter"
    video_prompt = "light changes slightly"
    scene_prompt = f"A product placed into a center of a composition on a wooden table. The product is surrounded by {holiday} items. Cozy and rustic {season} feeling. 4k. high resolution, 3d. Instagram ready."
    
    try:
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
        return {"message": f"Error generating video: {str(e)}"}

