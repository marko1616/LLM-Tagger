import os
import json

from fastapi import FastAPI, HTTPException, File, UploadFile, Header, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from .database import Database
from .schemas import Config, Dataset, DatasetItem

def load_config() -> Config:
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
db = Database()

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

@app.post("/images/upload", dependencies=[Depends(verify_auth_token)])
async def upload_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Handles uploading of image files.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise JSONResponse({"message":"File type not allowed"}, status_code=400)
    if file.size > config.max_file_size:
        raise JSONResponse({"message":"File size too large"}, status_code=400)
    return JSONResponse({
            "url": f"{config.api_base}images/{db.create_image(file.filename, file.content_type, await file.read())}"
        })

@app.get("/images/{id}")
async def get_uploaded_file(id: int) -> Response:
    """
    Serves the uploaded file.
    """
    image = db.get_image_by_id(id)
    return Response(image.data, media_type=image.file_type)

@app.get("/datasets/list", dependencies=[Depends(verify_auth_token)])
async def list_datasets() -> JSONResponse:
    """
    Lists all available datasets.
    """
    return JSONResponse({
            "message": "Datasets listed",
            "datasets": db.list_datasets()
        })

@app.post("/datasets/create", dependencies=[Depends(verify_auth_token)])
async def create_dataset(dataset: Dataset) -> JSONResponse:
    """
    Creates a new dataset.
    """
    if dataset.name == "":
        return JSONResponse({"message": "Dataset name cannot be empty"}, status_code=400)
    db.create_dataset(dataset.name, dataset.timestamp, dataset.items)
    return JSONResponse({"message": "Dataset created"})

@app.get("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def get_dataset(name: str) -> JSONResponse:
    """
    Retrieves a dataset.
    """
    db.get_dataset_by_name(name).as_dataset()
    return JSONResponse({"message": "Dataset retrieved"})

@app.put("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def update_dataset(name: str, dataset: Dataset) -> JSONResponse:
    """
    Updates an existing dataset.
    """
    db.update_dataset_by_name(name, dataset)
    return JSONResponse({"message": "Dataset updated"})

@app.delete("/datasets/{name}", dependencies=[Depends(verify_auth_token)])
async def delete_dataset(name: str) -> JSONResponse:
    """
    Deletes an existing dataset.
    """
    db.delete_dataset_by_name(name)
    return JSONResponse({"message": "Dataset deleted"})


@app.get("/datasets/{name}/list", dependencies=[Depends(verify_auth_token)])
async def list_dataset_items(name: str) -> JSONResponse:
    """
    Lists all available dataset items.
    """
    return JSONResponse({
            "message": "Dataset items listed",
            "items":[item.name for item in db.get_dataset_by_name(name).items]
        })

@app.post(
    "/datasets/{dataset_name}/create",
    dependencies=[Depends(verify_auth_token)],
)
async def create_dataset_item(
    dataset_name: str, item: DatasetItem
) -> JSONResponse:
    """
    Creates a dataset item.
    """
    dataset = db.get_dataset_by_name(dataset_name)
    dataset.items.append(item)
    db.update_dataset_by_name(dataset_name, dataset)
    return JSONResponse({"message": "Dataset item created"})

@app.get(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def get_dataset_item(dataset_name: str, item_name: str) -> JSONResponse:
    """
    Retrieves a dataset item.
    """
    dataset = db.get_dataset_by_name(dataset_name)
    for item in dataset.items:
        if item.name == item_name:
            return JSONResponse({"message": "Dataset item retrieved", "item": item.model_dump()})
    return JSONResponse({"message": "Dataset item not found"}, status_code=404)

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
    dataset = db.get_dataset_by_name(dataset_name)
    item.name = item_name
    for i, orig_item in enumerate(dataset.items):
        if orig_item.name == item_name:
            dataset.items[i] = item
            db.update_dataset_by_name(dataset_name, dataset)
            return JSONResponse({"message": "Dataset item updated"})
    return JSONResponse({"message": "Dataset item not found"}, status_code=404)

@app.delete(
    "/datasets/{dataset_name}/{item_name}",
    dependencies=[Depends(verify_auth_token)],
)
async def delete_dataset_item(dataset_name: str, item_name: str) -> JSONResponse:
    """
    Deletes a dataset item.
    """
    dataset = db.get_dataset_by_name(dataset_name)
    for i, item in enumerate(dataset.items):
        if item.name == item_name:
            del dataset.items[i]
            db.update_dataset_by_name(dataset_name, dataset)
            return JSONResponse({"message": "Dataset item deleted"})
    return JSONResponse({"message": "Dataset item not found"}, status_code=404)