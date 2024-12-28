import {createApp} from 'vue'
import axios from 'axios'

import App from './App.vue'

const app = createApp(App)

axios.get(`/config.json?version=${new Date().getTime()}`)
  .then(response => {
    const config = response.data
    app.config.globalProperties.$apiBase = config.apiBase
    axios.defaults.baseURL = config.apiBase
    console.log(config.apiKey)
    axios.defaults.headers.common['Authorization'] = config.apiKey
    app.mount('#app')
  })
  .catch(error => {
    console.error('Failed to load config.json:', error)
})
