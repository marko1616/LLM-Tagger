<template>
    <div class="rete" ref="rete"></div>
</template>

<script lang="ts">
import { defineComponent, ComponentPublicInstance } from 'vue'
import { reteEditor } from './NodeEditor'

export default defineComponent({
  data() {
    return {
      editor: null as reteEditor | null
    }
  },
  mounted() {
    this.editor = new reteEditor(this.$refs.rete as HTMLElement)
  },
  beforeUnmount() {
    this.editor?.destroy()
  },
  methods: {
    createUserAssistantPairs(): void {
      this.editor?.createUserAssistantPairs()
    }
  }
})

export type NodeEditorInstance = ComponentPublicInstance<{
  createUserAssistantPairs: () => void;
}>
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.rete {
  display: flex;

  height: 100%;
  width: 100%;
}
</style>

<style lang="scss">
@import "@/styles/color.scss";

[rete-context-menu] {
  min-width: max-content;
  background: $container-bg-color;
  border: 2px solid $container-border-color;
  border-radius: 10px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;

  &:hover {
    border-color: $container-border-hover-color;
  }

  .block {
    background: $container-bg-color;
    border-radius: 0.5vw;
    border: 0px;
    display: flex;
    align-items: center;
    transition: background 0.2s ease;

    &.item {
      cursor: pointer;
      border: 0.1vw solid transparent;
    }

    &:hover {
      background: $container-bg-hover-color !important;
      border-color: $container-border-hover-color !important;
      color: $content-color !important;
    }

    &:focus-visible {
      outline: 0px;
    }
  }

  .block:first-child input {
    width: 100%;
    background: $container-input-bg-color;
    color: $content-color;
    border: 2px solid $container-border-color;
    border-radius: 10px;
    outline: none;
    transition: all 0.3s ease;

    &:focus {
      background: $container-bg-hover-color;
      border-color: $container-border-hover-color;
    }
  }

  .search {
    color: $content-color;
    font-size: 1.4vh;
  }
}
</style>
