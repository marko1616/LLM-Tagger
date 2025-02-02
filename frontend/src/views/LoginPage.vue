<template>
  <div class="fill-area"><div class="login-container" ref="loginContainerRef">
    <h1 class="title">Welcome</h1>
    <form class="login-main">
      <input class="input" placeholder="Authkey" type="password" ref="authkeyRef"/>
      <div class="remember-container">
        <input class="remember" type="checkbox" ref="rememberRef"/>
        <label class="remember-label">Remember me for 7 days</label>
      </div>
      <div class="button-container">
        <button class="button" @click="doLogin">Login</button>
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
  mounted() {
    this.enterHandler = (event) => {
      if (event.key === 'Enter') {
        this.doLogin()
        event.preventDefault()
        event.stopPropagation()
      }
    }
    window.addEventListener('keypress', this.enterHandler)
  },
  unmounted() {
    window.removeEventListener('keypress', this.enterHandler)
  },
  setup() {
    const authkeyRef = ref<HTMLInputElement | null>(null)
    const rememberRef = ref<HTMLInputElement | null>(null)
    const loginContainerRef = ref<HTMLFormElement | null>(null)
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    const enterHandler = (_event: KeyboardEvent) => {}

    return { authkeyRef, rememberRef, loginContainerRef, enterHandler }
  }
})
</script>

<style lang="scss" scoped>
@use "@/styles/color.scss" as *;
@use "sass:color";

.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
  width: 30%;
  min-width: min-content;
  height: 50%;
  background-color: $container-bg-color;
  border: 0.4em solid $container-border-color;
  border-radius: 2em;
}

.title {
  padding: 1em;
  font-size: 3rem;
  font-weight: 900;
  color: $content-color;
}

.login-main {
  display: flex;
  flex-direction: column;
  align-items: left;
  justify-content: center;
  padding-bottom: 1em;
}

.input {
  padding: 0.25em 1em;
  margin: 0.5em;
  font-size: 2em;
  color: $content-color;
  outline: none;
  background: $main-bg-color;
  border: 0.1em solid $container-border-color;
  border-radius: 0.25em;
  transition: all 0.3s ease;

  &::placeholder {
    color: color.adjust($content-color, $lightness: 20%);
  }
}

.remember-container {
  padding-left: 0.75em;
}

.remember {
  margin-right: 0.5em;
}

.remember-label {
  color: $content-color;
  user-select: none;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 10%;
}

button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 10em;
  height: 1.75em;
  font-size: 2em;
  color: $button-color;
  user-select: none;
  background-color: $button-bg-color;
  border: 0;
  border-radius: 0.5em;
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
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: $main-bg-color;
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
  width: 100vw;
  height: 100vh;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

#app {
  display: flex;
  width: 100vw;
  height: 100vh;
  font-family: Consolas, "Courier New", "Microsoft YaHei", "Noto Sans CJK", monospace;
}
</style>
