enum ContextMenuTargetType {
  DATASET = 'dataset',
  ITEM = 'item',
}

enum Role {
  SYSTEM = 'system',
  USER = 'user',
  ASSISTANT = 'assistant',
  TOOL = 'tool',
}

type NodePosition = {
  x: number
  y: number
}

type NodeItem = {
  role: Role
  nodePosition: NodePosition
  positive: string
  negative?: string
  to: number[]
}

type DatasetItem = {
  name: string
  nodeItems: NodeItem[]
}

type DatasetItemSummary = {
  name: string
}

type Dataset = {
  name: string
  timestamp: number
  override: boolean
  items: DatasetItem[]
}

type DatasetSummary = {
  name: string
  items: DatasetItemSummary[]
}

export { ContextMenuTargetType, Role, NodePosition, NodeItem, DatasetItem, DatasetItemSummary, Dataset, DatasetSummary }