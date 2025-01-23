import os
import shutil
import time
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


class NodeSize(BaseModel):
    width: float
    height: float


class NodeItem(BaseModel):
    role: Role
    nodePosition: NodePosition
    nodeSize: NodeSize
    positive: str
    negative: Optional[str]
    to: list[int]


class DatasetItem(BaseModel):
    name: str
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
    allow_headers=["Content-Type", "Authorization"],
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


@app.post("/img/uploads", dependencies=[Depends(verify_auth_token)])
async def upload_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Handles uploading of image files.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400, detail="Only JPEG and PNG images are allowed."
        )

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
            "url": f"{config.api_base[:-1] if config.api_base.endswith('/') else config.api_base}/uploads/{file.filename}",
        },
        status_code=200,
    )


@app.get("/uploads/{filename}")
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


@app.get("/datasets/list", dependencies=[Depends(verify_auth_token)])
async def list_datasets() -> JSONResponse:
    """
    Lists all available datasets.
    """
    datasets = [f.stem for f in DATASET_DIR.glob("*.json")]
    return JSONResponse(content={"datasets": datasets}, status_code=200)


@app.post("/datasets/create", dependencies=[Depends(verify_auth_token)])
async def create_dataset(dataset: Dataset) -> JSONResponse:
    """
    Creates a new dataset.
    """
    dataset_dir = Path("./datasets") / f"{dataset.name}.json"

    if dataset.name == "":
        return JSONResponse(
            content={"message": "Dataset name cannot be empty."}, status_code=400
        )

    if os.path.exists(dataset_dir):
        return JSONResponse(
            content={"message": "Dataset already exists."}, status_code=400
        )

    with open(dataset_dir, "w") as f:
        f.write(dataset.model_dump_json(indent=config.json_indent))

    return JSONResponse(
        content={"message": "Dataset successfully updated."}, status_code=200
    )


@app.get("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def get_dataset(name: str) -> JSONResponse:
    """
    Retrieves a dataset.
    """
    dataset_dir = Path("./datasets") / f"{name}.json"

    if not dataset_dir.exists():
        return JSONResponse(
            content={"message": "Dataset does not exist."}, status_code=404
        )

    with open(dataset_dir, "r") as f:
        return JSONResponse(content=json.load(f), status_code=200)


@app.delete("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def delete_dataset(name: str) -> JSONResponse:
    """
    Deletes an existing dataset.
    """
    dataset_dir = Path("./datasets") / f"{name}.json"

    if not dataset_dir.exists():
        return JSONResponse(
            content={"message": "Dataset does not exist."}, status_code=404
        )

    dataset_dir.unlink()
    return JSONResponse(
        content={"message": "Dataset successfully deleted."}, status_code=200
    )


@app.get("/datasets/{name}/list", dependencies=[Depends(verify_auth_token)])
async def list_dataset_items(name: str) -> JSONResponse:
    """
    Lists all available dataset items.
    """
    dataset_dir = Path("./datasets") / f"{name}.json"

    if not dataset_dir.exists():
        return JSONResponse(
            content={"message": "Dataset does not exist."}, status_code=404
        )

    with open(dataset_dir, "r") as f:
        data = json.load(f)

    return JSONResponse({"items":[item["name"] for item in data["items"]]})


@app.get(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def get_dataset_item(dataset_name: str, item_name: str) -> JSONResponse:
    """
    Retrieves a dataset item.
    """
    dataset_dir = Path("./datasets") / f"{dataset_name}.json"

    if not dataset_dir.exists():
        return JSONResponse(
            content={"message": "Dataset does not exist."}, status_code=404
        )

    with open(dataset_dir, "r") as f:
        data = json.load(f)

    for item in data["items"]:
        if item["name"] == item_name:
            return JSONResponse(content=item, status_code=200)

    return JSONResponse(content={"message": "Item does not exist."}, status_code=404)


@app.post(
    "/datasets/{dataset_name}/create",
    dependencies=[Depends(verify_auth_token)],
)
async def update_dataset_item(
    dataset_name: str, item: DatasetItem
) -> JSONResponse:
    """
    Creates a dataset item.
    """
    dataset_dir = Path("./datasets") / f"{dataset_name}.json"

    if item.name == "":
        return JSONResponse(
            content={"message": "Item name cannot be empty."}, status_code=400
        )

    if not dataset_dir.exists():
        return JSONResponse(
            content={"message": "Dataset does not exist."}, status_code=404
        )

    with open(dataset_dir, "r") as f:
        data = json.load(f)

    if item.name in data["items"]:
        return JSONResponse(
            content={"message": "Item already exists."}, status_code=400
        )

    else:
        data["items"].append(item.model_dump())
    data["timestamp"] = int(time.time())

    with open(dataset_dir, "w") as f:
        f.write(json.dumps(data, indent=config.json_indent))

    return JSONResponse(
        content={"message": "Item successfully updated."}, status_code=200
    )


@app.delete(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def delete_dataset_item(dataset_name: str, item_name: str) -> JSONResponse:
    """
    Deletes a dataset item.
    """
    dataset_dir = Path("./datasets") / f"{dataset_name}.json"

    if not dataset_dir.exists():
        return JSONResponse(
            content={"message": "Dataset does not exist."}, status_code=404
        )

    with open(dataset_dir, "r") as f:
        data = json.load(f)

    for i, item in enumerate(data["items"]):
        if item["name"] == item_name:
            del data["items"][i]
            break
    else:
        return JSONResponse(
            content={"message": "Item does not exist."}, status_code=404
        )
    data["timestamp"] = int(time.time())

    with open(dataset_dir, "w") as f:
        f.write(json.dumps(data, indent=config.json_indent))

    return JSONResponse(
        content={"message": "Item successfully deleted."}, status_code=200
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host=config.listen.split(":")[0],
        port=int(config.listen.split(":")[1]),
        reload=True,
    )
