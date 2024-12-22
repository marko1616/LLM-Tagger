<template>
    <div class="rete" ref="rete"></div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {createEditor} from './ContextTree'

export default defineComponent({
  name: 'TextTree',
  mounted() {
    createEditor(this.$refs.rete as HTMLElement)
  }
})
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.rete {
  display: flex;

  height: 100%;
  width: 100%;
}
</style>
