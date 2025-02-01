import {ref} from 'vue'
import {ClassicPreset} from 'rete'
import {NodeSize} from '@/types/dataset'

class PromptTextInput extends ClassicPreset.Control {
  title = ref('')
  data = ref('')
  size: NodeSize

  constructor(title: string, prompt?: string, size? : NodeSize, private resizeCallback?: () => void) {
    super()
    this.data.value = prompt ?? ''
    this.title.value = title
    if(size) {
      this.size = size
    } else {
      this.size = {
        width: 256,
        height: 64
      }
    }
  }

  onInput(event: Event) {
    const target = event.target as HTMLTextAreaElement
    this.data.value = target.value
  }

  saveSize(textareaSize: DOMRectReadOnly) {
    this.resizeCallback?.()
    this.size = {
      width: textareaSize.width,
      height: textareaSize.height
    }
  }

  set(text: string) {
    this.data.value = text
  }
}

export {PromptTextInput}
