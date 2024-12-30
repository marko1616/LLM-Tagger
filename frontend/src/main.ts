import {createApp} from 'vue'
import axios from 'axios'

import App from './App.vue'

const app = createApp(App)

axios.get(`/config.json?version=${new Date().getTime()}`)
  .then(response => {
    const config = response.data
    app.config.globalProperties.$api_base = config.api_base
    axios.defaults.baseURL = config.api_base
    axios.defaults.headers.common['Authorization'] = config.api_token
    app.mount('#app')
  })
  .catch(error => {
    console.error('Failed to load config.json:', error)
})
