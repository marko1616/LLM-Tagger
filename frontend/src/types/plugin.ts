type DatasetParam = string

type FileParam = File

type PluginParam = {
  displayName: string
  apiName: string
  type: string
  description: string
  data?: DatasetParam | FileParam | null
}

type PluginInfo = {
  description: string
  name: string
  contentType: string
  params: PluginParam[]
  url: string
}

type PluginParamSummary = {
  pluginName: string
  displayName: string
  apiName: string
  type: string
}

type PluginSummary = {
  description: string
  name: string
  contentType: string
  params: PluginParam[]
  url: string
  show: boolean
}

export { DatasetParam, FileParam, PluginParam, PluginInfo, PluginParamSummary, PluginSummary }