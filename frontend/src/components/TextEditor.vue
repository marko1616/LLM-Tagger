<template>
  <transition name="zoom-fade">
    <div v-show="isEditorVisible" class="modal-overlay" @click.self="closeEditor">
      <div class="modal-content">
        <MdEditor v-model="text" @onUploadImg="onUploadImg"/>
      </div>
    </div>
  </transition>
</template>

<script lang="ts">
import { ref, watch, defineComponent} from 'vue'
import { MdEditor } from 'md-editor-v3'
import axios from 'axios';
import 'md-editor-v3/lib/style.css'

type UploadImgCallback = (urls: string[]) => void

export default defineComponent({
  props: {
    isEditorVisible: {
      type: Boolean,
      required: true
    },
    editingText: {
      type: String,
      required: true
    }
  },
  emits: ['close', 'updateText'],
  methods: {
    closeEditor() {
      this.$emit('close')
    }
  },
  components: {
    MdEditor
  },
  setup(props, { emit }) {
    const text = ref('')
    const onUploadImg = async (files: File[], callback: UploadImgCallback) => {
      const res = await Promise.all(
        files.map((file) => {
          return new Promise<{ data: { url: string } }>((resolve, reject) => {
            const form = new FormData()
            form.append('file', file)
            axios
              .post('/api/img/uploads', form, {
                headers: {
                  'Content-Type': 'multipart/form-data',
                },
              })
              .then((response) => resolve(response))
              .catch((error) => reject(error))
          })
        })
      )
      callback(res.map((item) => item.data.url))
    }

    watch(() => props.editingText, (newValue: string, oldValue: string) => {
      text.value = newValue
    })
    watch(text, (newValue: string, oldValue: string) => {
      emit('updateText', text.value)
    })
    return {
      text,
      onUploadImg
    }
  }
})
</script>

<style scoped>
.zoom-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  & .modal-content {
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
  }
}

.zoom-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.65, 0, 0.35, 1);
  & .modal-content {
    transition: all 0.4s cubic-bezier(0.75, 0, 0.25, 1);
  }
}

.zoom-fade-enter-from,
.zoom-fade-leave-to {
  opacity: 0;
  & .modal-content {
    transform: scale(0);
  }
}

.zoom-fade-enter-to,
.zoom-fade-leave-from {
  opacity: 1;
  & .modal-content {
    transform: scale(1);
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  max-width: 95vw;
  min-width: 75vw;
  max-height: 95vh;
  overflow: auto;
}
</style>

<style>
.md-editor {
  min-height: 75vh;
}
</style>