<template>
  <LoadingOverlay ref="loading" @loadingIn="loadingOut"/>
  <router-view/>
</template>

<script lang="ts">
import {ref, defineComponent} from 'vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

export default defineComponent({
  components: {
    LoadingOverlay
  },
  methods: {
    loadingOut() {
      const timer = setInterval(() => {
        if(document.readyState === 'complete') {
          clearInterval(timer)
          this.loading?.out()
        }
      }, 256)
    }
  },
  mounted() {
    this.loadingOut()
    this.$router.beforeEach(async (_to, _from, next) => {
      await this.loading?.in()
      next()
    })
  },
  setup() {
    const loading = ref<typeof LoadingOverlay>()
    return {loading}
  }
})
</script>