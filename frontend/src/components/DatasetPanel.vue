<template>
  <div class="dataset-panel">
    <simplebar>
      <ul class="dataset-list" ref="datasetListRef">
        <input @input="(_event) => {flushDatasets(true)}" v-model="datasetFilterText" class="search" placeholder="Search item..." />
        <li class="create" @click="(event) => {flipDropdownState(event)}" @click.stop>
          <div class="dropdown-list" @click.stop>
            <input class="input" placeholder="Enter name" ref="createDatasetNameRef"/>
            <div class="item create" @click="() => {createDataset($refs.createDatasetNameRef.value)}">Do create</div>
          </div>
          <p>Create new dataset</p>
        </li>
        <li v-for="dataset in filteredDatasets" :key="dataset.name"
          @click="(event) => {flipDropdownState(event)}"
          @contextmenu.prevent="openContextMenu($event, ['create', 'delete'], dataset.name)"
          @click.stop>
          <div class="dropdown-list" @click.stop>
            <input class="search" placeholder="Search item..." />
            <div class="item" v-for="item in dataset.items" :key="item.name"
            @click="openItem(dataset.name, item.name)"
            @contextmenu.prevent.stop="openContextMenu($event, ['delete'], dataset.name, item.name)"
            @click.stop>
              {{ item.name }}
            </div>
          </div>
          <p>{{ dataset.name }}</p>
        </li>
      </ul>
    </simplebar>
    <transition name="context-menu"><div class="context-menu" v-show="contextMenuOpened" ref="contextMenuRef" @click.stop>
      <input class="input" placeholder="Enter new item name" ref="createItemNameRef" v-show="contextMenuTypes.includes('create') && contextMenuTargetType === 'dataset'"/>
      <div class="item"
        @click="() => {doCreateItem($refs.createItemNameRef.value)}"
        @click.stop
        v-show="contextMenuTypes.includes('create') && contextMenuTargetType === 'dataset'">
        Create item
      </div>
      <div class="item"
        @click="() => {doDelete()}"
        @click.stop
        v-show="contextMenuTypes.includes('delete') && contextMenuTargetType == 'dataset'">
        Delete dataset
      </div>
      <div class="item"
        @click="() => {doDelete()}"
        @click.stop
        v-show="contextMenuTypes.includes('delete') && contextMenuTargetType == 'item'">
        Delete item
      </div>
    </div></transition>
  </div>
</template>

<script lang="ts">
import axios from 'axios'
import { AxiosError } from 'axios'
import { defineComponent, ref } from 'vue'
import { ContextMenuTargetType, Role, DatasetItem, Dataset, DatasetSummary } from '@/types/dataset'

import simplebar from 'simplebar-vue'
import 'simplebar-vue/dist/simplebar.min.css'

