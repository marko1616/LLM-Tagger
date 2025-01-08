import os
import shutil
import json
from enum import Enum
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, File, UploadFile, Header, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class Config(BaseModel):
    listen: str
    api_base: str
    auth_token: str
    json_indent: int

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class NodePosition(BaseModel):
    x: float
    y: float

class NodeItem(BaseModel):
    role: Role
    nodePosition: NodePosition
    positive: str
    negative: Optional[str]

class DatasetItem(BaseModel):
    name: Optional[str]
    nodeItems: list[NodeItem]

class Dataset(BaseModel):
    name: str
    timestamp: int
    override: bool
    items: list[DatasetItem]

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

DATASET_DIR = Path("./datasets")
DATASET_DIR.mkdir(exist_ok=True)

@app.post("/api/img/uploads", dependencies=[Depends(verify_auth_token)])
async def upload_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Handles uploading of image files.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed.")

    file_path = UPLOAD_DIR / file.filename
    if file_path.exists():
        raise HTTPException(status_code=400, detail="File already exists.")
    if file_path.suffix not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file extension.")

    try:
        with file_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}.")

    return JSONResponse(
        content={
            "message": "File uploaded successfully.",
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
        return JSONResponse(content={"message": "File not found"}, status_code=404)

    if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        return JSONResponse(content={"message": "Invalid file path"}, status_code=400)

    return FileResponse(file_path)

@app.get("/api/datasets/list", dependencies=[Depends(verify_auth_token)])
async def list_datasets() -> JSONResponse:
    """
    Lists all available datasets.
    """
    datasets = [f.stem for f in DATASET_DIR.glob("*.json")]
    return JSONResponse(content={"datasets": datasets}, status_code=200)

@app.post("/api/datasets/create", dependencies=[Depends(verify_auth_token)])
async def create_dataset(dataset: Dataset) -> JSONResponse:
    """
    Creates a new dataset.
    """
    dataset_dir = Path("./datasets") / f"{dataset.name}.json"

    if dataset_dir.exists():
        return JSONResponse(content={"message":"Dataset already exists."}, status_code=400)
    
    # Validate timestamp
    if not 0 <= dataset.timestamp <= (2**64 - 1):
        return JSONResponse(content={"message":"Invalid timestamp."}, status_code=400)

    with open(dataset_dir, "w") as f:
        f.write(dataset.model_dump_json(indent=config.json_indent))

    return JSONResponse(content={"message":"Dataset successfully created."}, status_code=200)

@app.get("/api/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def get_dataset(name: str) -> JSONResponse:
    """
    Retrieves a dataset.
    """
    dataset_dir = Path("./datasets") / f"{name}.json"

    if not dataset_dir.exists():
        return JSONResponse(content={"message":"Dataset does not exist."}, status_code=404)

    with open(dataset_dir, "r") as f:
        return JSONResponse(content=json.load(f), status_code=200)

@app.put("/api/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def update_dataset(name: str, dataset: Dataset) -> JSONResponse:
    """
    Updates an existing dataset.
    """
    dataset_dir = Path("./datasets") / f"{name}.json"

    if not dataset_dir.exists():
        return JSONResponse(content={"message":"Dataset does not exist."}, status_code=404)
    
    # Validate timestamp
    if not 0 <= dataset.timestamp <= (2**64 - 1):
        return JSONResponse(content={"message":"Invalid timestamp."}, status_code=400)

    with open(dataset_dir, "r") as f:
        data = json.load(f)
    if data.get("timestamp") >= dataset.timestamp and not dataset.override:
        return JSONResponse(content={"message":"The provided timestamp is not earlier than the dataset's current timestamp and override is not enabled."}, status_code=400)

@app.delete("/api/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def delete_dataset(name: str) -> JSONResponse:
    """
    Deletes an existing dataset.
    """
    dataset_dir = Path("./datasets") / f"{name}.json"

    if not dataset_dir.exists():
        return JSONResponse(content={"message":"Dataset does not exist."}, status_code=404)

    dataset_dir.unlink()
    return JSONResponse(content={"message":"Dataset successfully deleted."}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host=config.listen.split(":")[0], port=int(config.listen.split(":")[1]), reload=True)