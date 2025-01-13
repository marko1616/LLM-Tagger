import { ref, reactive } from 'vue'

const editingControl = reactive({
  controlId: '',
  data: ''
})
const openOuterEditor = ref<() => void>(() => {
  // eslint-disable-next-line @typescript-eslint/no-empty-function
})

export { editingControl, openOuterEditor }