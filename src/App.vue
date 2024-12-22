<template>
  <div id="app">
    <div class="editor-container">
      <TextTree class="editor" />
    </div>
    <div class="sidebar">
      <div class="sidebar-main-funct">
      </div>
      <div class="sidebar-buttom-funct">
        <button>提交</button>
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

html, body {
  display: flex;

  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
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

.editor {
  display: flex;
}

.editor-container {
  flex: 3;

  display: flex;
  margin-right: -1vw;
}

.sidebar {
  flex: 1;
  z-index: 1;
  background-color: $container-bg-color;
  border-left: 1px solid $container-border-color;
  border-radius: 1vw;
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
