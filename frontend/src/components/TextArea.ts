import {ref} from 'vue'
import {ClassicPreset} from 'rete'

class PromptTextArea extends ClassicPreset.Control {
  value = ref('')
  collapsed = ref(false)
  constructor() {
    super()
  }

  update(data: string) {
    this.value.value = data
  }

  getData() {
    return this.value
  }

  onInput(event: InputEvent) {
    const target = event.target as HTMLTextAreaElement
    this.value.value = target.value
  }

  onCollapse(target: HTMLTextAreaElement) {
    this.collapsed.value = !this.collapsed.value

    if(this.collapsed.value) {
      target.style.height = 'auto'
    } else {
      target.style.height = 'auto'
      target.style.height = target.scrollHeight + 'px'
    }
  }
}

export {PromptTextArea}
