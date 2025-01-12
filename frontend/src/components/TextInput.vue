<template>
  <div class="data-input-container">
    <div class="title-container">
        <div class="title" data-testid="title" @click="doEditingNode" @pointerdown.stop="">{{ data.title.value }}</div>
        <div class="title-padding"></div>
      </div>
    <textarea
      class="data-input"
      ref="textareaRef"
      v-model="data.value.value"
      @pointerdown.stop=""
      @input="data.onInput"
    ></textarea>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { PromptTextInput } from './TextInput'

import { editingControl, openOuterEditor } from './NodeEditorStore'

interface Props {
  data: PromptTextInput;
}

export default defineComponent({
  props: {
    data: {
      type: PromptTextInput,
      required: true
    }
  },
  methods: {
    doEditingNode() {
      editingControl.controlId = this.data.id
      editingControl.data = this.data.value.value
      openOuterEditor.value()
    }
  },
  mounted() {
    if(this.textareaRef) {
      if(this.data.size) {
        this.textareaRef.style.height = `${this.data.size.height}px`
        this.textareaRef.style.width = `${this.data.size.width}px`
      }
      this.observer.observe(this.textareaRef)
    }
  },
  setup(props: Props) {
    const textareaRef = ref<HTMLTextAreaElement | null>(null)
    watch(editingControl, (newValue, oldValue) => {
      if(editingControl.controlId == props.data.id) {
        props.data.value.value = newValue.data
      }
    })
    const observer = new ResizeObserver((entries) => {
      const textAreaSize = entries[0].contentRect
      props.data.saveSize(textAreaSize)
    })
    return {
      observer,
      textareaRef
    }
  }
})
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.data-input-container {
  & .title {
    cursor: pointer;
    display: flex;
    user-select: none;
    color: $content-color;
    font-family: sans-serif;
    font-size: 14px;
    padding: 4px;
    text-align: center;

    transition: all 0.3s ease;
  }

  & .title:hover {
    color: $content-select-color;
  }

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
    overflow: hidden;
    caret-color: $content-color;
    color: $content-color;
    min-width: 256px;
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
    transition: box-shadow 0.3s ease;

    &:hover {
      border-color: $content-border-select-color;
      box-shadow: 0 0 0 1px $content-border-select-color;
    }
  }
}
</style>
