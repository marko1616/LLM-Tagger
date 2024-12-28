<template>
  <div class="data-input-container" :class="{ 'is-collapsed': data.collapsed.value }">
    <textarea
      class="data-input"
      ref="textareaRef"
      v-model="data.value.value"
      @pointerdown.stop=""
      @input="data.onInput"
    ></textarea>
    <div class="toggle-button"
        @pointerdown.stop=""
        @dblclick.stop=""
        @click="data.onCollapse(textareaRef)">
        {{ data.collapsed.value ? '展开' : '折叠' }}
  </div>
  </div>
</template>

<script lang="ts">
import { ref, watch } from 'vue'
import { PromptTextArea } from './TextArea'

interface Props {
  data: PromptTextArea;
}

export default {
  props: {
    data: {
      type: PromptTextArea,
      required: true
    }
  },
  setup(props: Props) {
    const textareaRef = ref<HTMLTextAreaElement | null>(null)
    watch(() => props.data.value.value, (newValue) => {
      if(textareaRef.value == null) {
        return
      }
      if(props.data.collapsed.value) {
        textareaRef.value.style.height = 'auto'
      } else {
        textareaRef.value.style.height = 'auto'
        textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
      }
    })
    return {
      textareaRef
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.data-input-container {
  display: flex;
  flex-grow: 0;
  flex-direction: column;

  .toggle-button {
    display: flex;
    align-items: center;
    justify-content: center;

    background-color: #00000000;
    border-color: #00000000;
    color: $content-color;
    border-radius: 5px;

    padding: 10px;
    margin-top: -40px;
  }

  .data-input {
    display: flex;
    overflow-y: none;
    overflow: hidden;
    caret-color: $content-color;

    color: $content-color;
    min-width: 10vw;
    max-width: 100%;
    padding: 10px;
    font-size: 16px;
    font-weight: 300;
    text-wrap-mode: nowrap;
    line-height: 1.2;
    border: 1px solid $content-border-color;
    border-radius: 5px;
    background-color: $content-bg-color;
    word-wrap: break-word;
    min-height: 4vh;
    outline: none;

    flex-direction: column;
    align-items: flex-start;

    transition: background-color 0.3s ease, color 0.3s ease;
    transition: border-color 0.3s ease, color 0.3s ease;
    transition: box-shadow 0.3s ease;

    &:hover {
      border-color: $content-border-select-color;
      box-shadow: 0 0 5px $content-border-select-color;
    }
  }

  &.is-collapsed {
    .data-input {
      height: 50px;
    }

    .toggle-button {
      user-select: none;
      background: linear-gradient(to top, rgba($content-bg-color, 1), rgba($content-bg-color, 0));
    }
  }
}
</style>
