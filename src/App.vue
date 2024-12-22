<template>
  <div id="app">
    <div class="editor-container">
      <TextTree class="editor" />
    </div>
    <div class="sidebar">
      <div class="sidebar-content">
        <h2>工具</h2>
        <ul>
          <li>添加对话</li>
          <li>提交</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

import TextTree from '@/components/ContextTree.vue'

export default defineComponent({
  name: 'app',
  components: {
    TextTree
  }
})
</script>

<style lang="scss">
#app {
  display: flex;
  font-family: "Source Han Sans", "Noto Sans CJK SC", sans-serif;
  height: 100vh;
  width: 100vw;
}

.editor {
  display: flex;
}

.editor-container {
  flex: 3;
  display: flex;
}

.sidebar {
  flex: 1;
  background-color: #f0f0f0;
  border-left: 1px solid #ccc;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}
</style>
