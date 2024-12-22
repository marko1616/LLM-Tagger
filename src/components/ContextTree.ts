import {ref} from 'vue'

import {NodeEditor, GetSchemes, ClassicPreset} from 'rete'
import {AreaPlugin, AreaExtensions} from 'rete-area-plugin'
import {ConnectionPlugin, Presets as ConnectionPresets} from 'rete-connection-plugin'
import {VuePlugin, Presets, VueArea2D} from 'rete-vue-plugin'

import TextNode from './ContextNode.vue'
import Connection from './NodeConnection.vue'
import Socket from './NodeSocket.vue'

import TextAreaControl from './TextArea.vue'

type Schemes = GetSchemes<
  ClassicPreset.Node,
  ClassicPreset.Connection<ClassicPreset.Node, ClassicPreset.Node>
>
type AreaExtra = VueArea2D<Schemes>

class CustomTextArea extends ClassicPreset.Control {
  value = ''
  collapsed = ref(false)
  constructor() {
    super()
  }

  onInput(event: InputEvent) {
    const target = event.target as HTMLElement
    this.value = target.innerHTML
  }

  onCollapse() {
    this.collapsed.value = !this.collapsed.value
  }
}

async function createUserAssistantPairs(editor: NodeEditor<Schemes>, socket: ClassicPreset.Socket, start: number) {
  const userNode = new ClassicPreset.Node(`Input-User#${start}`)
  userNode.addControl('TextArea', new CustomTextArea())
  userNode.addOutput('context-out', new ClassicPreset.Output(socket))
  userNode.addInput('context-in', new ClassicPreset.Input(socket))
  await editor.addNode(userNode)

  const assistantNode = new ClassicPreset.Node(`Input-Assistant#${start}`)
  assistantNode.addControl('TextArea', new CustomTextArea())
  assistantNode.addOutput('context-out', new ClassicPreset.Output(socket))
  assistantNode.addInput('context-in', new ClassicPreset.Input(socket))
  await editor.addNode(assistantNode)

  await editor.addConnection(new ClassicPreset.Connection(userNode, 'context-out', assistantNode, 'context-in'))
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
            if (data.payload instanceof CustomTextArea) {
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
