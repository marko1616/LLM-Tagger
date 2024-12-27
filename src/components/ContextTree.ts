import {NodeEditor, GetSchemes, ClassicPreset, BaseSchemes} from 'rete'
import {AreaPlugin, AreaExtensions} from 'rete-area-plugin'
import {ConnectionPlugin, Presets as ConnectionPresets} from 'rete-connection-plugin'
import {VuePlugin, Presets, VueArea2D} from 'rete-vue-plugin'
import {ContextMenuExtra, ContextMenuPlugin, Presets as ContextMenuPresets } from "rete-context-menu-plugin";

import TextNode from './ContextNode.vue'
import Connection from './NodeConnection.vue'
import Socket from './NodeSocket.vue'

import {PromptTextArea} from './TextArea'
import TextAreaControl from './TextArea.vue'

import '@/styles/editorbg.scss'

type Schemes = GetSchemes<
  ClassicPreset.Node,
  ClassicPreset.Connection<ClassicPreset.Node, ClassicPreset.Node>
>
type AreaExtra = VueArea2D<Schemes> | ContextMenuExtra

function addCustomBackground<S extends BaseSchemes, K>(
    area: AreaPlugin<S, K>
) {
  const background = document.createElement('div')

  background.classList.add('background')
  background.classList.add('fill-area')

  area.area.content.add(background)
}

export class reteEditor {
  public readonly socket: ClassicPreset.Socket
  public readonly editor: NodeEditor<Schemes>
  public readonly area: AreaPlugin<Schemes, AreaExtra>
  public readonly connection: ConnectionPlugin<Schemes, AreaExtra>
  public readonly render: VuePlugin<Schemes, AreaExtra>
  public readonly contextMenu: ContextMenuPlugin<Schemes>
  public readonly rootNode: ClassicPreset.Node<any>

  constructor(container: HTMLElement) {
    this.socket = new ClassicPreset.Socket('socket')
    this.editor = new NodeEditor<Schemes>()
    this.area = new AreaPlugin<Schemes, AreaExtra>(container)
    this.connection = new ConnectionPlugin<Schemes, AreaExtra>()
    this.render = new VuePlugin<Schemes, AreaExtra>()
    this.contextMenu = new ContextMenuPlugin<Schemes>({
      items: ContextMenuPresets.classic.setup([
        ["User Node", () => this.userNodeFactory()],
        ["Assistant Node", () => this.assistantNodeFactory()]
      ])
    });

    this.area.use(this.contextMenu);
    AreaExtensions.selectableNodes(this.area, AreaExtensions.selector(), {
      accumulating: AreaExtensions.accumulateOnCtrl()
    })
  
    this.render.addPreset(Presets.contextMenu.setup());
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
              if (data.payload instanceof PromptTextArea) {
                return TextAreaControl
              }
            },
            socket(context) {
              return Socket
            },
            connection(context) {
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
  
    AreaExtensions.simpleNodesOrder(this.area)  
    AreaExtensions.zoomAt(this.area, this.editor.getNodes())

    this.rootNode = this.systemNodeFactory()
    this.editor.addNode(this.rootNode)
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

  createUserAssistantPairs() {
    const userNode = this.userNodeFactory()
    const assistantNode = this.assistantNodeFactory()
    this.editor.addNode(userNode)
    this.editor.addNode(assistantNode)
    this.editor.addConnection(new ClassicPreset.Connection(userNode, 'context-out', assistantNode, 'context-in'))
  }

  systemNodeFactory() {
    const systemNode = new ClassicPreset.Node(`Input-System`)
    systemNode.addControl('TextArea', new PromptTextArea())
    systemNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    systemNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return systemNode
  }

  userNodeFactory() {
    const userNode = new ClassicPreset.Node(`Input-User`)
    userNode.addControl('TextArea', new PromptTextArea())
    userNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    userNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return userNode
  }

  assistantNodeFactory() {
    const assistantNode = new ClassicPreset.Node(`Input-Assistant`)
    assistantNode.addControl('TextArea', new PromptTextArea())
    assistantNode.addOutput('context-out', new ClassicPreset.Output(this.socket))
    assistantNode.addInput('context-in', new ClassicPreset.Input(this.socket))
    return assistantNode
  }
}