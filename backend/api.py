import os
import shutil
from pathlib import Path

from fastapi import FastAPI, HTTPException, File, UploadFile, Header, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

class Config(BaseModel):
    listen: str
    apiBase: str
    authToken: str

def load_config():
    try:
        with open("config.json", "r") as f:
            return Config(**json.load(f))
    except Exception as e:
        raise RuntimeError(f"Error loading config: {e}")

config = load_config()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

def verify_auth_token(authorization: str = Header(None)):
    if authorization != config.authToken:
        raise HTTPException(status_code=401, detail="Invalid token")
    return authorization

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/img/uploads", dependencies=[Depends(verify_auth_token)])
async def upload_image(file: UploadFile = File(...)):
    """
    Handles uploading of image files.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed")

    file_path = UPLOAD_DIR / file.filename
    try:
        with file_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return JSONResponse(
        content={
            "message": "File uploaded successfully",
            "url": f"{config.apiBase[:-1] if config.apiBase.endswith('/') else config.apiBase}/api/uploads/{file.filename}"
        },
        status_code=200
    )

@app.get("/api/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """
    Serves the uploaded file.
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")

    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host=config.listen.split(":")[0], port=int(config.listen.split(":")[1]), reload=True)