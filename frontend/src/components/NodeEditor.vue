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

/**
 * Apply !important to override CSS specificity issues that arise
 * when switching between `npm serve` (development) and `npm build` (production).
 * In some cases, styles might not be applied correctly due to differences in how
 * CSS is processed during development and production builds. Using !important ensures
 * that this particular style is consistently applied regardless of the build environment.
 */
[rete-context-menu] {
  box-sizing: border-box !important;
  min-width: max-content !important;
  background: $container-bg-color !important;
  border: 2px solid $container-border-color !important;
  border-radius: 0.5em !important;
  transition: border-color 0.3s ease !important;

  &:hover {
    border-color: $container-border-hover-color !important;
  }

  .block {
    display: flex !important;
    align-items: center !important;
    background: $container-bg-color !important;
    border: 0 !important;
    border-radius: 0.5vw !important;
    transition: background 0.2s ease !important;

    &.item {
      cursor: pointer !important;
      border: 0.1vw solid transparent !important;
    }

    &:hover {
      color: $content-color !important;
      background: $container-bg-hover-color !important;
      border-color: $container-border-hover-color !important;
    }

    &:focus-visible {
      outline: 0 !important;
    }
  }

  .block:first-child input {
    width: 100% !important;
    color: $content-color !important;
    outline: none !important;
    background: $container-input-bg-color !important;
    border: 2px solid $container-border-color !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;

    &:focus {
      background: $container-bg-hover-color !important;
      border-color: $container-border-hover-color !important;
    }
  }

  .search {
    font-size: 1.5rem !important;
    color: $content-color !important;
  }
}
</style>
