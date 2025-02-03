import json

from fastapi import File, UploadFile, Body
from fastapi.responses import JSONResponse

from pydantic import BaseModel, ValidationError, model_validator
from typing import Optional, Any

from ..database import Database
from ..schemas import DatasetItem, NodeItem, NodePosition, NodeSize, Role

def format_validation_error(e: ValidationError) -> list[str]:
    error_messages = []
    for error in e.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        message = f"Field '{field_path}': {error['msg']}"
        error_messages.append(message)
    return error_messages

def parse_json_or_jsonl(content):
    content = content.strip()
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError:
        pass
    try:
        lines = content.splitlines()
        data = [json.loads(line) for line in lines if line.strip()]
        return data
    except json.JSONDecodeError:
        raise ValueError("Content is neither valid JSON nor valid JSONL format")

class AlpacaDialogueRound(BaseModel):
    human_instruction: str
    model_response: str

    @model_validator(mode="before")
    def parse_list_to_fields(cls, value: Any):
        if isinstance(value, list) and len(value) == 2:
            return {
                "human_instruction": value[0],
                "model_response": value[1]
            }
        return value

class AlpacaInteraction(BaseModel):
    instruction: str
    input: Optional[str] = None
    output: str
    system: Optional[str] = None
    history: Optional[list[AlpacaDialogueRound]] = None

class AlpacaDataset(BaseModel):
    data: list[AlpacaInteraction]

class Plugin:
    db: Database
    api_name = "import_alpaca"
    display_name = "Import alpaca"
    discription = "Import alpaca form dataset in a json or jsonl file."
    params = [
        {
            "display_name": "Target dataset",
            "api_name": "dataset_name",
            "type": "dataset",
            "description": "Export to which dataset.",
        },
        {
            "display_name": "Alpaca dataset",
            "api_name": "file",
            "type": "file",
            "description": "The file to import.",
        }
    ]

    def __init__(self, db: Database):
        self.db = db

    def api(self,
            dataset_name: str = Body(..., description="Dataset name"),
            file: UploadFile = File(..., description="File to upload")):
        
        try:
            data = parse_json_or_jsonl(file.file.read().decode())
        except ValueError:
            return JSONResponse(status_code=422, content={"message": "Invalid file format need json or jsonl"})

        try:
            data = AlpacaDataset(**{"data": data})
        except ValidationError as e:
            return JSONResponse(status_code=422, content={"message": "Invalid file format need json or jsonl", "details": format_validation_error(e)})
        
        defalut_prefix = "alpaca"
        prefix = f"{defalut_prefix}-{1}-"
        found_prefix = False
        count = 1
        while not found_prefix:
            for item in self.db.get_dataset_by_name(dataset_name).items:
                if item.name.startswith(prefix):
                    prefix = f"{defalut_prefix}-{count}-"
                    break
            else:
                found_prefix = True
            count += 1
        
        for i, item in enumerate(data.data):
            system_node = NodeItem(
                role=Role.SYSTEM,
                positive=item.system if item.system else "",
                negative="",
                nodePosition=NodePosition(x=0,y=0),
                nodeSize=NodeSize(height=64,width=256),
                to=[1],
            )
            converted_item = DatasetItem(name=f"{prefix}{i}", nodeItems=[system_node])
            count = 1
            if item.history is None:
                item.history = []
            for node_item in item.history:
                converted_item.nodeItems.append(
                    NodeItem(
                        role=Role.USER,
                        positive=node_item.human_instruction,
                        negative="",
                        nodePosition=NodePosition(x=(count*2-1)*350,y=0),
                        nodeSize=NodeSize(height=64,width=256),
                        to=[count*2],
                    )
                )
                converted_item.nodeItems.append(
                    NodeItem(
                        role=Role.ASSISTANT,
                        positive=node_item.model_response,
                        negative="",
                        nodePosition=NodePosition(x=count*2*350,y=0),
                        nodeSize=NodeSize(height=64,width=256),
                        to=[count*2+1],
                    )
                )
                count += 1
            converted_item.nodeItems.append(
                NodeItem(
                    role=Role.USER,
                    positive=item.instruction+(f"\n{item.input}" if item.input else ""),
                    negative="",
                    nodePosition=NodePosition(x=(count*2-1)*350,y=0),
                    nodeSize=NodeSize(height=64,width=256),
                    to=[count*2],
                )
            )
            converted_item.nodeItems.append(
                NodeItem(
                    role=Role.ASSISTANT,
                    positive=item.output,
                    negative="",
                    nodePosition=NodePosition(x=count*2*350,y=0),
                    nodeSize=NodeSize(height=64,width=256),
                    to=[],
                )
            )
            dataset = self.db.get_dataset_by_name(dataset_name)
            dataset.items.append(converted_item)
            self.db.update_dataset_by_name(dataset_name, dataset)
        return JSONResponse(status_code=200, content={"message": "Imported"})