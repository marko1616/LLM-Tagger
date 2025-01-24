<template>
    <div class="socket" :title="data.name"></div>
</template>

<script>
export default {
  props: ['data']
}
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;
@use "sass:color";

.socket {
    z-index: 2;
    box-sizing: border-box;
    display: inline-block;
    width: 20px;
    height: 20px;
    vertical-align: middle;
    cursor: pointer;
    background: $socket-color;
    border: 2px solid $content-border-color;
    border-radius: 50%;
    transition: transform 0.3s ease, border-color 0.3s ease;

    &:hover {
        background: color.adjust($socket-color, $lightness: 10%);
        border-color: color.adjust($content-border-color, $lightness: -10%);
        transform: scale(1.2);
    }
}
</style>
