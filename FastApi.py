from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from typing import Optional

app = FastAPI()


# Define a route to handle the uploaded image and optional text input
@app.post("/upload-image/")
async def upload_image(image: UploadFile = File(...)):
    # Process the uploaded image
    contents = await image.read()
    
    # Here you can save the image or process it as needed
    with open(image.filename, "wb") as f:
        f.write(contents)
    
    print(f"Uploaded image: {image.filename}")
    return {"message": "Image uploaded successfully", "filename": image.filename}

# Define a route to handle the uploaded text
@app.post("/upload-text/")
async def upload_text(text: str = Form(...)):
    # Process the uploaded text
    print(f"Uploaded text: {text}")
    return {"message": "Text uploaded successfully", "text": text}
