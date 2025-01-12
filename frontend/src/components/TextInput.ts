import {ref} from 'vue'
import {ClassicPreset} from 'rete'

class PromptTextInput extends ClassicPreset.Control {
  value = ref('')
  title = ref('')
  size: DOMRectReadOnly | null = null

  constructor(title: string) {
    super()
    this.title.value = title
  }

  update(data: string) {
    this.value.value = data
  }

  onInput(event: Event) {
    const target = event.target as HTMLTextAreaElement
    this.value.value = target.value
  }

  saveSize(size: DOMRectReadOnly) {
    this.size = size
  }
}

export {PromptTextInput}
