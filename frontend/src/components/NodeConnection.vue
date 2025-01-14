<template>
  <svg data-testid="connection">
    <path :d="path"></path>
  </svg>
</template>

<script>
import {defineComponent} from 'vue'

export default defineComponent({
  props: ['data', 'start', 'end', 'path']
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

svg {
  overflow: visible !important;
  position: absolute;
  pointer-events: none;
  width: 100vw;
  height: 100vh;

  path {
    fill: none;
    stroke-width: 5px;
    stroke: $connection-color;
    pointer-events: auto;
    transition: stroke-width 0.3s ease;
    &:hover {
        stroke-width: 10px;
    }
  }
}
</style>
