<template>
  <div class="dataset-panel">
    <div class="list-container" @mousedown="startSelection" @wheel="handleSelection" @keydown="handleKeyDown">
      <div v-if="isSelecting" class="selection-box" :style="selectionBoxStyle"></div>
      <simplebar>
        <ul class="dataset-list" ref="datasetListRef">
          <input v-model="datasetSearchQuery" class="search" placeholder="Search dataset..." />
          <li class="create" @click="(event) => {flipDropdownState(event)}" @click.stop>
            <div class="dropdown-list" @click.stop>
              <input class="input" placeholder="Enter name"/>
              <div class="item create" @click="(event) => {createDataset(((event.target as HTMLDivElement).previousElementSibling as HTMLInputElement).value)}">Do create</div>
            </div>
            <p>Create new dataset</p>
          </li>
          <li
            v-for="datasetSummary in datasetSummaries.filter((dataset) => {return !datasetSearchQuery || dataset.name.toLocaleLowerCase().includes(datasetSearchQuery)})" :key="datasetSummary.name"
            :dataset-name="datasetSummary.name"
            :class="{ selected: selectedDataset === datasetSummary.name }"
            @click="selectDataset(datasetSummary.name)"
            @contextmenu.prevent="openContextMenu($event, datasetSummary.name)"
            @click.stop>
            <p @click="datasetSummary.show = !datasetSummary.show">{{ datasetSummary.name }}</p>
            <transition name="item-list"><ul class="item-list" v-show="datasetSummary.show">
              <input v-model="datasetSummary.searchQuery" class="search" placeholder="Search item..."/>
              <li class="create" @click="(event) => {flipDropdownState(event)}" @click.stop>
                <div class="dropdown-list" @click.stop>
                  <input class="input" placeholder="Enter name"/>
                  <div class="item create" @click="(event: MouseEvent) => {createItem(datasetSummary.name,((event.target as HTMLDivElement).previousElementSibling as HTMLInputElement).value)}">Do create</div>
                </div>
                <p>Create new item</p>
              </li>
              <li class="dataset-item"
              v-for="item in datasetSummary.items.filter((item) => {return !datasetSummary.searchQuery || item.name.toLocaleLowerCase().includes(datasetSummary.searchQuery)})" :key="item.name"
              :dataset-name="datasetSummary.name"
              :item-name="item.name"
              :class="{ selected: selectedItems.some((selectedItem) => selectedItem.datasetName === datasetSummary.name && selectedItem.itemName === item.name) }"
              @click="selectItem(datasetSummary.name, item.name)"
              @dblclick="loadItem(datasetSummary.name, item.name)"
              @contextmenu.prevent.stop="openContextMenu($event, datasetSummary.name, item.name)"
              @click.stop>
                {{ item.name }}
              </li>
            </ul></transition>
          </li>
        </ul>
      </simplebar>
      <transition name="context-menu"><div class="context-menu" v-show="contextMenuOpened" ref="contextMenuRef" @click.stop>
        <div class="item"
          @click="doDelete()"
          @click.stop
          v-show="contextMenuTargetType == 'dataset'">
          Delete dataset
        </div>
        <div class="item"
          @click="doDelete()"
          @click.stop
          v-show="contextMenuTargetType == 'item'">
          Delete item
        </div>
      </div></transition>
    </div>
    <div class="btn-container">
      <button @click="saveHandler">Save</button>
      <button @click="saveAsHandler">Save as selected</button>
    </div>
  </div>
</template>

<script lang="ts">
import axios from 'axios'
import { AxiosError } from 'axios'
import { defineComponent, ref } from 'vue'
import { ContextMenuTargetType, Role, DatasetItem, Dataset, DatasetSummary } from '@/types/dataset'

import simplebar from 'simplebar-vue'

type SelectedItem = {
  datasetName: string | null,
  itemName: string | null
}

