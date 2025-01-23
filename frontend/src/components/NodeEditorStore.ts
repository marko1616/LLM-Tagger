import { ref, reactive, watch } from 'vue'

const editingControl = reactive({
  controlId: '',
  data: ''
})
const editingState = reactive({
  saved: false,
})
const openOuterEditor = ref<() => void>(() => {
  // eslint-disable-next-line @typescript-eslint/no-empty-function
})

watch(editingControl, () => {
  editingState.saved = false
})

export { editingControl, editingState, openOuterEditor }