<template>
  <div id="app">
    <TextEditor @close="closeEditor" :isEditorVisible="isEditorVisible" :editingText="editingTextRef" @updateText="updateText"/>
    <div class="node-editor-container">
      <NodeEditor class="node-editor" ref="nodeEditorRef"/>
    </div>
    <div class="sidebar">
      <div class="sidebar-main-panel">
        <DatasetPanel @loadItem="loadItem" @saveCurrentItem="saveCurrentItem" ref="datasetPanelRef"/>
        <PluginPanel @getSelectedDataset="getSelectedDataset" @flushDatasets="flushDatasets" ref="pluginPanelRef"/>
      </div>
      <footer>
        <p>&copy; 2024 <a href="https://github.com/marko1616/LLM-Tagger" target="_blank">LLM-Tagger</a>.</p>
        <p>Licensed under <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank">Apache 2.0 License</a>.</p>
      </footer>
    </div>
  </div>
</template>

<script lang="ts">
import {ref, toRef, defineComponent} from 'vue'
import axios from 'axios'

import { openOuterEditor, editingControl } from '@/components/NodeEditorStore'
import { DatasetItem } from '@/types/dataset'
import { editingState } from '@/components/NodeEditorStore'
import NodeEditor from '@/components/NodeEditor.vue'
import TextEditor from '@/components/TextEditor.vue'
import DatasetPanel from '@/components/DatasetPanel.vue'
import PluginPanel from '@/components/PluginPanel.vue'

export default defineComponent({
  components: {
    NodeEditor,
    TextEditor,
    DatasetPanel,
    PluginPanel
  },
  methods: {
    async loadItem(datasetName: string, itemName: string) {
      const item = (await axios.get(`/datasets/${datasetName}/${itemName}`)).data.item as DatasetItem
      this.nodeEditorRef?.loadItem(item)
    },
    toggleEditor() {
      this.isEditorVisible = !this.isEditorVisible
    },
    closeEditor() {
      this.isEditorVisible = false
    },
    getSelectedDataset(callback: (datasetName: string) => void) {
      const selectedDataset = (this.$refs.datasetPanelRef as typeof DatasetPanel).getSelectedDataset()
      if(selectedDataset) {
        callback(selectedDataset)
      }
    },
    async ctrlSaveHandler (event: KeyboardEvent) {
      if (event.ctrlKey && (event.key === 's' || event.key === 'S')) {
        event.preventDefault()
        const pathPart = this.$router.currentRoute.value.path.split('/')
        if(pathPart.length === 4) {
          // Save
          const datasetName = pathPart[2]
          const itemName = pathPart[3]
          await this.saveCurrentItem(datasetName, itemName)
        }
      }
    },
    async saveCurrentItem(datasetName: string, itemName: string) {
      const datasetItem: DatasetItem = this.nodeEditorRef?.exportDatasetItem()
      await axios.put(`/datasets/${datasetName}/${itemName}`, datasetItem)
      editingState.saved = true
    },
    async flushDatasets() {
      await (this.$refs.datasetPanelRef as typeof DatasetPanel).flushDatasets()
    }
  },
  mounted() {
    openOuterEditor.value = () => {
      this.toggleEditor()
    }
    window.addEventListener('keydown', this.ctrlSaveHandler)
    if(this.$route.params.datasetName) {
      const datasetName = this.$route.params.datasetName as string
      const itemName = this.$route.params.itemName as string
      this.loadItem(datasetName, itemName)
    }
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.ctrlSaveHandler)
  },
  setup() {
    const isEditorVisible = ref(false)
    const nodeEditorRef = ref<typeof NodeEditor | null>(null)
    const editingTextRef = toRef(editingControl, 'data')

    const updateText = (text: string) => {
      editingControl.data = text
    }

    return {
      nodeEditorRef,
      isEditorVisible,
      editingTextRef,
      updateText,
    }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

footer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 5%;
  color: $content-color;

  & > p {
    margin-top: 0.1em;
    margin-bottom: 0.1em;
  }
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
  min-width: 20em;
  max-width: 10vw;
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
  box-sizing: border-box;
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  width: 100%;
  max-height: 95%;
}
</style>

<style lang="css">
@import 'simplebar-vue/dist/simplebar.min.css';

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

[data-simplebar] {
  width: 100%;
}
</style>
