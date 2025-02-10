from dataclasses import dataclass
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Awaitable


class Image(BaseModel):
    id: int
    name: str
    file_type: str
    data: bytes


class Config(BaseModel):
    listen: str
    api_base: str
    auth_token: str
    max_file_size: int


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
    items: list[DatasetItem]


class PluginParam(BaseModel):
    display_name: str
    api_name: str
    type: str
    description: str


@dataclass
class PluginInterface:
    display_name: str
    api_name: str
    type: str
    content_type: str
    description: str
    params: list[PluginParam]
    handler: callable | Awaitable
