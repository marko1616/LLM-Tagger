<template>
    <div class="rete" ref="rete"></div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { ReteEditor } from './NodeEditor'
import { DatasetItem } from '@/types/dataset'

export default defineComponent({
  data() {
    return {
      editor: null as ReteEditor | null
    }
  },
  mounted() {
    this.editor = new ReteEditor(this.$refs.rete as HTMLElement)
  },
  beforeUnmount() {
    this.editor?.destroy()
  },
  methods: {
    exportDatasetItem() {
      return this.editor?.exportDatasetItem()
    },
    openItem(item: DatasetItem) {
      this.editor?.openItem(item)
    },
    createUserAssistantPairs(): void {
      this.editor?.createUserAssistantPairs()
    }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

.rete {
  display: flex;
  width: 100%;
  height: 100%;
}
</style>

<style lang="scss">
@use "@/styles/color.scss" as *;

[rete-context-menu] {
  box-sizing: border-box;
  min-width: max-content;
  background: $container-bg-color;
  border: 2px solid $container-border-color;
  border-radius: 10px;
  transition: border-color 0.3s ease;

  &:hover {
    border-color: $container-border-hover-color;
  }

  .block {
    display: flex;
    align-items: center;
    background: $container-bg-color;
    border: 0;
    border-radius: 0.5vw;
    transition: background 0.2s ease;

    &.item {
      cursor: pointer;
      border: 0.1vw solid transparent;
    }

    &:hover {
      color: $content-color !important;
      background: $container-bg-hover-color !important;
      border-color: $container-border-hover-color !important;
    }

    &:focus-visible {
      outline: 0;
    }
  }

  .block:first-child input {
    width: 100%;
    color: $content-color;
    outline: none;
    background: $container-input-bg-color;
    border: 2px solid $container-border-color;
    border-radius: 10px;
    transition: all 0.3s ease;

    &:focus {
      background: $container-bg-hover-color;
      border-color: $container-border-hover-color;
    }
  }

  .search {
    font-size: 1.4vh;
    color: $content-color;
  }
}
</style>
