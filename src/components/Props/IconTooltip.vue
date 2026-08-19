<template>
  <div class="icon_tooltip">
    <v-tooltip
      :disabled="!props.hint_message"
      :location="props.location"
      :color="tooltip_color"
      :width="props.width ?? ''"
      :open-on-focus="false"
    >
      <template #activator="{ props }">
        <v-btn
          v-bind="{
            ...props,
            ...dialogProps,
            onClick: (e) => {
              e.stopPropagation()
              onBtnClick?.(e) 
              dialogProps?.onClick?.(e)
            }
          }"
          icon
          variant="text"
          size="x-small"
          :class="[{ 'no-pointer': !isButton }, 'keep-color']"
          :loading="is_loading"
          :disabled="is_loading"
          :density="density"
          :color="icon_color"
          :ripple="false"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          <v-icon :size="size">
            {{ icon }}
          </v-icon>
        </v-btn>
      </template>

      <div class="text-pre-wrap mono">
        {{ props.hint_message }}
      </div>
    </v-tooltip>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: "info"
  },
  size: {
    type: String,
    default: "24"
  },
  location: {
    type: String,
    default: "bottom"
  },
  hint_message: {
    type: String,
    default: ""
  },
  width: {
    type: String,
    default: ""
  },
  bgColor: {
    type: String,
    default: ""
  },
  density: {
    type: String,
    default: 'compact',
  },
  is_loading: {
    type: Boolean,
    default: false
  },
  isButton: {
    type: Boolean,
    default: false
  },
  onBtnClick: {
    type: Function,
    default: () => {}
  },
  dialogProps: {
    type: Object,
    default: null
  }
})

const icon = computed(() => {
  switch (props.type) {
    case 'info':
      return 'mdi-information-outline'
    case 'warning':
      return 'mdi-alert-outline'
    case 'error':
      return 'mdi-close-circle-outline'
    case 'success':
      return 'mdi-check-circle-outline'
    case 'file_export':
      return 'mdi-file-export'
    case 'read_file':
      return 'mdi-file-eye'
    case 'close':
      return 'mdi-close'
    case 'copy':
      return 'mdi-content-copy'
    case 'check':
      return 'mdi-check'
    default:
      return 'mdi-help-circle-outline'
  }
})

const icon_color = computed(() => {
  switch (props.type) {
    case 'info':
      return 'white'
    case 'warning':
      return 'warning'
    case 'error':
      return 'error'
    case 'success':
      return 'success'
    case 'file_export':
      return 'success'
    case 'read_file':
      return 'info'
    case 'close':
      return 'grey'
    case 'copy':
      return 'grey'
    case 'check':
      return 'success'
    default:
      return 'white'
  }
})

const tooltip_color = computed(() => {
  if (props.bgColor) {
    return props.bgColor
  }

  switch (props.type) {
    case 'info':
      return 'grey-darken-3'
    case 'warning':
      return 'warning'
    case 'error':
      return 'error'
    case 'success':
      return 'success'
    case 'file_export':
      return 'success'
    case 'read_file':
      return 'info'
    case 'close':
      return 'grey-darken-2'
    case 'copy':
      return 'grey-darken-2'
    case 'check':
      return 'success'
    default:
      return 'grey-darken-3'
  }
})
</script>