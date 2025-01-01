import {ref} from 'vue'
import {ClassicPreset} from 'rete'

class PromptTextInput extends ClassicPreset.Control {
  value = ref('')
  title = ref('')
  collapsed = ref(false)
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

export {PromptTextInput}
