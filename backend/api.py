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
    api_base: str
    auth_token: str

def load_config() -> None:
    """
    Loads the configuration from the config.json file.
    """
    if not os.path.exists("config.json"):
        raise RuntimeError("config.json not found")
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

def verify_auth_token(authorization: str = Header(None)) -> str:
    """
    Verifies the provided authorization token.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token is required")
    if authorization != config.auth_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return authorization

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/img/uploads", dependencies=[Depends(verify_auth_token)])
async def upload_image(file: UploadFile = File(...)) -> JSONResponse:
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
            "url": f"{config.api_base[:-1] if config.api_base.endswith('/') else config.api_base}/api/uploads/{file.filename}"
        },
        status_code=200
    )

@app.get("/api/uploads/{filename}")
async def get_uploaded_file(filename: str) -> FileResponse:
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