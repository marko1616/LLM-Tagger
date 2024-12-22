import {ref} from 'vue'
import { ClassicPreset } from 'rete'

class PromptTextArea extends ClassicPreset.Control {
  value = ''
  collapsed = ref(false)
  constructor() {
    super()
  }

  onInput(event: InputEvent) {
    const target = event.target as HTMLElement
    target.querySelectorAll('*').forEach((el) => {
      (el as HTMLElement).removeAttribute('style');
    });
    this.value = target.innerHTML
  }

  onCollapse() {
    this.collapsed.value = !this.collapsed.value
  }
}

export { PromptTextArea }