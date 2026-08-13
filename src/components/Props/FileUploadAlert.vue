<template>
  <div class="file_upload_alert floating-alert">
    <v-alert
      v-if="show_success"
      type="success"
      theme="dark"
      closable
      @click:close="closeSuccess"
    >
      <div>{{ success_message }}</div>

      <ul v-if="type === 'multiple'" class="mt-2">
        <li v-for="file in valid_files" :key="file">
          {{ file }}
        </li>
      </ul>
    </v-alert>

    <v-alert
      v-if="show_warning"
      type="warning"
      theme="dark"
      closable
      @click:close="closeWarning"
    >
      <div>{{ warning_message }}</div>

      <ul v-if="type === 'multiple'" class="mt-2">
        <li v-for="file in not_valid_files" :key="file">
          {{ file }}
        </li>
      </ul>
    </v-alert>

    <v-alert
      v-if="show_error"
      type="error"
      theme="dark"
      closable
      @click:close="closeError"
    >
      <div>{{ error_message }}</div>

      <ul v-if="type === 'multiple'" class="mt-2">
        <li v-for="file in failed_files" :key="file">
          {{ file }}
        </li>
      </ul>
    </v-alert>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

defineProps({
  type: {
    type: String,
    default: 'multiple'
  },
  show_success: {
    type: Boolean,
    default: false
  },
  show_warning: {
    type: Boolean,
    default: false
  },
  show_error: {
    type: Boolean,
    default: false
  },
  success_message: {
    type: String,
    requried: true
  },
  warning_message: {
    type: String,
    requried: true
  },
  error_message: {
    type: String,
    requried: true
  },
  valid_files: {
    type: Array,
    default: []
  },
  not_valid_files: {
    type: Array,
    default: []
  },
  failed_files: {
    type: Array,
    default: []
  },
})

const emit = defineEmits([
  'update:show_success',
  'update:show_warning',
  'update:show_error'
])

function closeSuccess() {
  emit('update:show_success', false)
}

function closeWarning() {
  emit('update:show_warning', false)
}

function closeError() {
  emit('update:show_error', false)
}
</script>