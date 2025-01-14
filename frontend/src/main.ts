import {createApp} from 'vue'

import axios from 'axios'
import Cookies from 'js-cookie'
import router from '@/router'
import App from '@/App.vue'

const app = createApp(App).use(router)
const savedKey = Cookies.get("authkey")
if (savedKey) {
  axios.defaults.headers.common['Authorization'] = savedKey
}
app.mount('#app')

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response.status === 401) {
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

axios.get(`/config.json?version=${new Date().getTime()}`)
  .then(response => {
    const config = response.data
    app.config.globalProperties.$api_base = config.api_base
    axios.defaults.baseURL = config.api_base
  })
  .catch(error => {
    console.error('Failed to load config.json:', error)
})
