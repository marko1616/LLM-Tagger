import {UnwrapRef} from 'vue'
import {NodeEditor, GetSchemes, ClassicPreset, BaseSchemes} from 'rete'
import {AreaPlugin, AreaExtensions, BaseAreaPlugin} from 'rete-area-plugin'
import {ConnectionPlugin, Presets as ConnectionPresets} from 'rete-connection-plugin'
import {VuePlugin, Presets, VueArea2D} from 'rete-vue-plugin'
import {ContextMenuExtra, ContextMenuPlugin, Presets as ContextMenuPresets} from 'rete-context-menu-plugin'

import TextNode from './ContextNode.vue'
import Connection from './NodeConnection.vue'
import Socket from './NodeSocket.vue'

import {PromptTextInput} from './TextInput'
import {editingState} from './NodeEditorStore'
import TextInputControl from './TextInput.vue'

import { DatasetItem, NodeSize, Role } from '@/types/dataset'
import '@/styles/editorbg.scss'

type ContextMenuItem = {
  label: string
  key: string
  handler(): void | Promise<void>
  subitems?: ContextMenuItem[]
}

type Position = {
  x: number
  y: number
}

type Schemes = GetSchemes<
  ClassicPreset.Node,
  ClassicPreset.Connection<ClassicPreset.Node, ClassicPreset.Node>
>

type KeyDeleteSignal = {type: 'keydelete', data: null}

type AreaExtra = VueArea2D<Schemes> | ContextMenuExtra | KeyDeleteSignal

function addCustomBackground<S extends BaseSchemes, K>(
    area: AreaPlugin<S, K>
) {
  const background = document.createElement('div')

  background.classList.add('background')
  background.classList.add('editor-grid-bg')

  area.area.content.add(background)
}

/**
 * A Rete-based editor for creating and managing nodes and connections.
 * This class provides functionality for adding nodes, creating connections,
 * handling context menus, and exporting/importing dataset items.
 */
export class ReteEditor {
  public readonly socket: ClassicPreset.Socket
  public readonly editor: NodeEditor<Schemes>
  public readonly area: AreaPlugin<Schemes, AreaExtra>
  public readonly connection: ConnectionPlugin<Schemes, AreaExtra>
  public readonly render: VuePlugin<Schemes, AreaExtra>
  public readonly contextMenu: ContextMenuPlugin<Schemes>
  public readonly handleKeyDown: (event: KeyboardEvent) => void

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private rootNode: ClassicPreset.Node<any>
  private replaceRootNode = false;

  /**
   * Initializes a new instance of the ReteEditor class.
   * @param container - The HTML element that will contain the editor.
   */
  constructor(container: HTMLElement) {
    this.socket = new ClassicPreset.Socket('socket')
    this.editor = new NodeEditor<Schemes>()
    this.area = new AreaPlugin<Schemes, AreaExtra>(container)
    this.connection = new ConnectionPlugin<Schemes, AreaExtra>()
    this.render = new VuePlugin<Schemes, AreaExtra>()
    this.contextMenu = new ContextMenuPlugin<Schemes>({
      items: (context, plugin) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const area = plugin.parentScope<BaseAreaPlugin<Schemes, any>>(BaseAreaPlugin)
        const classicPreset = ContextMenuPresets.classic.setup([
          ['User Node', () => this.userNodeFactory()],
          ['Assistant Node', () => this.assistantNodeFactory()],
          ['Assistant Pairwise Node', () => this.assistantPairwiseNodeFactory()]
        ])
        const createUserAssistantPairs: ContextMenuItem = {
          label: 'Create User-Assistant Pairs',
          key: 'createUserAssistantPairs',
          handler: (async () => await this.createUserAssistantPairs(area.area.pointer))
        }
        const defaultMenu = classicPreset(context, plugin)

        if(context == 'root') {
          defaultMenu.list.push(createUserAssistantPairs)
        }

        if(context instanceof ClassicPreset.Node) {
          if(context.label !== 'Input-System') {
            const cloneNode: ContextMenuItem = {
              label: 'Clone Node',
              key: 'cloneNode',
              handler: (async () => this.cloneNode(context.id, area.area.pointer))
            }
            defaultMenu.list.push(cloneNode)
          }
        }

        return defaultMenu
      }
    })

