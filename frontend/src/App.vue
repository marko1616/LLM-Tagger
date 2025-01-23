<template>
  <LoadingOverlay ref="loading" @loadingIn="loadingOut"/>
  <router-view/>
</template>

<script lang="ts">
import {ref, defineComponent} from 'vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { editingState } from './components/NodeEditorStore';

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
    window.addEventListener('beforeunload', function (event) {
      console.log(editingState.saved)
      if(editingState.saved === false) {
        event.preventDefault()
      }
    })
  },
  setup() {
    const loading = ref<typeof LoadingOverlay>()
    return {loading}
  }
})
</script>