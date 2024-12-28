<template>
  <div id="app">
    <TextEditor @close="closeEditor" :isEditorVisible="isEditorVisible" :editingText="editingTextRef" @updateText="updateText"/>
    <div class="context-tree-container">
      <ContextTree class="context-tree" ref="contextTreeRef"/>
    </div>
    <div class="sidebar">
      <div class="sidebar-main-funct">
      </div>
      <div class="sidebar-buttom-funct">
        <button>提交</button>
        <button @click="toggleEditor">编辑</button>
        <button @click="createUserAssistantPairs">添加节点</button>
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
import {ref, toRef} from 'vue'
import {defineComponent} from 'vue'
import ContextTree, { ContextTreeInstance } from '@/components/ContextTree.vue'
import TextEditor from '@/components/TextEditor.vue'
import { openOuterEditor, editingNode } from '@/components/ContextTreeStore'

export default defineComponent({
  components: {
    ContextTree,
    TextEditor
  },
  methods: {
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
  },
  setup(props, { expose }) {
    const isEditorVisible = ref(false)
    const contextTreeRef = ref<ContextTreeInstance | null>(null)
    const editingTextRef = toRef(editingNode, 'data')

    const createUserAssistantPairs = () => {
      contextTreeRef.value?.createUserAssistantPairs()
    }

    const updateText = (text: string) => {
      editingNode.data = text
    }

    return {
      createUserAssistantPairs,
      contextTreeRef,
      isEditorVisible,
      editingTextRef,
      updateText
    }
  }
})
</script>

<style lang="scss">
html, body {
  display: flex;

  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>

<style lang="scss" scoped>
@import "@/styles/color.scss";

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

body {
  background-color: $main-bg-color;
}

#app {
  display: flex;
  font-family: Consolas, "Courier New", "Microsoft YaHei", "Noto Sans CJK", monospace;
  height: 100vh;
  width: 100vw;
}

.context-tree {
  display: flex;
}

.context-tree-container {
  flex: 3;

  display: flex;
  margin-right: -1vw;
}

.sidebar {
  flex: 1;
  z-index: 1;
  background-color: $container-bg-color;
  border-left: 1px solid $container-border-color;
  border-top-left-radius: 1vw;
  border-bottom-left-radius: 1vw;
  display: flex;
  flex-direction: column;
  padding: 16px;
  padding-left: 1vw;
  padding-right: 1vw;
}

.sidebar-main-funct {
  display: flex;
  flex: 1;
}

.sidebar-buttom-funct {
  display: flex;
  justify-content: center;
}
</style>
