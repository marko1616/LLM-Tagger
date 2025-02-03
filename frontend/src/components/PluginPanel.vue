<template>
  <div class="plugin-panel">
    <div class="container-padding"><div class="panel-container">
      <simplebar><ul class="plugin-list" ref="pluginListRef">
        <li v-for="plugin in plugins" :key="plugin.name"
          :plugin-name="plugin.name"
          :class="{ selected: selectedPlugin?.name === plugin.name }"
          @click="selectPlugin(plugin.name)">
          <p @click="plugin.show = !plugin.show">{{ plugin.name }}</p>
          <transition name="parameter-list"><ul class="parameter-list" v-show="plugin.show">
            <li @click="applyPlugin(plugin.name)">
              Apply plugin
            </li>
            <li v-for="param in plugin.params" :key="param.displayName"
            :param-name="param.apiName"
            :class="{ selected: selectedParam?.apiName === param.apiName }"
            @click="selectParam(plugin.name, param.apiName)">
              {{ param.displayName }}
            </li>
          </ul></transition>
        </li>
      </ul></simplebar>
    </div></div>
    <div class="container-padding"><div class="panel-container">
      <transition name="param-panel"><div class="dataset-selector" v-show="selectedParam?.type === 'dataset'">
        <div class="divider">
          <span>Picked dataset</span>
        </div>
        <h1>{{ selectedParam ? getParam(selectedParam.pluginName, selectedParam.apiName)?.data ?? 'Null' : 'Null' }}</h1>
        <div class="button-padding">
          <button @click="pickDataset">Pick selected dataset</button>
        </div>
      </div></transition>
      <transition name="param-panel"><div class="file-selector" v-show="selectedParam?.type === 'file'">
        <input
          ref="fileInputRef"
          type="file"
          style="display: none;"
          @change="handleFileSelect"
        />
        <div class="divider">
          <span>Picked file</span>
        </div>
        <div class="file-zone-padding">
          <div class="file-zone"
          :class="{ 'drag-active': isDragging }"
          @click="triggerFileInput"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          >
            <p ref="fileDropZoneInfoRef">{{ selectedParam ? (getParam(selectedParam.pluginName, selectedParam.apiName)?.data as File | null)?.name ?? 'Select file' : 'Select file' }}</p>
          </div>
        </div>
      </div></transition>
    </div></div>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent } from 'vue';

import axios from 'axios';
import simplebar from 'simplebar-vue';

import { DatasetParam, FileParam, PluginInfo, PluginParam, PluginSummary, PluginParamSummary } from '@/types/plugin';

