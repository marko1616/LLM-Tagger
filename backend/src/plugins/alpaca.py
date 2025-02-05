import json
import uuid

from fastapi import File, UploadFile, Body
from fastapi.responses import JSONResponse, Response

from pydantic import BaseModel, ValidationError, model_validator
from typing import Optional, Any

from ..database import Database
from ..schemas import PluginInterface, PluginParam, DatasetItem, NodeItem, NodePosition, NodeSize, Role

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
    assistant_response: str

    @model_validator(mode="before")
    def parse_list_to_fields(cls, value: Any):
        if isinstance(value, list) and len(value) == 2:
            return {
                "human_instruction": value[0],
                "assistant_response": value[1]
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

class DatasetName(BaseModel):
    dataset_name: str

class Plugin:
    db: Database
    on_events = {}
    export_cache = {}

    def __init__(self, db: Database) -> None:
        self.db = db
        self.plugin_interfaces = [PluginInterface(
            display_name="Import alpaca",
            api_name="import_alpaca",
            type="request",
            content_type="multipart/form-data",
            description="Import alpaca form dataset in a json or jsonl file.",
            handler=self.import_alpaca,
            params=[PluginParam(
                display_name="Target dataset",
                api_name="dataset_name",
                description="Import to which dataset.",
                type="dataset",
            ), PluginParam(
                display_name="Alpaca dataset",
                api_name="file",
                description="The file to import.",
                type="file",
            )]
        ),PluginInterface(
                display_name="Export alpaca",
                api_name="export_alpaca",
                type="request",
                content_type="application/json",
                description="Export alpaca dataset to a json or jsonl file.",
                handler=self.export_alpaca,
                params=[
                    PluginParam(
                        display_name="Target dataset",
                        api_name="dataset_name",
                        description="Export from which dataset.",
                        type="dataset",
                    )
                ]
            ),
            PluginInterface(
                display_name="Download alpaca",
                api_name="download_alpaca/{download_id}",
                type="download",
                content_type="application/octet-stream",
                description="Download exported alpaca dataset.",
                handler=self.download_file,
                params=[]
            )]

    async def import_alpaca(self,
            dataset_name: str = Body(..., description="Dataset name"),
            file: UploadFile = File(..., description="File to upload")) -> JSONResponse:
        
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
                        positive=node_item.assistant_response,
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

    def recursive_parse_nodes(self, node_items: list[NodeItem], at: int, context: AlpacaInteraction, alpaca_dataset: list[AlpacaInteraction]) -> None:
        if at >= len(node_items):
            return
        current_node = node_items[at]
        if current_node.role == Role.USER:
            if not current_node.to:
                raise ValueError(f"USER node at index {at} has empty 'to' links")
            for next_index in current_node.to:
                if next_index >= len(node_items):
                    raise ValueError(
                        f"Invalid node graph: next_index {next_index} "
                        f"exceeds node_items length {len(node_items)}"
                    )
                next_node = node_items[next_index]
                if next_node.role != Role.ASSISTANT:
                    raise ValueError(
                        f"Expected ASSISTANT node after USER at index {at}, "
                        f"but got {next_node.role} at index {next_index}"
                    )
                new_context = context.model_copy(deep=True)
                if not next_node.to:
                    new_context.instruction = current_node.positive
                    new_context.input = ""
                else:
                    new_context.history.append(AlpacaDialogueRound(
                        human_instruction=current_node.positive,
                        assistant_response=next_node.positive
                    ))
                self.recursive_parse_nodes(
                    node_items, next_index, 
                    new_context, alpaca_dataset
                )
        elif current_node.role == Role.ASSISTANT:
            if not current_node.to:
                context.output = current_node.positive
                alpaca_dataset.append(context)
            else:
                for next_index in current_node.to:
                    self.recursive_parse_nodes(
                        node_items, next_index, context, alpaca_dataset
                    )
    async def export_alpaca(self, dataset_name: DatasetName = Body(..., description="The dataset to export")) -> JSONResponse:
        dataset_name = dataset_name.dataset_name
        try:
            dataset = self.db.get_dataset_by_name(dataset_name)
            if not dataset:
                raise ValueError(f"Dataset '{dataset_name}' not found")
            
            alpaca_dataset = []
            for item in dataset.items:
                if not item.nodeItems:
                    raise ValueError(f"Empty nodeItems in dataset item {item.name}")
                if item.nodeItems[0].role != Role.SYSTEM:
                    raise ValueError(
                        f"First node must be SYSTEM role in item {item.name}"
                    )
                
                system_positive = item.nodeItems[0].positive
                context = AlpacaInteraction(
                    instruction="",
                    input=None,
                    output="",
                    system=system_positive,
                    history=[]
                )
                try:
                    for start_index in item.nodeItems[0].to:
                        self.recursive_parse_nodes(item.nodeItems, start_index, context, alpaca_dataset)
                except ValueError as e:
                    raise ValueError(
                        f"Error processing item {item.name}: {str(e)}"
                    ) from e

            validated_data = []
            for interaction in alpaca_dataset:
                try:
                    validated = AlpacaInteraction.model_validate(interaction)
                    dumped = validated.model_dump(exclude_none=True)
                    dumped["history"] = [
                        [item["human_instruction"], item["assistant_response"]]
                        for item in dumped["history"]
                    ]
                    validated_data.append(dumped)
                except ValidationError as e:
                    raise ValueError(
                        f"Generated invalid Alpaca interaction: {format_validation_error(e)}"
                    ) from e
            
            json_data = validated_data
            json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
            content = json_content.encode('utf-8')

            download_id = str(uuid.uuid4())
            self.export_cache[download_id] = content
            return JSONResponse(
                status_code=200,
                content={"message": "Dataset exported", "url": f"/plugins/download_alpaca/{download_id}", "filename": f"alpaca_export_{download_id}.json"}
            )
        
        except ValueError as e:
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Export failed",
                    "details": str(e)
                }
            )

    async def download_file(self, download_id: str) -> Response:
        content = self.export_cache.pop(download_id, None)
        if content is None:
            return Response(status_code=404)
        
        return Response(
            content=content,
            headers={
                "Content-Disposition": f'attachment; filename="alpaca_export_{download_id}.json"',
                "Content-Type": "application/json",
            }
        )