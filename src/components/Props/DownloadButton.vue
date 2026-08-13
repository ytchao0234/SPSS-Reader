<template>
  <div class="download_button">
    <v-btn 
      :loading="is_loading"
      :disabled="is_loading"
      class="keep-color"
      icon 
      variant="text" 
      color="secondary"
      size="x-small"
      @click.stop="onClick"
      :ripple="false"
      @keydown.enter.prevent="$event.target.blur()"
      @keydown.space.prevent="$event.target.blur()"
    >
        <v-icon>
          mdi-download
        </v-icon>
    </v-btn>

    <v-overlay
      :model-value="is_loading"
      persistent
    >
    </v-overlay>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

const props = defineProps({
  args: {
    type: Array,
    required: true
  },
  download: {
    type: Function,
    required: true
  },
})

const is_loading = ref(false)

async function onClick() {
  utility.is_dialog_opened = true
  is_loading.value = true

  await props.download(...props.args)

  utility.is_dialog_opened = false
  is_loading.value = false
}
</script>