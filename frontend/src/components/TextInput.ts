import {ref} from 'vue'
import {ClassicPreset} from 'rete'

class PromptTextInput extends ClassicPreset.Control {
  value = ref('')
  title = ref('')
  emitRenderCallback?: () => void

  constructor(title: string, emitRenderCallback?: () => void) {
    super()
    this.title.value = title
    this.emitRenderCallback = emitRenderCallback
  }

  update(data: string) {
    this.value.value = data
  }

  onInput(event: Event) {
    const target = event.target as HTMLTextAreaElement
    this.value.value = target.value
  }

  emitRender() {
    this.emitRenderCallback?.()
  }
}

export {PromptTextInput}
