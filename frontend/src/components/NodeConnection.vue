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
  position: absolute;
  width: 100vw;
  height: 100vh;
  overflow: visible !important;
  pointer-events: none;

  path {
    pointer-events: auto;
    fill: none;
    stroke: $connection-color;
    stroke-width: 5px;
    transition: stroke-width 0.3s ease;

    &:hover {
        stroke-width: 10px;
    }
  }
}
</style>
