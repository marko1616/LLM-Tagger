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
    getData(): void {
      console.log(this.editor?.getNodes())
      console.log(this.editor?.getConnections())
    },

    createUserAssistantPairs(): void {
      this.editor?.createUserAssistantPairs()
    },
  }
})

export type ContextTreeInstance = ComponentPublicInstance<{
  getData: () => void;
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
