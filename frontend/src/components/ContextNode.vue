<template>
    <div
      class="node"
      :class="{ selected: data.selected }"
      data-testid="node"
    >
      <div class="title-container">
        <div class="title" data-testid="title" @click="doEditingNode" @pointerdown.stop="">{{ data.label }}</div>
        <div class="title-padding"></div>
      </div>

      <!-- Inputs -->
      <div class="inputs">
        <div
          class="input"
          v-for="[key, input] in inputs()"
          :key="key + seed"
          :data-testid="'input-' + key"
        >
          <Ref
            class="input-socket"
            :emit="emit"
            :data="{
              type: 'socket',
              side: 'input',
              key: key,
              nodeId: data.id,
              payload: input.socket,
            }"
            data-testid="input-socket"
          />
          <div
            class="input-title"
            v-show="!input.control || !input.showControl"
            data-testid="input-title"
          >
            {{ input.label }}
          </div>
          <Ref
            class="input-control"
            v-show="input.control && input.showControl"
            :emit="emit"
            :data="{ type: 'control', payload: input.control }"
            data-testid="input-control"
          />
        </div>
      </div>

      <!-- Controls -->
      <div class="controls">
        <Ref
          class="control"
          v-for="[key, control] in controls()"
          :key="key + seed"
          :emit="emit"
          :data="{ type: 'control', payload: control }"
          :data-testid="'control-' + key"
        />
      </div>

      <!-- Outputs -->
      <div class="outputs">
        <div
          class="output"
          v-for="[key, output] in outputs()"
          :key="key + seed"
          :data-testid="'output-' + key"
        >
          <div class="output-title" data-testid="output-title">
            {{ output.label }}
          </div>
          <Ref
            class="output-socket"
            :emit="emit"
            :data="{
              type: 'socket',
              side: 'output',
              key: key,
              nodeId: data.id,
              payload: output.socket,
            }"
            data-testid="output-socket"
          />
        </div>
      </div>
    </div>
</template>

<script lang="ts">
import {defineComponent, PropType, watch} from 'vue'
import {Ref} from 'rete-vue-plugin'

import { editingNode, openOuterEditor } from './ContextTreeStore'

interface NodeData {
  id: string;
  label: string;
  selected: boolean;
  width?: number;
  height?: number;
  inputs: Record<string, InputData>;
  outputs: Record<string, OutputData>;
  controls: Record<string, ControlData>;
}

interface InputData {
  label: string;
  control?: ControlData;
  showControl?: boolean;
  socket: any;
  index?: number;
}

interface OutputData {
  label: string;
  socket: any;
  index?: number;
}

interface ControlData {
  getData: () => string;
  update: (data: string) => void;
}

/**
 * Sorts an array of entries by the `index` property of the value.
 *
 * @template T - The value type in the entries
 * @param {[string, T & {index?: number}][]} entries - The array of entries to sort
 * @returns {[string, T][]} The sorted array of entries
 */
function sortByIndex<T>(
    entries: [string, T & { index?: number }][]
): [string, T][] {
  return entries.sort((a, b) => {
    const indexA = a[1].index ?? 0
    const indexB = b[1].index ?? 0
    return indexA - indexB
  })
}

export default defineComponent({
  props: {
    data: {
      type: Object as PropType<NodeData>,
      required: true
    },
    emit: Function as PropType<(event: string, payload: any) => void>,
    seed: Number
  },
  methods: {
    inputs() {
      return sortByIndex(Object.entries(this.data.inputs))
    },
    outputs() {
      return sortByIndex(Object.entries(this.data.outputs))
    },
    controls() {
      return sortByIndex(Object.entries(this.data.controls))
    },
    doEditingNode() {
      const control = this.data.controls['TextArea']
      editingNode.nodeId = this.data.id
      editingNode.data = control.getData()
      openOuterEditor.value()
    }
  },
  components: {
    Ref
  },
  setup(props) {
    watch(editingNode, (newValue, oldValue) => {
      const control = props.data.controls['TextArea']
      if(editingNode.nodeId == props.data.id) {
        control.update(newValue.data)
      }
    })
  }
})
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.node {
  display: flex;

  min-width: fit-content;
  min-height: fit-content;
  background-color: $container-bg-color;
  border: 2px solid $container-border-color;
  border-radius: 10px;
  box-sizing: border-box;
  padding: 8px;
  flex-direction: column;
  gap: 10px;

  transition: all 0.3s ease;

  & .title-container {
    display: flex;
  }

  & .title {
    cursor: pointer;
    display: flex;
    user-select: none;
    color: $content-color;
    font-family: sans-serif;
    font-size: 18px;
    padding: 4px;
    text-align: center;

    transition: all 0.3s ease;
  }

  & .title:hover {
    color: $content-select-color;
  }

  & .outputs,
  & .inputs,
  & .controls {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  & .output,
  & .input {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  & .output-title,
  & .input-title {
    display: flex;
    color: white;
    font-family: sans-serif;
    font-size: 14px;
  }

  & .output-socket,
  & .input-socket {
    display: flex;
    display: inline-flex;
  }

  & .control {
    display: flex;
    align-self: stretch;
  }

  &:hover {
    background-color: $container-bg-hover-color;
    border-color: $container-border-hover-color;
  }

  &.selected {
    background-color: $container-bg-select-color;
    border-color: $container-border-select-color;
  }
}
</style>