import { ref, reactive } from 'vue';

const editingNode = reactive({
  nodeId: '',
  data: '',
});
const openOuterEditor = ref<() => void>(() => {})

export { editingNode, openOuterEditor }