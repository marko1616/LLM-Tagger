import { ref, reactive } from 'vue'

const editingControl = reactive({
  controlId: '',
  data: ''
})
const openOuterEditor = ref<() => void>(() => {})

export { editingControl, openOuterEditor }