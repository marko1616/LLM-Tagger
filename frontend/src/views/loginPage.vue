<template>
  <div class="fill-area"><div class="login-container" ref="loginContainerRef">
    <h1 class="title">Login</h1>
    <form class="login-main">
      <input class="input" placeholder="Authkey" type="password" ref="authkeyRef"/>
      <div class="remember-container">
        <input class="remember" type="checkbox" ref="rememberRef"/>
        <label class="remember-label">Remember me for 7 days</label>
      </div>
      <div class="button-container">
        <div class="button" @click="doLogin">Login</div>
      </div>
    </form>
  </div></div>
</template>

<script lang="ts">
import { ref, defineComponent } from 'vue'
import { AxiosError } from 'axios';
import Cookies from 'js-cookie'
import axios from 'axios'
import router from '@/router';

export default defineComponent({
  methods: {
    async doLogin() {
      axios.defaults.headers.common['Authorization'] = (this.authkeyRef as HTMLInputElement).value
      try {
        const _response = await axios.get('/datasets/list')
        if(this.rememberRef?.checked) {
          Cookies.set('authkey', (this.authkeyRef as HTMLInputElement).value, { expires: 7 })
        }
        router.push('/')
      } catch (error) {
        if(error instanceof AxiosError) {
          if(error.response?.status === 401) {
            this.loginContainerRef?.classList.add('shake-animation');
            this.loginContainerRef?.addEventListener('animationend', () => {
              this.loginContainerRef?.classList.remove('shake-animation');
            }, { once: true });
          }
        } else {
          throw error
        }
      }
    }
  },
  setup() {
    const authkeyRef = ref<HTMLInputElement | null>(null)
    const rememberRef = ref<HTMLInputElement | null>(null)
    const loginContainerRef = ref<HTMLFormElement | null>(null)

    return { authkeyRef, rememberRef, loginContainerRef }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;

.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: $container-bg-color;
  border-radius: 2em;
  border: 0.4em solid $container-border-color;
  height: 50%;
  width: 30%;
  min-width: min-content;
}

.title {
  padding: 1em;
  color: $content-color;
}

.login-main {
  display: flex;
  justify-content: center;
  align-items: left;
  flex-direction: column;
  flex-grow: 1;
}

.input {
  background: $main-bg-color;
  color: $content-color;
  outline: none;
  font-size: xx-large;
  padding-top: 0.25em;
  padding-bottom: 0.25em;
  border-radius: 0.25em;
  margin: 0.5em 0.5em 0.5em 0.5em;
  padding-left: 1em;
  padding-right: 1em;
  border: 0.1em solid $container-border-color;
  border-radius: 0.25em;

  transition: all 0.3s ease;

  &::placeholder {
    color: lighten($content-color, 20%);
  }
}

.remember-container {
  padding-left: 0.75em;
}

.remember {
  margin-right: 0.5em;
}

.remember-label {
  user-select: none;
  color: $content-color;
}

.button-container {
  display: flex;
  justify-content: center;

  margin-top: 10%;
}

.button {
  user-select: none;
  display: flex;
  justify-content: center;
  align-items: center;
  color: $button-color;
  background-color: $button-bg-color;
  font-size: xx-large;

  border-radius: 0.5em;
  height: 1.75em;
  width: 10em;

  transition: all 0.3s ease;

  &:hover {
    background-color: $button-hover-bg-color;
  }

  &:active {
    transform: scale(0.95);
  }
}

.fill-area {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: $main-bg-color;
  height: 100%;
  width: 100%;
}

.shake-animation {
  animation: shake 0.2s ease-in-out 2;
}

@keyframes shake {
  0% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-1em);
  }
  75% {
    transform: translateX(1em);
  }
  100% {
    transform: translateX(0);
  }
}
</style>

<style lang="scss">
html, body {
  display: flex;

  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

#app {
  display: flex;
  font-family: Consolas, "Courier New", "Microsoft YaHei", "Noto Sans CJK", monospace;
  height: 100vh;
  width: 100vw;
}
</style>