    this.area.use(this.contextMenu)
    AreaExtensions.selectableNodes(this.area, AreaExtensions.selector(), {
      accumulating: AreaExtensions.accumulateOnCtrl()
    })
  
    this.render.addPreset(Presets.contextMenu.setup())
    this.render.addPreset(
      Presets.classic.setup({
        customize: {
          node(context) {
            if (context.payload.label.startsWith('Input')) {
              return TextNode
            }
            return Presets.classic.Node
          },
          control(data) {
            if (data.payload instanceof PromptTextInput) {
              return TextInputControl
            }
          },
          socket(_context) {
            return Socket
          },
          connection(_context) {
            return Connection
          }
        }
      })
    )
    this.connection.addPreset(ConnectionPresets.classic.setup())
  
    addCustomBackground(this.area)
  
    this.editor.use(this.area)
    this.area.use(this.connection)
    this.area.use(this.render)

    this.area.addPipe(event => {
      return event
    })
  
    AreaExtensions.simpleNodesOrder(this.area)  
    AreaExtensions.zoomAt(this.area, this.editor.getNodes())

    // Create system node that can't be deleted.
    this.rootNode = this.systemNodeFactory()
    this.editor.addNode(this.rootNode)
    this.editor.addPipe(event => {
      if (event.type === 'noderemove' && event.data.id === this.rootNode.id && !this.replaceRootNode) {
        return undefined
      }
      return event
    })

