import {NodeEditor, GetSchemes, ClassicPreset, BaseSchemes} from 'rete'
import {AreaPlugin, AreaExtensions, BaseAreaPlugin} from 'rete-area-plugin'
import {ConnectionPlugin, Presets as ConnectionPresets} from 'rete-connection-plugin'
import {VuePlugin, Presets, VueArea2D} from 'rete-vue-plugin'
import {ContextMenuExtra, ContextMenuPlugin, Presets as ContextMenuPresets} from 'rete-context-menu-plugin'

import TextNode from './ContextNode.vue'
import Connection from './NodeConnection.vue'
import Socket from './NodeSocket.vue'

import {PromptTextInput} from './TextInput'
import TextInputControl from './TextInput.vue'

import { DatasetItem, Role } from '@/types/dataset'
import { editingControl } from './NodeEditorStore'

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

export class reteEditor {
  public readonly socket: ClassicPreset.Socket
  public readonly editor: NodeEditor<Schemes>
  public readonly area: AreaPlugin<Schemes, AreaExtra>
  public readonly connection: ConnectionPlugin<Schemes, AreaExtra>
  public readonly render: VuePlugin<Schemes, AreaExtra>
  public readonly contextMenu: ContextMenuPlugin<Schemes>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public readonly rootNode: ClassicPreset.Node<any>
  public readonly handleKeyDown: (event: KeyboardEvent) => void

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
      if (event.type === 'noderemove' && event.data.id === this.rootNode.id) {
        return undefined
      }
      return event
    })

    this.handleKeyDown = (event: KeyboardEvent) => {if(event.key == 'Delete') this.area.emit({type: 'keydelete', data: null})}
    window.addEventListener('keydown', this.handleKeyDown)
    this.area.addPipe(event => {
      // Remove all selected nodes on key delete.
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

  async createUserAssistantPairs(position: Position | null = null) {
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

  systemNodeFactory(prompt?: string) {
    const systemNode = new ClassicPreset.Node('Input-System')
    systemNode.addControl('TextInput', new PromptTextInput('System', prompt, this.gettextareaResizeCallback(systemNode.id)))
    systemNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    return systemNode
  }

  userNodeFactory(prompt?: string) {
    const userNode = new ClassicPreset.Node('Input-User')
    userNode.addControl('TextInput', new PromptTextInput('User', prompt, this.gettextareaResizeCallback(userNode.id)))
    userNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    userNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return userNode
  }

  assistantNodeFactory(prompt?: string) {
    const assistantNode = new ClassicPreset.Node('Input-Assistant')
    assistantNode.addControl('TextInputPositive', new PromptTextInput('Assistant positive', prompt, this.gettextareaResizeCallback(assistantNode.id)))
    assistantNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    assistantNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return assistantNode
  }

  assistantPairwiseNodeFactory(promptPositive?: string, promptNegative?: string) {
    const assistantPairwiseNode = new ClassicPreset.Node('Input-Assistant-Pairwise')
    assistantPairwiseNode.addControl('TextInputPositive', new PromptTextInput('Assistant positive', promptPositive, this.gettextareaResizeCallback(assistantPairwiseNode.id)))
    assistantPairwiseNode.addControl('TextInputNegative', new PromptTextInput('Assistant negative', promptNegative, this.gettextareaResizeCallback(assistantPairwiseNode.id)))
    assistantPairwiseNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    assistantPairwiseNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return assistantPairwiseNode
  }

  async openItem(item: DatasetItem) {
    // Remove all
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const nodes:ClassicPreset.Node<any>[] = []
    for (const node of this.getNodes()) {
      const nodeId = node.id
      if(nodeId !== this.rootNode.id) {
        await this.editor.removeNode(node.id)
        const connections = this.editor.getConnections().filter(c => {
          return c.source === nodeId || c.target === nodeId
        })
        for(const connection of connections) {
          await this.editor.removeConnection(connection.id)
        }
      }
    }
    for (const nodeItem of item.nodeItems) {
      switch(nodeItem.role) {
        case Role.SYSTEM: {
          editingControl.controlId = this.rootNode.controls['TextInput']?.id as string
          editingControl.data = nodeItem.positive
          nodes.push(this.rootNode)
          await this.area.translate(this.rootNode.id, nodeItem.nodePosition)
          await Promise.resolve()
          break
        }
        case Role.USER: {
          const node = this.userNodeFactory(nodeItem.positive)
          nodes.push(node)
          await this.editor.addNode(node)
          await this.area.translate(node.id, nodeItem.nodePosition)
          await Promise.resolve()
          break
        }
        case Role.ASSISTANT: {
          if(nodeItem.negative) {
            const node = this.assistantPairwiseNodeFactory(nodeItem.positive, nodeItem.negative)
            nodes.push(node)
            await this.editor.addNode(node)
            await this.area.translate(node.id, nodeItem.nodePosition)
          } else {
            const node = this.assistantNodeFactory(nodeItem.positive)
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