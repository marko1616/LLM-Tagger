<template>
  <div class="dataset-panel">
    <div class="dropdown-container">
      <div class="dropdown" :class="{ 'dropdown-active': datasetDroppedDown }" @click="() => {datasetDroppedDown = !datasetDroppedDown}">Select Dataset<i class="dropdown-arrow uil uil-arrow-down"></i></div>
      <div class="dropdown-list-container">
        <div class="dropdown-list" :class="{ 'dropdown-active': datasetDroppedDown }">
          <input class="search" placeholder="Search dataset..." />
          <div class="item" @click="createDataset">Create new</div>
          <div class="item" v-for="dataset in datasets" :key="dataset">
            {{ dataset }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import axios from 'axios'
import { defineComponent, ref } from 'vue'

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
    }
  },
  mounted() {
    this.flushDatasets()
  },
  setup() {
    const datasetDroppedDown = ref(false)
    const datasets = ref<string[]>([])
    return { datasetDroppedDown, datasets }
  }
})
</script>

<style lang="scss" scoped>
@import "@/styles/color.scss";

.dropdown-container {
  display: flex;
  flex-direction: column;
  margin: 10px;
}

.dropdown {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  user-select: none;
  background: $dropdown-btn-bg-color;
  color: $dropdown-btn-color;
  border-radius: 10px;

  padding-left: 0.5vw;
  padding-right: 0.5vw;
  padding-top: 0.5vh;
  padding-bottom: 0.5vh;

  &.dropdown-active {
    & .dropdown-arrow {
      display: flex;
      font-size: 24px;
      margin-left: 10px;
      transform: rotate(180deg);
      transition: transform 0.3s ease;
    }
  }

  &:not(.dropdown-active) {
    & .dropdown-arrow {
      display: flex;
      font-size: 24px;
      margin-left: 10px;
      transition: transform 0.3s ease;
    }
  }
}

.dropdown-list-container {
  margin: 0;
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

  opacity: 0;
  transform: translateY(5vh);
  transition: all 0.3s ease;

  font-size: large;

  &.dropdown-active {
    pointer-events: all;
    opacity: 1;
    transform: translateY(0);
  }

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

    border-radius: 2.5px;
    color: $dropdown-list-item-color;
    background-color: $dropdown-list-bg-color;

    transition: all 0.2s ease;

    &:hover {
      background-color: $dropdown-list-bg-hover-color;
      color: $dropdown-list-item-hover-color;
    }
  }
}
</style>