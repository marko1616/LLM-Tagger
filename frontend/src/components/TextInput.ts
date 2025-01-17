import {ref} from 'vue'
import {ClassicPreset} from 'rete'

class PromptTextInput extends ClassicPreset.Control {
  title = ref('')
  data = ref('')
  size: DOMRectReadOnly | null = null

  constructor(title: string, prompt?: string, private resizeCallback?: () => void) {
    super()
    this.data.value = prompt ?? ''
    this.title.value = title
  }

  onInput(event: Event) {
    const target = event.target as HTMLTextAreaElement
    this.data.value = target.value
  }

  saveSize(textareaSize: DOMRectReadOnly) {
    this.resizeCallback?.()
    this.size = textareaSize
  }

  set(text: string) {
    this.data.value = text
  }
}

export {PromptTextInput}
