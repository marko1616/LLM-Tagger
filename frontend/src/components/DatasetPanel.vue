<template>
  <div class="dataset-panel">
    <simplebar>
      <div><ui class="dataset-list" ref="datasetListRef">
        <input @input="(_event) => {flushDatasets(true)}" v-model="datasetFilterText" class="search" placeholder="Search item..." />
        <li class="create">Create new dataset</li>
        <li v-for="dataset in filteredDatasets" :key="dataset.name" @click="(event) => {flipDropdownState(event)}" @click.stop>
          <div class="dropdown-list" @click.capture.stop>
            <input class="search" placeholder="Search item..." />
            <div class="item create" @click="createDataset">Create new item</div>
            <div class="item" v-for="item in dataset.items" :key="item.name">
              {{ item }}
            </div>
          </div>
          <p>{{ dataset.name }}</p>
        </li>
      </ui></div>
    </simplebar>
  </div>
</template>

<script lang="ts">
import axios from 'axios'
import { defineComponent, ref } from 'vue'

import simplebar from 'simplebar-vue'
import 'simplebar-vue/dist/simplebar.min.css'

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
  name: string
  nodeItems: NodeItem[]
}

type DatasetItemSummary = {
  name: string
}

type Dataset = {
  name: string
  timestamp: number
  override: boolean
  items: DatasetItem[]
}

type DatasetSummary = {
  name: string
  items: DatasetItemSummary[]
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

      axios.post('/api/datasets/create', dataset).then((_response) => {
        this.flushDatasets()
      })
    },
    async flushDatasets(cache?: boolean) {
      if (cache) {
        this.filteredDatasets.length = 0
        this.datasetsCache.forEach((dataset) => {
          if (dataset.name.toLocaleLowerCase().includes(this.datasetFilterText)) {
            this.filteredDatasets.push(dataset)
          }
        })
        return
      }

      try {
        const response = await axios.get('/api/datasets/list')
        this.datasetsCache.length = 0
        this.filteredDatasets.length = 0

        const datasetPromises = response.data.datasets.map(async (datasetName: string) => {
          const datasetResponse = await axios.get(`/api/datasets/${datasetName}/list`)
          return {
            name: datasetName,
            items: datasetResponse.data
          }
        })

        const datasets = await Promise.all(datasetPromises)

        datasets.forEach((dataset) => {
          this.datasetsCache.push(dataset)
          if (dataset.name.toLocaleLowerCase().includes(this.datasetFilterText)) {
            this.filteredDatasets.push(dataset)
          }
        })
      } catch (error) {
        console.error('Error fetching datasets:', error)
      }
    },
    flipDropdownState(event: MouseEvent) {
      const target = event.currentTarget
      if(target instanceof HTMLElement) {
        if (target.classList.contains('dropdown-active')) {
          target.classList.remove('dropdown-active')
        } else {
          target.classList.add('dropdown-active')
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
    document.addEventListener('click', this.disableDropdownStates)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.disableDropdownStates)
  },
  setup() {
    const datasetsCache: DatasetSummary[] = []
    const datasetListRef = ref<HTMLElement | null>(null)
    const datasetDroppedDown = ref(false)
    const filteredDatasets = ref<DatasetSummary[]>([])
    const datasetFilterText = ref('')
    return { datasetsCache, datasetFilterText, datasetListRef, datasetDroppedDown, filteredDatasets }
  }
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

  & > .search {
    display: flex;
    background: $dropdown-list-bg-color;
    color: $content-color;
    outline: none;
    font-size: 1.25em;
    padding-top: 0.25em;
    padding-bottom: 0.25em;
    border-radius: 0.25em;
    margin: 0.5em 0.5em 0.5em 0.5em;
    padding-left: 1em;
    padding-right: 1em;
    border-width: 0;
    border-color: $container-border-color;
    border-radius: 0.25em;

    transition: all 0.3s ease;

    &::placeholder {
      color: lighten($content-color, 20%);
    }
  }

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
    margin-top: 0.1em;
    margin-bottom: 0.1em;
    margin-left: 0.5em;
    margin-right: 0.5em;

    transition: all 0.3s ease;

    &:hover,
    &.selected {
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

    &:hover,
    &.selected {
      background-color: $dropdown-list-bg-hover-color;
      color: $dropdown-list-item-hover-color;
    }
  }
}

[data-simplebar] {
  width: 100%;
}
</style>
