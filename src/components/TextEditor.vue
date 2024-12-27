<template>
  <transition name="zoom-fade">
    <div v-show="isEditorVisible" class="modal-overlay" @click.self="closeEditor">
      <div class="modal-content">
        <MdEditor v-model="text"/>
      </div>
    </div>
  </transition>
</template>

<script lang="ts">
import { ref, watch, defineComponent} from 'vue'
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';

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
    const text = ref("")
    watch(() => props.editingText, (newValue: string, oldValue: string) => {
      console.log(`outter changed from ${oldValue} to ${newValue}`);
      text.value = newValue
    });
    watch(text, (newValue: string, oldValue: string) => {
      console.log(`inner changed from ${oldValue} to ${newValue}`);
      emit('updateText', text.value)
    });
    return {
      text: text
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
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
}
</style>