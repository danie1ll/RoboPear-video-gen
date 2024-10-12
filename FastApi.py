from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import os

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
    """

# Define a route to handle the uploaded image
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
