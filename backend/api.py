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


@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str) -> FileResponse:
    """
    Serves the uploaded file.
    """


@app.get("/datasets/list", dependencies=[Depends(verify_auth_token)])
async def list_datasets() -> JSONResponse:
    """
    Lists all available datasets.
    """


@app.post("/datasets/create", dependencies=[Depends(verify_auth_token)])
async def create_dataset(dataset: Dataset) -> JSONResponse:
    """
    Creates a new dataset.
    """


@app.get("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def get_dataset(name: str) -> JSONResponse:
    """
    Retrieves a dataset.
    """

@app.put("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def update_dataset(name: str, dataset: Dataset) -> JSONResponse:
    """
    Updates an existing dataset.
    """

@app.delete("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def delete_dataset(name: str) -> JSONResponse:
    """
    Deletes an existing dataset.
    """


@app.get("/datasets/{name}/list", dependencies=[Depends(verify_auth_token)])
async def list_dataset_items(name: str) -> JSONResponse:
    """
    Lists all available dataset items.
    """

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

@app.get(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def get_dataset_item(dataset_name: str, item_name: str) -> JSONResponse:
    """
    Retrieves a dataset item.
    """

@app.put(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def update_dataset_item(
    dataset_name: str, item_name: str, item: DatasetItem
) -> JSONResponse:
    """
    Updates a dataset item.
    """


@app.delete(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def delete_dataset_item(dataset_name: str, item_name: str) -> JSONResponse:
    """
    Deletes a dataset item.
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host=config.listen.split(":")[0],
        port=int(config.listen.split(":")[1]),
        reload=True,
    )
