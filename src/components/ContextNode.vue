<template>
    <div
      class="node"
      :class="{ selected: data.selected }"
      data-testid="node"
    >
      <div class="title" data-testid="title">{{ data.label }}</div>

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
import {defineComponent, PropType} from 'vue'
import {Ref} from 'rete-vue-plugin'

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
  key: string;
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
    }
  },
  components: {
    Ref
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

  & .title {
    display: flex;
    color: $content-color;
    font-family: sans-serif;
    font-size: 18px;
    padding: 4px;
    text-align: center;
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

<style lang="scss">
@import "@/styles/color.scss";

[rete-context-menu] {
  width: 40vw;
  min-width: 100px;
  max-width: 800px;
  background: $container-bg-color;
  border: 2px solid $container-border-color;
  border-radius: 10px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;

  &:hover {
    border-color: $container-border-hover-color;
  }

  .block {
    background: $container-bg-color;
    border-radius: 0.5vw;
    border: 0px;
    display: flex;
    align-items: center;
    transition: background 0.2s ease;

    &.item {
      cursor: pointer;
      border: 0.1vw solid transparent;
    }

    &:hover {
      background: $container-bg-hover-color !important;
      border-color: $container-border-hover-color !important;
      color: $content-color !important;
    }

    &:focus-visible {
      outline: 0px;
    }
  }

  .block:first-child input {
    width: 100%;
    background: $container-input-bg-color;
    color: $content-color;
    border: 2px solid $container-border-color;
    border-radius: 10px;
    outline: none;
    transition: all 0.3s ease;

    &:focus {
      background: $container-bg-hover-color;
      border-color: $container-border-hover-color;
    }
  }

  .search {
    color: $content-color;
    font-size: 1.4vh;
  }
}
</style>
