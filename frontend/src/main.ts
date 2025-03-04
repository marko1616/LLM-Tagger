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
router.isReady().then(() => {
  // The code inside this block will run after the router is fully loaded and initialized

  // Why do we need router.isReady()?
  // 1. Ensures all asynchronous routes (e.g., components loaded dynamically via import()) are fully loaded.
  // 2. Avoids executing the initial navigation from `/` to the route manually typed by the user before the router is ready.
  app.mount('#app')
})

axios.get('/config.json')
  .then(response => {
    const config = response.data
    app.config.globalProperties.$api_base = config.api_base
    axios.defaults.baseURL = config.api_base
  })
  .catch(error => {
    console.error('Failed to load config.json:', error)
})
