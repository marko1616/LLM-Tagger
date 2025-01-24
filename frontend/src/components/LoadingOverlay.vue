<template>
  <div class="loading-container">
    <div class="loading-overlay1" ref="loadingOverlayRef1"/>
    <div class="loading-overlay2" ref="loadingOverlayRef2"/>
    <div class="loading-overlay3" ref="loadingOverlayRef3"/>
    <div class="loading-main" ref="loadingMainRef">
      <div class="loading-content">
        <h1 class="loading-text">
          Loading...
        </h1>
        <svg class="loading-circle" viewBox="0 0 100 100">
          <path
            class="circle-path"
            d="M 50,10 A 40,40 0 1,1 50,90 A 40,40 0 1,1 50,10"
            fill="none"
            stroke-width="10"
            stroke-linecap="round"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent } from 'vue'

enum LoadingStage {
  Idle = 0,
  In = 1,
  Loading = 2,
  Out = 3
}

export default defineComponent({
  name: 'LoadingOverlay',
  emits: ['loadingIn'],
  methods: {
    async out() {
      this.loadingStage = LoadingStage.Out
      await this.addClassWithDelay(this.loadingMainRef as HTMLElement, 'slide-out', 64)
      await this.addClassWithDelay(this.loadingOverlayRef1 as HTMLElement, 'slide-out', 64)
      await this.addClassWithDelay(this.loadingOverlayRef2 as HTMLElement, 'slide-out', 64)
      await this.addClassWithDelay(this.loadingOverlayRef3 as HTMLElement, 'slide-out', 1000)
      // Same delay as the out animation.
      await this.removeClassWithOpacity(this.loadingMainRef as HTMLElement, 'slide-out', 0)
      await this.removeClassWithOpacity(this.loadingOverlayRef1 as HTMLElement, 'slide-out', 0)
      await this.removeClassWithOpacity(this.loadingOverlayRef2 as HTMLElement, 'slide-out', 0)
      await this.removeClassWithOpacity(this.loadingOverlayRef3 as HTMLElement, 'slide-out', 0)
      this.loadingStage = LoadingStage.Idle
    },
    async in() {
      while (this.loadingStage !== LoadingStage.Idle) {
        if(this.loadingStage === LoadingStage.In || this.loadingStage === LoadingStage.Loading) {
          // Skip loading in if already in.
          return
        }
        await this.delay(64)
      }
      this.loadingStage = LoadingStage.In
      await this.addClassWithDelay(this.loadingOverlayRef3 as HTMLElement, 'slide-in', 64)
      await this.addClassWithDelay(this.loadingOverlayRef2 as HTMLElement, 'slide-in', 64)
      await this.addClassWithDelay(this.loadingOverlayRef1 as HTMLElement, 'slide-in', 64)
      await this.addClassWithDelay(this.loadingMainRef as HTMLElement, 'slide-in', 1000)
      await this.removeClassWithOpacity(this.loadingOverlayRef3 as HTMLElement, 'slide-in', 1)
      await this.removeClassWithOpacity(this.loadingOverlayRef2 as HTMLElement, 'slide-in', 1)
      await this.removeClassWithOpacity(this.loadingOverlayRef1 as HTMLElement, 'slide-in', 1)
      await this.removeClassWithOpacity(this.loadingMainRef as HTMLElement, 'slide-in', 1)
      this.loadingStage = LoadingStage.Loading
      this.$emit("loadingIn")
    },
    delay(ms: number) {
      return new Promise((resolve) => setTimeout(resolve, ms))
    },
    async addClassWithDelay(elementRef: HTMLElement, className: string, ms: number) {
      elementRef.classList.add(className)
      elementRef.style.opacity = '1'
      await this.delay(ms)
    },
    async removeClassWithOpacity(elementRef: HTMLElement, className: string, opacity: number) {
      elementRef.classList.remove(className)
      elementRef.style.opacity = opacity.toString()
    }
  },
  setup() {
    const loadingOverlayRef1 = ref<HTMLElement | null>(null)
    const loadingOverlayRef2 = ref<HTMLElement | null>(null)
    const loadingOverlayRef3 = ref<HTMLElement | null>(null)
    const loadingMainRef = ref<HTMLElement | null>(null)
    const loadingStage = LoadingStage.Idle

    return {
      loadingOverlayRef1,
      loadingOverlayRef2,
      loadingOverlayRef3,
      loadingMainRef,
      loadingStage
    }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

.loading-container {
  pointer-events: none;
}

.loading-main {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1024;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  background-color: $main-bg-color;
  animation: loading-out 1s ease-in-out forwards;
}

.loading-overlay1,
.loading-overlay2,
.loading-overlay3 {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
}

.loading-overlay1 {
  z-index: 512;
  background-color: $loading-overlay1-color;
}

.loading-overlay2 {
  z-index: 256;
  background-color: $loading-overlay2-color;
}

.loading-overlay3 {
  z-index: 128;
  background-color: $loading-overlay3-color;
}

.loading-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.loading-text {
  font-size: 1.5em;
  color: $loading-loader-color;
}

.loading-circle {
  width: 100px;
  height: 100px;
  stroke: $loading-loader-color;
  animation: rotate 2s linear infinite;
}

.circle-path {
  stroke-dasharray: 250;
  stroke-dashoffset: 250;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
    0% {
        stroke-dashoffset: 250;
    }

    50% {
        stroke-dashoffset: 0;
    }

    100% {
        stroke-dashoffset: 250;
    }
}

.slide-out {
  animation: slide-out 1s forwards;
}

@keyframes slide-out {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(100%);
  }
}

.slide-in {
  animation: slide-in 1s forwards;
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
  }

  to {
    transform: translateX(0);
  }
}
</style>