export default defineComponent({
  components: {
    simplebar
  },
  emits: {
    'getSelectedDataset': (_callback: (datasetName:string) => void) => {
      return true
    },
    'flushDatasets': () => {
      return true
    }
  },
  methods: {
    getPlugin(pluginName: string) {
      return this.plugins.find(plugin => plugin.name === pluginName)
    },
    getParam(pluginName: string, paramName: string) {
      return this.plugins.find(plugin => plugin.name === pluginName)?.params.find(param => param.apiName === paramName)
    },
    selectPlugin(pluginName: string) {
      const plugin = this.getPlugin(pluginName) as PluginInfo
      this.selectedPlugin = {
        name: plugin.name,
        description: plugin.description,
        params: plugin.params,
        url: plugin.url,
        show: false
      }
    },
    selectParam(pluginName: string, paramName: string) {
      if(!this.pluginListRef) {
        return
      }
      const param = this.getParam(pluginName, paramName) as PluginParam

      this.selectedParam = {
        pluginName: pluginName,
        displayName: param.displayName,
        apiName: param.apiName,
        type: param.type
      }
    },
    async applyPlugin(pluginName: string) {
      const plugin = this.getPlugin(pluginName) as PluginInfo
      let params: {[key: string]: DatasetParam | FileParam} = {}
      plugin.params.forEach((param) => {
        if(!param.data) {
          return
        }
        if(param.type === 'dataset') {
          params[param.apiName] = param.data as string
        } else if(param.type === 'file') {
          params[param.apiName] = param.data as File
        }
      })
      await axios.post(plugin.url, params, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      this.$emit('flushDatasets')
    },
    pickDataset() {
      this.$emit('getSelectedDataset', (datasetName: string) => {
        const param = this.getParam(
          this.selectedPlugin?.name ?? '',
          this.selectedParam?.apiName ?? ''
        );
        if (param) {
          param.data = datasetName;
        }
      })
    },
    handleFile(file: File) {
      if(this.selectedParam?.type !== 'file') {
        return
      }

      const param = this.getParam(
        this.selectedPlugin?.name ?? '',
        this.selectedParam?.apiName ?? ''
      );

      if(param) {
        param.data = file
      }
    },
    handleFileSelect(event: Event) {
      const file = (event.target as HTMLInputElement).files?.[0]
      if(file) {
        this.handleFile(file)
      }
    },
    triggerFileInput() {
      this.fileInputRef?.click()
    },
    handleDragOver() {
      this.isDragging = true
    },
    handleDragLeave() {
      this.isDragging = false
    },
    handleDrop(event: DragEvent) {
      this.isDragging = false
      const file = event.dataTransfer?.files[0]
      if (file) {
        this.handleFile(file)
      }
    }
  },
  async mounted() {
    this.plugins.length = 0
    {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (await axios.get('/plugins/list')).data.plugins.forEach((plugin: any) => {
        this.plugins.push({
          description: plugin.description,
          name: plugin.name,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          params: plugin.params.map((param: any) => {
            return {
              displayName: param.display_name,
              apiName: param.api_name,
              type: param.type,
              description: param.description,
              data: null
            }
          }),
          url: plugin.url,
          show: false
        })
      })
    }
  },
  setup() {
    const isDragging = ref(false)
    const pluginListRef = ref<HTMLElement | null>(null)
    const fileInputRef = ref<HTMLInputElement | null>(null)
    const fileDropZoneInfoRef = ref<HTMLElement | null>(null)
    const plugins = ref<PluginSummary[]>([])
    const selectedPlugin = ref<PluginSummary | null>(null)
    const selectedParam = ref<PluginParamSummary | null>(null)
    return { isDragging, pluginListRef, fileInputRef, fileDropZoneInfoRef, plugins, selectedPlugin, selectedParam }
  },
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

p {
  margin: 0;
}

ul {
  padding: 0;
}

.param-panel-enter-from {
  transform: translateY(100%);
}

.param-panel-leave-to {
  transform: translateY(-100%);
}

.param-panel-enter-active,
.param-panel-leave-active {
  transition: all 0.3s ease;
}

.parameter-list-enter-from,
.parameter-list-leave-to {
  max-height: 0;
  opacity: 0;
}

.parameter-list-enter-to,
.parameter-list-leave-from {
  max-height: 100vh;
  opacity: 1;
}

.parameter-list-enter-active,
.parameter-list-leave-active {
  transition: all 0.3s ease;
}

.plugin-panel {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  width: 100%;
  max-height: 50%;
}

.main-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.container-padding {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 50%;
  padding-top: 0.25em;
  padding-bottom: 0.25em;
}

.panel-container {
  position: relative;
  box-sizing: border-box;
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
  border: 0.2em solid $container-border-color;
  border-radius: 1em;
}

.dataset-selector,
.file-selector {
  position: absolute;
  top: 0;
  left: 0;
}

.dataset-selector {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;

  & .divider {
    display: flex;
    justify-content: center;
    height: 15%;

    span {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 0 10px;
      color: $content-color;
      user-select: none;

      &::before,
      &::after {
        position: absolute;
        top: 50%;
        width: 50%;
        content: '';
        border-bottom: 0.1em solid $content-color;
      }

      &::before {
        right: 100%;
      }

      &::after {
        left: 100%;
      }
    }
  }

  & .button-padding {
    display: flex;
    height: 20%;
    padding-top: 5%;
    padding-bottom: 5%;
  }

  & h1 {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 55%;
    margin: 0;
    color: $content-color;
    user-select: none;
  }

  & button {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 20em;
    height: 100%;
    color: $content-color-dark;
    user-select: none;
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

.file-selector {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;

  & .divider {
    display: flex;
    justify-content: center;
    height: 15%;

    span {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 0 10px;
      color: $content-color;
      user-select: none;

      &::before,
      &::after {
        position: absolute;
        top: 50%;
        width: 50%;
        content: '';
        border-bottom: 0.1em solid $content-color;
      }

      &::before {
        right: 100%;
      }

      &::after {
        left: 100%;
      }
    }
  }

  & .file-zone-padding {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 85%;
    height: 85%;
    padding-top: 10%;
    padding-bottom: 10%;
    user-select: none;

    & .file-zone {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      overflow: hidden;
      color: $content-color;
      border: 0.2em dashed $content-color;
      border-radius: 0.25em;

      & p {
        max-width: 100%;
        padding: 1em;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 1em;
        white-space: nowrap;
      }
    }
  }
}

.plugin-list {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  & > * {
    padding-left: 0.4rem;
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

    &:hover,
    &.selected {
      color: $content-color-dark;
      background: $list-level1-selected-color;
    }
  }
}

/**
 * The `not(.plugin-list)` selector is used to prevent potential conflicts
 * and undefined behavior with `.plugin-list`. Although `.plugin-list` and
 * the current context cannot appear simultaneously, this exclusion is
 * necessary to satisfy the linter's requirements and ensure code
 * consistency.
 */
.parameter-list:not(.plugin-list) {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  & > * {
    padding-left: 0.4rem;
  }

  & > li {
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 0.1em 0.5em;
    cursor: pointer;
    user-select: none;
    border-radius: 0.25em;
    transition: all 0.3s ease;

    &:hover,
    &.selected {
      color: $content-color-dark;
      background: $list-level2-selected-color;
    }

    & button {
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 20em;
      height: 100%;
      color: $content-color-dark;
      user-select: none;
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
}
</style>