export default defineComponent({
  components: {
    simplebar
  },
  emits: {
    'loadItem': (_datasetName: string, _itemName: string) => {
      return true
    },
    'saveCurrentItem': (_datasetName: string, _itemName: string) => {
      return true
    }
  },
  computed: {
    selectionBoxStyle() {
      const left = Math.min(this.startX, this.endX);
      const top = Math.min(this.startY, this.endY);
      const width = Math.abs(this.startX - this.endX);
      const height = Math.abs(this.startY - this.endY);
      return {
        left: `${left}px`,
        top: `${top}px`,
        width: `${width}px`,
        height: `${height}px`,
      };
    },
  },
  methods: {
    async loadItem(datasetName: string, itemName: string) {
      if(!await this.$router.push(`/edit/${datasetName}/${itemName}`)) {
        this.$emit('loadItem', datasetName, itemName) 
      }
    },
    saveHandler() {
      const pathPart = this.$router.currentRoute.value.path.split('/')
      if(pathPart.length === 4) {
        const datasetName = pathPart[2]
        const itemName = pathPart[3]
        this.$emit('saveCurrentItem', datasetName, itemName)
      }
    },
    saveAsHandler() {
      if(this.selectedItems.length !== 1) {
        alert('Please select one item to save.')
        return
      }

      if(!this.selectedItems[0].datasetName || !this.selectedItems[0].itemName) {
        return
      }
      this.$emit('saveCurrentItem', this.selectedItems[0].datasetName, this.selectedItems[0].itemName)
    },
    selectItem(datasetName: string, itemName: string) {
      this.selectedItems = [{
        datasetName: datasetName,
        itemName: itemName
      }]
    },
    selectDataset(datasetName: string) {
      this.selectedDataset = datasetName
    },
    openContextMenu(event: MouseEvent, datasetName: string, itemName: string | null = null) {
      this.contextMenuOpened = true
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
    async doDelete() {
      try {
        if (this.contextMenuTargetType === ContextMenuTargetType.DATASET) {
          if (confirm(`Are you sure you want to delete dataset ${this.contextMenuTargetDataset}?`)) {
            await axios.delete(`/datasets/${this.contextMenuTargetDataset}`)
            this.flushDatasets()
          }
        } else if (this.contextMenuTargetType === ContextMenuTargetType.ITEM) {
          if (confirm(`Are you sure you want to delete item ${this.contextMenuTargetItem} from dataset ${this.contextMenuTargetDataset}?`)) {
            await axios.delete(`/datasets/${this.contextMenuTargetDataset}/${this.contextMenuTargetItem}`)
            this.flushDatasets()
          }
        }
      } catch (error) {
        console.error('Error deleting:', error)
      } finally {
        this.closeContextMenu()
      }
    },
    async createItem(datasetName: string, itemName: string) {
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

      await axios.post(`/datasets/${datasetName}/create`, item)
      this.flushDatasets()
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
    async flushDatasets() {
      try {
        const response = await axios.get('/datasets/list')
        this.datasetSummaries.length = 0

        const datasetPromises = response.data.datasets.map(async (datasetName: string) => {
          const datasetResponse = await axios.get(`/datasets/${datasetName}/list`)
          return {
            name: datasetName,
            show: false,
            searchQuery: '',
            items: datasetResponse.data.items.map((itemName: string) => ({ name: itemName }))
          }
        })

        const datasets = await Promise.all(datasetPromises)

        datasets.forEach((dataset) => {
          this.datasetSummaries.push(dataset)
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
    },
    getSelectedDataset() {
      return this.selectedDataset
    },
    startSelection(event: MouseEvent) {
      this.isSelecting = true;
      this.startX = event.clientX;
      this.startY = event.clientY;
      this.endX = event.clientX;
      this.endY = event.clientY;
      this.selectedItems = [];
    },
    endSelection() {
      this.isSelecting = false;
    },
    handleSelection(event: MouseEvent | WheelEvent) {
      if (this.isSelecting) {
        this.endX = event.clientX;
        this.endY = event.clientY;
        const selectionRect = {
          left: Math.min(this.startX, this.endX),
          top: Math.min(this.startY, this.endY),
          right: Math.max(this.startX, this.endX),
          bottom: Math.max(this.startY, this.endY),
        }
        this.datasetListRef?.querySelectorAll('.dataset-item')?.forEach((element) => {
          const itemRect = element.getBoundingClientRect()
          if(itemRect.left < selectionRect.right &&
            itemRect.right > selectionRect.left &&
            itemRect.top < selectionRect.bottom &&
            itemRect.bottom > selectionRect.top &&
            !this.selectedItems.some((selectedItems) => selectedItems.datasetName === element.getAttribute('dataset-name') && selectedItems.itemName === element.getAttribute('item-name'))
          ) {
            this.selectedItems.push({
              datasetName: element.getAttribute('dataset-name') as string,
              itemName: element.getAttribute('item-name') as string,
            })
          }
        })
      }
    },
    async handleKeyDown(event: KeyboardEvent) {
      if(event.key === 'Delete' && confirm(`Delete ${this.selectedItems.length} selected items?`)) {
        for(const item of this.selectedItems) {
          this.flushDatasets()
          await axios.delete(`/datasets/${item.datasetName}/${item.itemName}`)
        }
      }
      this.selectedItems = []
    }
  },
  mounted() {
    this.flushDatasets()
    document.addEventListener('click', this.globalClick)
    document.addEventListener('mousemove', this.handleSelection)
    document.addEventListener('mouseup', this.endSelection)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.globalClick)
    document.removeEventListener('mousemove', this.handleSelection)
    document.removeEventListener('mouseup', this.endSelection)
  },
  setup() {
    const datasetSummaries = ref<DatasetSummary[]>([])
    const datasetListRef = ref<HTMLElement | null>(null)
    const datasetDroppedDown = ref(false)
    const datasetSearchQuery = ref('')
    const contextMenuOpened = ref(false)
    const contextMenuTargetType = ref<string>(ContextMenuTargetType.DATASET)
    const contextMenuTargetDataset = ref<string>('')
    const contextMenuTargetItem = ref<string|null>(null)
    const selectedDataset = ref<string|null>(null)
    const selectedItems = ref<SelectedItem[]>([])

    const isSelecting = ref<boolean>(false)
    const startX = ref(0)
    const startY = ref(0)
    const endX = ref(0)
    const endY = ref(0)
    return {
      datasetSummaries,
      datasetSearchQuery,
      datasetListRef,
      datasetDroppedDown,
      contextMenuTargetType,
      contextMenuOpened,
      contextMenuTargetDataset,
      contextMenuTargetItem,
      selectedDataset,
      selectedItems,
      isSelecting,
      startX,
      startY,
      endX,
      endY
    }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;
@use "sass:color";

.selection-box {
  position: absolute;
  z-index: 128;
  pointer-events: none;
  background-color: rgba($selection-box-color, 0.5);
  border: 0.1em solid $selection-box-color;
  border-radius: 0.25em;
}

.dataset-panel {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  width: 100%;
  max-height: 50%;
}

.list-container {
  box-sizing: border-box;
  display: flex;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border: 0.2em solid $container-border-color;
  border-radius: 1em;
  clip-path: inset(0);
}

.btn-container {
  box-sizing: border-box;
  display: flex;
  justify-content: space-evenly;
  margin: 0.25em;

  & button {
    width: 10em;
    padding: 0.25em;
    color: $content-color-dark;
    background-color: $button-bg-color;
    border: 0;
    border-radius: 0.25em;
    transition: all 0.3s ease;

    &:hover {
      background-color: $button-hover-bg-color;
    }

    &:active {
      transform: scale(0.95);
    }
  }
}

.context-menu-enter-from,
.context-menu-leave-to  {
  opacity: 0;
  transform: translateY(2em);
}

.item-list-enter-from,
.item-list-leave-to {
  max-height: 0;
  opacity: 0;
}

.item-list-enter-to,
.item-list-leave-from {
  max-height: 100vh;
  opacity: 1;
}

.item-list-enter-active,
.item-list-leave-active {
  transition: all 0.3s ease;
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
  border-radius: 0.5em;
  transition: all 0.3s ease;

  & > * {
    margin: 0.25em;
  } 

  .search {
    box-sizing: border-box;
    display: flex;
    color: $content-color;
    outline: none;
    background: $dropdown-list-bg-color;
    border: 0;
  }
}

.dropdown-list {
  position: fixed;
  z-index: 512;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
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
    transition: all 0.3s ease;

    &:hover,
    &.selected {
      color: $dropdown-list-item-hover-color;
      background-color: $dropdown-list-bg-hover-color;
    }
  }
}

.item-list {
  display: flex;
  flex-direction: column;
  padding: 0;

  & p {
    display: flex;
    justify-content: center;
  }

  & > li {
    display: flex;
    margin: 0.25rem 0.5rem;
    list-style-type: none;
    border-radius: 0.25rem;
    transition: background 0.3s ease;

    &:hover,
    &.selected {
      color: $content-color-dark;
      background: $list-level2-selected-color;
    }

    & > .dropdown-list {
      padding-left: 0;
      transform: translateX(-0.5rem);
    }

    &.dropdown-active {
      & > .dropdown-list {
        pointer-events: all;
        opacity: 1;
        transform: translateY(1em);
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

  & > * {
    padding-left: 0.4rem;
  }

  & .search {
    display: flex;
    padding: 0.1rem 1rem;
    margin: 0.5rem;
    color: $content-color;
    outline: none;
    background: $dropdown-list-bg-color;
    border-color: $container-border-color;
    border-width: 0;
    border-radius: 0.25rem;
  }
}

/**
 * The `not(.item-list)` selector is used to prevent potential conflicts
 * and undefined behavior with `.item-list`. Although `.item-list` and
 * the current context cannot appear simultaneously, this exclusion is
 * necessary to satisfy the linter's requirements and ensure code
 * consistency.
 */
.dataset-list:not(.item-list) {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 0;

  & > .search {
    display: flex;
    padding: 0.25rem 1rem;
    margin: 0.5rem;
    color: $content-color;
    outline: none;
    background: $dropdown-list-bg-color;
    border-color: $container-border-color;
    border-width: 0;
    border-radius: 0.25rem;
    transition: all 0.3s ease;

    &::placeholder {
      color: color.adjust($content-color, $lightness: 20%);
    }
  }

  & > li {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding-top: 0.25em;
    padding-bottom: 0.25em;
    margin: 0.1em 0.5em;
    color: $content-color;
    cursor: pointer;
    user-select: none;
    list-style-type: none;
    border-radius: 0.25em;
    transition: all 0.3s ease;

    & > * {
      padding-left: 0.4rem;
    }

    &:hover,
    &.selected {
      color: $content-color-dark;
      background: $list-level1-selected-color;
    }

    & .item-padding {
      flex-grow: 10;
    }

    & p {
      max-height: 1em;
      margin: 0;
    }

    & > .dropdown-list {
      padding-left: 0;
    }

    &.dropdown-active {
      & > .dropdown-list {
        pointer-events: all;
        opacity: 1;
        transform: translateY(2.5em);
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
</style>
