<template>
    <div class="socket" :title="data.name"></div>
</template>

<script>
export default {
  props: ['data']
}
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.socket {
    display: inline-block;
    cursor: pointer;
    border: 2px solid $content-border-color;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    vertical-align: middle;
    background: $socket-color;
    z-index: 2;
    box-sizing: border-box;
    transition: transform 0.3s ease, border-color 0.3s ease;

    &:hover {
        background: lighten($socket-color, 10%);
        transform: scale(1.2);
        border-color: darken($content-border-color, 10%);
    }
}
</style>
