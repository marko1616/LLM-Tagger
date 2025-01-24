<template>
  <div id="app">
    <TextEditor @close="closeEditor" :isEditorVisible="isEditorVisible" :editingText="editingTextRef" @updateText="updateText"/>
    <div class="node-editor-container">
      <NodeEditor class="node-editor" ref="nodeEditorRef"/>
    </div>
    <div class="sidebar">
      <div class="sidebar-main-panel">
        <DatasetPanel @openItem="openItem"/>
      </div>
      <footer>
        <p>
          &copy; 2024 <a href="https://github.com/marko1616/LLM-Tagger" target="_blank">LLM-Tagger</a>.
          Licensed under <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank">Apache 2.0 License</a>.
        </p>
      </footer>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, toRef, defineComponent} from 'vue'

import NodeEditor from '@/components/NodeEditor.vue'
import { openOuterEditor, editingControl } from '@/components/NodeEditorStore'
import { DatasetItem } from '@/types/dataset'
import TextEditor from '@/components/TextEditor.vue'
import DatasetPanel from '@/components/DatasetPanel.vue'

export default defineComponent({
  components: {
    NodeEditor,
    TextEditor,
    DatasetPanel
  },
  methods: {
    openItem(item: DatasetItem) {
      this.nodeEditorRef?.openItem(item)
    },
    toggleEditor() {
      this.isEditorVisible = !this.isEditorVisible
    },
    closeEditor() {
      this.isEditorVisible = false
    }
  },
  mounted() {
    openOuterEditor.value = () => {
      this.toggleEditor()
    }
    window.addEventListener('keydown', this.ctrlSaveHandler)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.ctrlSaveHandler)
  },
  setup() {
    const isEditorVisible = ref(false)
    const nodeEditorRef = ref<typeof NodeEditor | null>(null)
    const editingTextRef = toRef(editingControl, 'data')

    const createUserAssistantPairs = () => {
      nodeEditorRef.value?.createUserAssistantPairs()
    }

    const updateText = (text: string) => {
      editingControl.data = text
    }

    const ctrlSaveHandler = (event: KeyboardEvent) => {
      if (event.ctrlKey && (event.key === 's' || event.key === 'S')) {
        nodeEditorRef.value?.exportDatasetItem()
        event.preventDefault();
      }
    }

    return {
      createUserAssistantPairs,
      nodeEditorRef,
      isEditorVisible,
      editingTextRef,
      updateText,
      ctrlSaveHandler
    }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

footer {
  display: flex;
  justify-content: center;
  margin-top: 1vh;
  color: $content-color;
}

a {
  color: $content-color;
  text-decoration: none;
}

a:visited {
  color: $content-select-color;
}

a:active {
  color: $content-select-color;
}

.node-editor {
  display: flex;
}

.node-editor-container {
  display: flex;
  flex: 3;
  margin-right: -1vw;
}

.sidebar {
  z-index: 1;
  display: flex;
  flex: 1;
  flex-direction: column;
  max-height: 100%;
  padding: 16px;
  padding-right: 1vw;
  padding-left: 1vw;
  background-color: $container-bg-color;
  border-left: 1px solid $container-border-color;
  border-top-left-radius: 1vw;
  border-bottom-left-radius: 1vw;
}

.sidebar-main-panel {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.sidebar-buttom-panel {
  display: flex;
  justify-content: center;
}
</style>

<style lang="scss">
html, body {
  display: flex;
  width: 100vw;
  height: 100vh;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

#app {
  display: flex;
  width: 100vw;
  height: 100vh;
  font-family: Consolas, "Courier New", "Microsoft YaHei", "Noto Sans CJK", monospace;
}
</style>
