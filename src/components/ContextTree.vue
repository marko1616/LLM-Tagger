<template>
    <div class="rete" ref="rete"></div>
</template>

<script lang="ts">
import { defineComponent, ComponentPublicInstance } from 'vue'
import { reteEditor } from './ContextTree'

export default defineComponent({
  data() {
    return {
      editor: null as reteEditor | null,
    };
  },
  mounted() {
    this.editor = new reteEditor(this.$refs.rete as HTMLElement)
  },
  methods: {
    createUserAssistantPairs(): void {
      this.editor?.createUserAssistantPairs()
    },
  }
})

export type ContextTreeInstance = ComponentPublicInstance<{
  createUserAssistantPairs: () => void;
}>;
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.rete {
  display: flex;

  height: 100%;
  width: 100%;
}
</style>
