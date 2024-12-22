import {NodeEditor, GetSchemes, ClassicPreset, BaseSchemes} from 'rete'
import {AreaPlugin, AreaExtensions} from 'rete-area-plugin'
import {ConnectionPlugin, Presets as ConnectionPresets} from 'rete-connection-plugin'
import {VuePlugin, Presets, VueArea2D} from 'rete-vue-plugin'

import TextNode from './ContextNode.vue'
import Connection from './NodeConnection.vue'
import Socket from './NodeSocket.vue'

import { PromptTextArea } from './TextArea'
import TextAreaControl from './TextArea.vue'

import "@/styles/editorbg.scss"

type Schemes = GetSchemes<
  ClassicPreset.Node,
  ClassicPreset.Connection<ClassicPreset.Node, ClassicPreset.Node>
>
type AreaExtra = VueArea2D<Schemes>

async function createUserAssistantPairs(editor: NodeEditor<Schemes>, socket: ClassicPreset.Socket, start: number) {
  const userNode = new ClassicPreset.Node(`Input-User#${start}`)
  userNode.addControl('TextArea', new PromptTextArea())
  userNode.addOutput('context-out', new ClassicPreset.Output(socket))
  userNode.addInput('context-in', new ClassicPreset.Input(socket))
  await editor.addNode(userNode)

  const assistantNode = new ClassicPreset.Node(`Input-Assistant#${start}`)
  assistantNode.addControl('TextArea', new PromptTextArea())
  assistantNode.addOutput('context-out', new ClassicPreset.Output(socket))
  assistantNode.addInput('context-in', new ClassicPreset.Input(socket))
  await editor.addNode(assistantNode)

  await editor.addConnection(new ClassicPreset.Connection(userNode, 'context-out', assistantNode, 'context-in'))
}

function addCustomBackground<S extends BaseSchemes, K>(
  area: AreaPlugin<S, K>
) {
  const background = document.createElement("div");

  background.classList.add("background");
  background.classList.add("fill-area");

  area.area.content.add(background);
}


export async function createEditor(container: HTMLElement) {
  const socket = new ClassicPreset.Socket('socket')

  const editor = new NodeEditor<Schemes>()
  const area = new AreaPlugin<Schemes, AreaExtra>(container)
  const connection = new ConnectionPlugin<Schemes, AreaExtra>()
  const render = new VuePlugin<Schemes, AreaExtra>()

  AreaExtensions.selectableNodes(area, AreaExtensions.selector(), {
    accumulating: AreaExtensions.accumulateOnCtrl(),
  })

  render.addPreset(
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
          },
        },
      }),
  )
  connection.addPreset(ConnectionPresets.classic.setup())

  addCustomBackground(area)

  editor.use(area)
  area.use(connection)
  area.use(render)

  AreaExtensions.simpleNodesOrder(area)

  createUserAssistantPairs(editor, socket, 1)
  createUserAssistantPairs(editor, socket, 2)
  createUserAssistantPairs(editor, socket, 3)

  AreaExtensions.zoomAt(area, editor.getNodes())

  return () => area.destroy()
}
