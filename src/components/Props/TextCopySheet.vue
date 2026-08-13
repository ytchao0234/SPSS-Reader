<template>
  <div class="text_copy_sheet">
    <v-sheet 
      v-if="text"
      class="pa-2 rounded-md border"
      :color="color"
    >
      <div class="d-flex align-center justify-space-between" >
        <span>{{ text }}</span>

        <IconTooltip
          :type="copied ? 'check' : 'copy'"
          location="top"
          :hint_message="copied ? 'Copied' : 'Copy'"
          size="20"
          is-button
          :on-btn-click="CopyText"
        />
      </div>
    </v-sheet>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'

const props = defineProps({
  text: {
    type: String,
    default: ""
  },
  color: {
    type: String,
    default: "grey-darken-3"
  }
})

const copied = ref(false)

function CopyText() {
  window.api.copyText(props.text)
  copied.value = true

  setTimeout(() => {
    copied.value = false
  }, 500)
}
</script>