    this.handleKeyDown = (event: KeyboardEvent) => {if(event.key == 'Delete') this.area.emit({type: 'keydelete', data: null})}
    window.addEventListener('keydown', this.handleKeyDown)
    this.area.addPipe(event => {
      // Remove all selected nodes on key delete.
      if (event.type in ['noderemoved', 'nodecreated', 'noderesized', 'nodetranslated']) {
        editingState.saved = false
      }
      if (event.type === 'keydelete') {
        this.editor.getNodes().forEach(node => {
          if(node.selected) {
            const nodeId = node.id
            const connections = this.editor.getConnections().filter(c => {
              return c.source === nodeId || c.target === nodeId
            })
  
            for (const connection of connections) {
              this.editor.removeConnection(connection.id)
            }
            this.editor.removeNode(nodeId)
          }
        })
        return undefined
      }
      return event
    })
  }

  gettextareaResizeCallback(id: string) {
    // Little hack here because size will be reclac in retejs/render-utils
    return () => this.area.emit({
      type: 'noderesized',
      data: {
        id: id,
        size: {
          width: 0,
          height: 0,
        }
      }
    })
  }

  destroy() {
    this.area.destroy()
  }

  getNodes() {
    return this.editor.getNodes()
  }

  getNode(id: string) {
    return this.editor.getNode(id)
  }

  getConnections() {
    return this.editor.getConnections()
  }

  getConnection(id: string) {
    return this.editor.getConnection(id)
  }

  getNodePosition(id: string) {
    return this.area.nodeViews.get(id)?.position
  }

  async cloneNode(id: string, to?: Position) {
    const origNode = this.getNode(id)
    if(!origNode) {
      return
    }
    if(origNode.hasControl('TextInput')) {
      // Clone non pairwise node
      const label = origNode.label
      const prompt = (origNode.controls['TextInput'] as PromptTextInput).data.value
      const size = (origNode.controls['TextInput'] as PromptTextInput).size
      switch(label) {
        case 'Input-System': {
          // Can't clone root node
          return
        }
        case 'Input-User': {
          const node = this.userNodeFactory(prompt, size)
          await this.editor.addNode(node)
          await this.area.translate(node.id, to ?? {x: 0, y: 0})
          break
        }
        case 'Input-Assistant': {
          const node = this.assistantNodeFactory(prompt, size)
          await this.editor.addNode(node)
          await this.area.translate(node.id, to ?? {x: 0, y: 0})
          break
        }
      }
    } else {
      // Clone pairwise node
      const promptPositive = (origNode.controls['TextInputPositive'] as PromptTextInput).data.value
      const promptNegative = (origNode.controls['TextInputNegative'] as PromptTextInput).data.value
      const size = (origNode.controls['TextInputPositive'] as PromptTextInput).size
      const node = this.assistantPairwiseNodeFactory(promptPositive, promptNegative, size)
      await this.editor.addNode(node)
      await this.area.translate(node.id, to ?? {x: 0, y: 0})
    }
  }

  async createUserAssistantPairs(position?: Position) {
    const userNode = this.userNodeFactory()
    const assistantNode = this.assistantNodeFactory()
    await this.editor.addNode(userNode)
    await this.editor.addNode(assistantNode)
    await this.editor.addConnection(new ClassicPreset.Connection(userNode, 'context-out', assistantNode, 'context-in'))

    if(position) {
      await this.area.translate(userNode.id, position)
      await this.area.translate(assistantNode.id, {x: position.x + 500, y: position.y})
    }
  }

  systemNodeFactory(prompt?: string, size?: NodeSize) {
    const systemNode = new ClassicPreset.Node('Input-System')
    systemNode.addControl('TextInput', new PromptTextInput('System', prompt, size, this.gettextareaResizeCallback(systemNode.id)))
    systemNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    return systemNode
  }

  userNodeFactory(prompt?: string, size?: NodeSize) {
    const userNode = new ClassicPreset.Node('Input-User')
    userNode.addControl('TextInput', new PromptTextInput('User', prompt, size, this.gettextareaResizeCallback(userNode.id)))
    userNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    userNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return userNode
  }

  assistantNodeFactory(prompt?: string, size?: NodeSize) {
    const assistantNode = new ClassicPreset.Node('Input-Assistant')
    assistantNode.addControl('TextInput', new PromptTextInput('Assistant positive', prompt, size, this.gettextareaResizeCallback(assistantNode.id)))
    assistantNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    assistantNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return assistantNode
  }

  assistantPairwiseNodeFactory(promptPositive?: string, promptNegative?: string, size?: NodeSize) {
    const assistantPairwiseNode = new ClassicPreset.Node('Input-Assistant-Pairwise')
    assistantPairwiseNode.addControl('TextInputPositive', new PromptTextInput('Assistant positive', promptPositive, size, this.gettextareaResizeCallback(assistantPairwiseNode.id)))
    assistantPairwiseNode.addControl('TextInputNegative', new PromptTextInput('Assistant negative', promptNegative, size, this.gettextareaResizeCallback(assistantPairwiseNode.id)))
    assistantPairwiseNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    assistantPairwiseNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return assistantPairwiseNode
  }

  getConnectionsFrom(nodeId: string) {
    const connections = this.getConnections()
    return connections.filter(connection => connection.source === nodeId)
  }

  exportDatasetItem() {
    const datasetItem: DatasetItem = {name:'', nodeItems:[]}
    const nodes = this.getNodes()
    nodes.forEach(node => {
      const label = node.label
      switch(label) {
        case 'Input-System': {
          const positivePrompt = (node.controls['TextInput'] as UnwrapRef<PromptTextInput>).data
          const {width, height} = (node.controls['TextInput'] as PromptTextInput).size 
          const {x, y} = this.getNodePosition(node.id) as Position
          const to: number[] = []
          this.getConnectionsFrom(node.id).forEach(connection => {
            const targetNodeId = connection.target
            to.push(nodes.findIndex(node => node.id === targetNodeId))
          })
          datasetItem.nodeItems.push({
            role: Role.SYSTEM,
            nodePosition: {x, y},
            nodeSize: {width, height},
            positive: positivePrompt,
            negative: null,
            to: to
          })
          break
        }
        case 'Input-User': {
          const positivePrompt = (node.controls['TextInput'] as UnwrapRef<PromptTextInput>).data
          const {width, height} = (node.controls['TextInput'] as PromptTextInput).size 
          const {x, y} = this.getNodePosition(node.id) as Position
          const to: number[] = []
          this.getConnectionsFrom(node.id).forEach(connection => {
            const targetNodeId = connection.target
            to.push(nodes.findIndex(node => node.id === targetNodeId))
          })
          datasetItem.nodeItems.push({
            role: Role.USER,
            nodePosition: {x, y},
            nodeSize: {width, height},
            positive: positivePrompt,
            negative: null,
            to: to
          })
          break
        }
        case 'Input-Assistant': {
          const positivePrompt = (node.controls['TextInput'] as UnwrapRef<PromptTextInput>).data as string
          const {width, height} = (node.controls['TextInput'] as PromptTextInput).size
          const {x, y} = this.getNodePosition(node.id) as Position
          const to: number[] = []
          this.getConnectionsFrom(node.id).forEach(connection => {
            const targetNodeId = connection.target
            to.push(nodes.findIndex(node => node.id === targetNodeId))
          })
          datasetItem.nodeItems.push({
            role: Role.ASSISTANT,
            nodePosition: {x, y},
            nodeSize: {width, height},
            positive: positivePrompt,
            negative: null,
            to: to
          })
          break
        }
        case 'Input-Assistant-Pairwise': {
          const positivePrompt = (node.controls['TextInputPositive'] as UnwrapRef<PromptTextInput>).data
          const negativePrompt = (node.controls['TextInputNegative'] as UnwrapRef<PromptTextInput>).data
          const {width, height} = (node.controls['TextInputPositive'] as PromptTextInput).size
          const {x, y} = this.getNodePosition(node.id) as Position
          const to: number[] = []
          this.getConnectionsFrom(node.id).forEach(connection => {
            const targetNodeId = connection.target
            to.push(nodes.findIndex(node => node.id === targetNodeId))
          })
          datasetItem.nodeItems.push({
            role: Role.ASSISTANT,
            nodePosition: {x, y},
            nodeSize: {width, height},
            positive: positivePrompt,
            negative: negativePrompt,
            to: to
          })
          break
        }
      }
    })
    return datasetItem
  }

  async loadItem(item: DatasetItem) {
    // Remove all
    this.replaceRootNode = true
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const nodes:ClassicPreset.Node<any>[] = []
    for (const node of this.getNodes()) {
      const nodeId = node.id
      await this.editor.removeNode(node.id)
      const connections = this.editor.getConnections().filter(c => {
        return c.source === nodeId || c.target === nodeId
      })
      for(const connection of connections) {
        await this.editor.removeConnection(connection.id)
      }
    }
    this.replaceRootNode = false
    for (const nodeItem of item.nodeItems) {
      switch(nodeItem.role) {
        case Role.SYSTEM: {
          const node = this.systemNodeFactory(nodeItem.positive, nodeItem.nodeSize)
          nodes.push(node)
          await this.editor.addNode(node)
          await this.area.translate(node.id, nodeItem.nodePosition)
          this.rootNode = node
          await Promise.resolve()
          break
        }
        case Role.USER: {
          const node = this.userNodeFactory(nodeItem.positive, nodeItem.nodeSize)
          nodes.push(node)
          await this.editor.addNode(node)
          await this.area.translate(node.id, nodeItem.nodePosition)
          await Promise.resolve()
          break
        }
        case Role.ASSISTANT: {
          if(nodeItem.negative) {
            const node = this.assistantPairwiseNodeFactory(nodeItem.positive, nodeItem.negative, nodeItem.nodeSize)
            nodes.push(node)
            await this.editor.addNode(node)
            await this.area.translate(node.id, nodeItem.nodePosition)
          } else {
            const node = this.assistantNodeFactory(nodeItem.positive, nodeItem.nodeSize)
            nodes.push(node)
            await this.editor.addNode(node)
            await this.area.translate(node.id, nodeItem.nodePosition)
          }
          await Promise.resolve()
          break
        }
        case Role.TOOL: {
          // TODO
          await Promise.resolve()
          break
        }
      }
    }
    // Connect
    for (let i = 0; i < item.nodeItems.length; i++) {
      const thisNode = item.nodeItems[i]
      const targetNodes = thisNode.to
      for (const targetNodeIndex of targetNodes) {
        await this.editor.addConnection(new ClassicPreset.Connection(nodes[i], 'context-out', nodes[targetNodeIndex], 'context-in'))
      }
    }
  }
}