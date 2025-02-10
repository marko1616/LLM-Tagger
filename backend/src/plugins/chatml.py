import json
import uuid
import time
import asyncio

from fastapi import File, UploadFile, Body
from fastapi.responses import JSONResponse, Response

from pydantic import BaseModel, ValidationError
from typing import List

from ..database import Database
from ..schemas import (
    PluginInterface,
    PluginParam,
    DatasetItem,
    NodeItem,
    NodePosition,
    NodeSize,
    Role,
)


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


class ChatMLMessage(BaseModel):
    role: str
    content: str


class ChatMLInteraction(BaseModel):
    conversation: List[ChatMLMessage]


class ExportReq(BaseModel):
    dataset_name: str


class ExportCacheItem(BaseModel):
    content: bytes
    filename: str
    expiration_time: float


class Plugin:
    db: Database
    on_events = {}
    export_cache = {}
    file_expiration_time = 60

    def __init__(self, db: Database) -> None:
        self.db = db
        self.plugin_interfaces = [
            PluginInterface(
                display_name="Import ChatML",
                api_name="import_chatml",
                type="request",
                content_type="multipart/form-data",
                description="Import ChatML format dataset in a json or jsonl file.",
                handler=self.import_chatml,
                params=[
                    PluginParam(
                        display_name="Target dataset",
                        api_name="dataset_name",
                        description="Import to which dataset.",
                        type="dataset",
                    ),
                    PluginParam(
                        display_name="ChatML dataset",
                        api_name="file",
                        description="The file to import.",
                        type="file",
                    ),
                ],
            ),
            PluginInterface(
                display_name="Export ChatML",
                api_name="export_chatml",
                type="request",
                content_type="application/json",
                description="Export dataset to ChatML format json or jsonl file.",
                handler=self.export_chatml,
                params=[
                    PluginParam(
                        display_name="Target dataset",
                        api_name="dataset_name",
                        description="Export from which dataset.",
                        type="dataset",
                    )
                ],
            ),
            PluginInterface(
                display_name="Download ChatML",
                api_name="download_chatml/{download_id}",
                type="download",
                content_type="application/octet-stream",
                description="Download exported ChatML dataset.",
                handler=self.download_file,  # Reusing download_file as it's generic
                params=[],
            ),
        ]
        self.on_events["startup"] = [self.on_startup]

    async def on_startup(self):
        asyncio.create_task(self.cleanup_export_cache())

    async def cleanup_export_cache(self):
        while True:
            current_time = time.time()
            expired_ids = [
                download_id
                for download_id, item in self.export_cache.items()
                if current_time > item.expiration_time
            ]
            for download_id in expired_ids:
                del self.export_cache[download_id]
            await asyncio.sleep(self.file_expiration_time)

    async def import_chatml(
        self,
        dataset_name: str = Body(..., description="Dataset name"),
        file: UploadFile = File(..., description="File to upload"),
    ) -> JSONResponse:
        try:
            content = await file.read()
            data = parse_json_or_jsonl(content.decode())
        except ValueError:
            return JSONResponse(
                status_code=422,
                content={"message": "Invalid file format need json or jsonl"},
            )

        chatml_items = []
        try:
            if isinstance(data, list):
                for item in data:
                    chatml_items.append(ChatMLInteraction(conversation=item))
            else:
                return JSONResponse(
                    status_code=422,
                    content={"message": "Dataset must be a list of chatml items"},
                )
        except ValidationError as e:
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Invalid ChatML format",
                    "details": format_validation_error(e),
                },
            )

        default_prefix = "chatml"
        count = 0
        while True:
            prefix = f"{default_prefix}-{count}-"
            dataset = self.db.get_dataset_by_name(dataset_name)
            if not any(item.name.startswith(prefix) for item in dataset.items):
                break
            count += 1

        for i, item in enumerate(chatml_items):
            system_node = NodeItem(
                role=Role.SYSTEM,
                positive=item.conversation[0].content
                if item.conversation[0].role == Role.SYSTEM.value
                else "",
                negative="",
                nodePosition=NodePosition(x=0, y=0),
                nodeSize=NodeSize(height=64, width=256),
                to=[],
            )
            converted_item = DatasetItem(name=f"{prefix}{i}", nodeItems=[system_node])
            for current_idx, conversation_item in enumerate(item.conversation):
                if conversation_item.role == Role.SYSTEM.value:
                    if current_idx != 0:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "message": "System message must be the first message in the conversation"
                            },
                        )
                elif conversation_item.role == Role.USER.value:
                    converted_item.nodeItems.append(
                        NodeItem(
                            role=Role.USER,
                            positive=conversation_item.content,
                            negative="",
                            nodePosition=NodePosition(x=current_idx * 350, y=0),
                            nodeSize=NodeSize(height=64, width=256),
                            to=[],
                        )
                    )
                elif conversation_item.role == Role.ASSISTANT.value:
                    converted_item.nodeItems.append(
                        NodeItem(
                            role=Role.ASSISTANT,
                            positive=conversation_item.content,
                            negative="",
                            nodePosition=NodePosition(x=current_idx * 350, y=0),
                            nodeSize=NodeSize(height=64, width=256),
                            to=[],
                        )
                    )
                if current_idx < len(item.conversation) - 1:
                    converted_item.nodeItems[-1].to.append(current_idx + 1)
            dataset = self.db.get_dataset_by_name(dataset_name)
            dataset.items.append(converted_item)
            self.db.update_dataset_by_name(dataset_name, dataset)
        return JSONResponse(status_code=200, content={"message": "Imported"})

    def traverse_nodes(
        self,
        node_items: list[NodeItem],
        idx: int,
        context: ChatMLInteraction,
        chatml_dataset: list[ChatMLInteraction],
    ) -> None:
        if idx >= len(node_items):
            raise ValueError("Invalid index")
        current_node = node_items[idx]
        assert current_node.role != Role.SYSTEM
        if current_node.role == Role.USER:
            if not current_node.to:
                raise ValueError(f"USER node at index {idx} has empty 'to' links")
            for next_index in current_node.to:
                if next_index >= len(node_items):
                    raise ValueError(
                        f"Invalid node graph: next_index {next_index} "
                        f"exceeds node_items length {len(node_items)}"
                    )
                next_node = node_items[next_index]
                if next_node.role != Role.ASSISTANT:
                    raise ValueError(
                        f"Expected ASSISTANT node after USER at index {idx}, "
                        f"but got {next_node.role} at index {next_index}"
                    )
                new_context = context.model_copy(deep=True)
                new_context.conversation.append(
                    ChatMLMessage(role=Role.USER.value, content=current_node.positive)
                )
                self.traverse_nodes(node_items, next_index, new_context, chatml_dataset)
        elif current_node.role == Role.ASSISTANT:
            context.conversation.append(
                ChatMLMessage(role=Role.ASSISTANT.value, content=current_node.positive)
            )
            chatml_dataset.append(context)
            new_context = context.model_copy(deep=True)
            if current_node.to:
                for next_index in current_node.to:
                    self.traverse_nodes(
                        node_items, next_index, new_context, chatml_dataset
                    )

    async def export_chatml(
        self, export_req: ExportReq = Body(..., description="The dataset to export")
    ) -> JSONResponse:
        dataset_name = export_req.dataset_name
        dataset = self.db.get_dataset_by_name(dataset_name)
        if not dataset:
            return JSONResponse({"message": "Dataset not found"}, status_code=404)

        chatml_dataset = []
        for item in dataset.items:
            if not item.nodeItems:
                return JSONResponse({"message": "Empty nodeItems"}, status_code=400)
            if item.nodeItems[0].role != Role.SYSTEM:
                return JSONResponse(
                    {
                        "message": "Invalid dataset item",
                        "detail": "First item must be system",
                    },
                    status_code=400,
                )

            system_positive = item.nodeItems[0].positive
            context = ChatMLInteraction(
                conversation=[ChatMLMessage(role="system", content=system_positive)]
            )
            try:
                for start_index in item.nodeItems[0].to:
                    self.traverse_nodes(
                        item.nodeItems, start_index, context, chatml_dataset
                    )
            except ValueError as e:
                return JSONResponse(
                    {"message": "Invalid dataset item", "detail": str(e)},
                    status_code=400,
                )

        dumped_data = []
        for interaction in chatml_dataset:
            try:
                dumped = interaction.model_dump(exclude_none=True)
                dumped_data.append(dumped)
            except ValidationError as e:
                return JSONResponse(
                    {
                        "message": "Invalid dataset item",
                        "detail": format_validation_error(e),
                    },
                    status_code=400,
                )

        json_data = dumped_data
        json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
        content = json_content.encode("utf-8")

        download_id = str(uuid.uuid4())
        filename = f"chatml_export_{download_id}.json"

        self.export_cache[download_id] = ExportCacheItem(
            content=content,
            expiration_time=time.time() + self.file_expiration_time,
            filename=filename,
        )

        return JSONResponse(
            {
                "message": "Dataset exported",
                "url": f"/plugins/download_chatml/{download_id}",
                "filename": filename,
            },
            status_code=200,
        )

    async def download_file(self, download_id: str) -> Response:
        item = self.export_cache.get(download_id)
        if not item:
            return JSONResponse(status_code=404, content={"message": "File not found"})
        if time.time() > item.expiration_time:
            del self.export_cache[download_id]
            return JSONResponse(
                status_code=410, content={"message": "File has expired"}
            )
        self.export_cache[download_id].expiration_time = (
            time.time() + self.file_expiration_time
        )

        return Response(
            content=item.content,
            headers={
                "Content-Disposition": f'attachment; filename="{item.filename}"',
                "Content-Type": "application/json",
            },
        )