export default defineComponent({
  components: {
    simplebar
  },
  emits: {
    'openItem': (_dataset: DatasetItem) => {
      return true
    } 
  },
  methods: {
    async openItem(datasetName: string, itemName: string) {
      const response = await axios.get(`/datasets/${datasetName}/${itemName}`)
      await this.$router.push(`/edit/${datasetName}/${itemName}`)
      this.$emit('openItem', response.data.item as DatasetItem)
    },
    openContextMenu(event: MouseEvent, types: string[], datasetName: string, itemName: string | null = null) {
      this.contextMenuOpened = true
      this.contextMenuTypes = types
      new Promise((_resolve) => {
        if(this.$refs.contextMenuRef instanceof HTMLElement) {
          this.$refs.contextMenuRef.style.left = `${event.clientX}px`
          this.$refs.contextMenuRef.style.top = `${event.clientY}px`
        }
      })

      if(itemName === null) {
        this.contextMenuTargetType = ContextMenuTargetType.DATASET
      } else {
        this.contextMenuTargetType = ContextMenuTargetType.ITEM
      }

      this.contextMenuTargetDataset = datasetName
      this.contextMenuTargetItem = itemName

      this.foldDropdowns()
    },
    closeContextMenu() {
      this.contextMenuOpened = false
    },
    doCreateItem(itemName: string) {
      axios.post(`/datasets/${this.contextMenuTargetDataset}/create`, {
        name: itemName,
        nodeItems: [
          {
            role: Role.SYSTEM,
            nodePosition: {
              x: 0,
              y: 0
            },
            nodeSize: {
              width: 256,
              height: 64
            },
            positive: '',
            negative: '',
            to: []
          }
        ]
      }).then((_response) => {
        this.flushDatasets()
      })
    },
    doDelete() {
      if(this.contextMenuTargetType === ContextMenuTargetType.DATASET) {
        if(confirm(`Are you sure you want to delete dataset ${this.contextMenuTargetDataset}?`)) {
          axios.delete(`/datasets/${this.contextMenuTargetDataset}`).then((_response) => {
            this.flushDatasets()
          })
        }
      } else if(this.contextMenuTargetType === ContextMenuTargetType.ITEM) {
        if(confirm(`Are you sure you want to delete item ${this.contextMenuTargetItem} from dataset ${this.contextMenuTargetDataset}?`)) {
          axios.delete(`/datasets/${this.contextMenuTargetDataset}/${this.contextMenuTargetItem}`).then((_response) => {
            this.flushDatasets()
          })
        }
      }
      this.closeContextMenu()
    },
    createItem(datasetName: string, itemName: string) {
      const item: DatasetItem = {
        name: itemName,
        nodeItems: [
          {
            role: Role.SYSTEM,
            nodePosition: {
              x: 0,
              y: 0
            },
            nodeSize: {
              width: 256,
              height: 64
            },
            positive: '',
            negative: '',
            to: []
          }
        ]
      }

      axios.post(`/datasets/${datasetName}/create`, item).then((_response) => {
        this.flushDatasets()
      })
    },
    createDataset(name: string) {
      const dataset: Dataset = {
        name: name,
        timestamp: Date.now(),
        override: true,
        items: []
      }

      axios.post('/datasets/create', dataset).then((_response) => {
        this.flushDatasets()
      })

      this.foldDropdowns()
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
        const response = await axios.get('/datasets/list')
        this.datasetsCache.length = 0
        this.filteredDatasets.length = 0

        const datasetPromises = response.data.datasets.map(async (datasetName: string) => {
          const datasetResponse = await axios.get(`/datasets/${datasetName}/list`)
          return {
            name: datasetName,
            items: datasetResponse.data.items.map((itemName: string) => ({ name: itemName }))
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
        if(error instanceof AxiosError) {
          if(error.response?.status === 401) {
            this.$router.push('login/')
          }
        }
      }
    },
    foldDropdowns(except?: HTMLElement) {
      const dropdowns = this.datasetListRef?.querySelectorAll('.dropdown-active')
      dropdowns?.forEach((dropdown) => {
        if(dropdown !== except) {
          dropdown.classList.remove('dropdown-active')
        }
      })
    },
    flipDropdownState(event: MouseEvent) {
      const target = event.currentTarget
      if(target instanceof HTMLElement) {
        if (target.classList.contains('dropdown-active')) {
          target.classList.remove('dropdown-active')
        } else {
          this.foldDropdowns(target)
          target.classList.add('dropdown-active')
        }
      }
      this.closeContextMenu()
    },
    globalClick() {
      this.foldDropdowns()
      this.contextMenuOpened = false
    }
  },
  mounted() {
    this.flushDatasets()
    document.addEventListener('click', this.globalClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.globalClick)
  },
  setup() {
    const datasetsCache: DatasetSummary[] = []
    const datasetListRef = ref<HTMLElement | null>(null)
    const datasetDroppedDown = ref(false)
    const filteredDatasets = ref<DatasetSummary[]>([])
    const datasetFilterText = ref('')
    const contextMenuOpened = ref(false)
    const contextMenuTypes = ref<string[]>([])
    const contextMenuTargetType = ref<string>(ContextMenuTargetType.DATASET)
    const contextMenuTargetDataset = ref<string>('')
    const contextMenuTargetItem = ref<string|null>(null)
    return {
      datasetsCache,
      datasetFilterText,
      datasetListRef,
      datasetDroppedDown,
      filteredDatasets,
      contextMenuOpened,
      contextMenuTypes,
      contextMenuTargetType,
      contextMenuTargetDataset,
      contextMenuTargetItem,
    }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;
@use "sass:color";

.context-menu-enter-from,
.context-menu-leave-to  {
  opacity: 0;
  transform: translateY(2em);
}

.context-menu {
  position: absolute;
  display: flex;
  flex-direction: column;
  padding: 0.75em;
  margin: 0;
  color: $content-color;
  user-select: none;
  background-color: $dropdown-list-bg-color;
  transition: all 0.3s ease;

  & > * {
    margin: 0.25em;
  } 

  & .input,
  .search {
    box-sizing: border-box;
    display: flex;
    color: $content-color;
    outline: none;
    background: $dropdown-list-bg-color;
    border: 0;
  }
}

.dataset-panel {
  display: flex;
  width: 100%;
  max-height: 100%;
  border: 0.2em solid $container-border-color;
  border-radius: 1em;
}

.dropdown-list {
  position: fixed;
  z-index: 512;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
  font-size: large;
  pointer-events: none;
  background-color: $dropdown-list-bg-color;
  transition: all 0.3s ease;

  & .input,
  .search {
    box-sizing: border-box;
    display: flex;
    margin: 0.75vh 0.5vw 0.25vh;
    color: $content-color;
    outline: none;
    background: $dropdown-list-bg-color;
    border: 0;
  }

  & .item {
    box-sizing: border-box;
    display: flex;
    width: 90%;
    padding: 0.25vh 0.5vw;
    margin-bottom: 0.5vh;
    color: $dropdown-list-item-color;
    cursor: pointer;
    user-select: none;
    background-color: $dropdown-list-bg-color;
    border-radius: 0.25em;
    transition: all 0.2s ease;

    &:hover,
    &.selected {
      color: $dropdown-list-item-hover-color;
      background-color: $dropdown-list-bg-hover-color;
    }
  }
}

.dataset-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 0;

  & > .search {
    display: flex;
    padding: 0.25em 1em;
    margin: 0.5em;
    font-size: 1.25em;
    color: $content-color;
    outline: none;
    background: $dropdown-list-bg-color;
    border-color: $container-border-color;
    border-width: 0;
    border-radius: 0.25em;
    transition: all 0.3s ease;

    &::placeholder {
      color: color.adjust($content-color, $lightness: 20%);
    }
  }

  & li {
    display: flex;
    justify-content: center;
    padding-top: 0.25em;
    padding-bottom: 0.25em;
    margin: 0.1em 0.5em;
    font-size: 1.25em;
    color: $content-color;
    cursor: pointer;
    user-select: none;
    list-style-type: none;
    border-radius: 0.25em;
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
      margin: 0;
    }

    &.dropdown-active {
      & > .dropdown-list {
        pointer-events: all;
        opacity: 1;
        transform: translateY(2em);
      }
    }

    &:not(.dropdown-active) {
      & > .dropdown-list {
        pointer-events: none;
        opacity: 0;
        transform: translateY(10em);
      }
    }
  }
}

[data-simplebar] {
  width: 100%;
}
</style>
