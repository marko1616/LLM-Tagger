<template>
  <div class="dataset-panel">
    <simplebar>
      <div>
      <ui class="dataset-list" ref="datasetListRef">
        <li>Create new dataset</li>
        <li v-for="dataset in datasets" :key="dataset" @click="(event) => {flipDropdownState(event)}" @click.stop>
          <div class="dropdown-list" @click.capture.stop>
            <input class="search" placeholder="Search item..." />
            <div class="item" @click="createDataset">Create new item</div>
            <div class="item" v-for="dataset in datasets" :key="dataset">
              {{ dataset }}
            </div>
          </div>
          <p>{{ dataset }}</p>
        </li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
        <li>PAD</li>
      </ui></div>
    </simplebar>
  </div>
</template>

<script lang="ts">
import axios from 'axios'
import { defineComponent, ref } from 'vue'

import simplebar from 'simplebar-vue';
import 'simplebar-vue/dist/simplebar.min.css';

enum Role {
  SYSTEM = 'system',
  USER = 'user',
  ASSISTANT = 'assistant',
  TOOL = 'tool',
}

type NodePosition = {
  x: number
  y: number
}

type NodeItem = {
  role: Role
  nodePosition: NodePosition
  positive: string
  negative?: string
}

type DatasetItem = {
  name?: string
  nodeItems: NodeItem[]
}

type Dataset = {
  name: string
  timestamp: number
  override: boolean
  items: DatasetItem[]
}

export default defineComponent({
  components: {
    simplebar
  },
  methods: {
    createDataset() {
      const dataset: Dataset = {
        name: 'test',
        timestamp: Date.now(),
        override: true,
        items: []
      }

      axios.post('/api/datasets/create', dataset).then((response) => {
        this.flushDatasets()
      })
    },
    flushDatasets() {
      axios.get('/api/datasets/list').then((response) => {
        this.datasets.length = 0
        this.datasets.push(...response.data.datasets)
      })
    },
    flipDropdownState(event: MouseEvent) {
      const target = event.currentTarget
      if(target instanceof HTMLElement) {
        if (target.classList.contains('dropdown-active')) {
          target.classList.remove('dropdown-active');
        } else {
          target.classList.add('dropdown-active');
        }
      }
    },
    disableDropdownStates() {
      const dropdowns = this.datasetListRef?.querySelectorAll('.dropdown-active')
      dropdowns?.forEach((dropdown) => {
        dropdown.classList.remove('dropdown-active')
      })
    }
  },
  mounted() {
    this.flushDatasets()
    document.addEventListener('click', this.disableDropdownStates);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.disableDropdownStates);
  },
  setup() {
    const datasetListRef = ref<HTMLElement | null>(null)
    const datasetDroppedDown = ref(false)
    const datasets = ref<string[]>([])
    return { datasetListRef, datasetDroppedDown, datasets }
  },
})
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.dataset-panel {
  display: flex;
  width: 100%;
  max-height: 100%;

  border: 0.2em solid $container-border-color;
  border-radius: 1em;
}

.dataset-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;

  & li {
    cursor: pointer;
    user-select: none;
    display: flex;
    justify-content: center;
    list-style-type: none;
    color: $content-color;
    font-size: 1.25em;
    padding-top: 0.25em;
    padding-bottom: 0.25em;
    border-radius: 0.25em;
    margin: 0.5em 0.5em 0.5em 0.5em;

    transition: all 0.3s ease;

    &:hover {
      color: $content-color-dark;
      background: $dropdown-btn-bg-color;
    }

    & .item-padding {
      flex-grow: 10;
    }

    & p {
      max-height: 1em;
      margin: 0em;
    }

    &.dropdown-active {
      & .dropdown-list {
        pointer-events: all;
        opacity: 1;
        transform: translateY(2em);
      }
    }

    &:not(.dropdown-active) {
      & .dropdown-list {
        pointer-events: none;
        opacity: 0;
        transform: translateY(10em);
      }
    }
  }
}

.dropdown-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: fixed;
  pointer-events: none;
  z-index: 512;

  margin-top: 10px;
  background-color: $dropdown-list-bg-color;
  transition: all 0.3s ease;
  font-size: large;

  & .search {
    display: flex;
    box-sizing: border-box;
    margin-top: 0.75vh;
    margin-bottom: 0.25vh;
    margin-left: 0.5vw;
    margin-right: 0.5vw;
    border: 0;

    background: $dropdown-list-bg-color;
    color: $content-color;
    outline: none;
  }

  & .item {
    cursor: pointer;
    user-select: none;

    display: flex;
    padding-top: 0.25vh;
    padding-bottom: 0.25vh;
    padding-left: 0.5vw;
    padding-right: 0.5vw;
    margin-bottom: 0.5vh;
    width: 90%;
    box-sizing: border-box;

    border-radius: 0.25em;
    color: $dropdown-list-item-color;
    background-color: $dropdown-list-bg-color;

    transition: all 0.2s ease;

    &:hover {
      background-color: $dropdown-list-bg-hover-color;
      color: $dropdown-list-item-hover-color;
    }
  }
}

[data-simplebar] {
  width: 100%;
}
</style>
