<template>
  <div class="export_significant_result_button">
    <IconTooltip
      :is_loading="is_loading"
      type="file_export"
      hint_message="Export Significant Results Report"
      density="default"
      is-button
      :on-btn-click="onClick"
    />

    <v-overlay
      :model-value="is_loading"
      persistent
    >
    </v-overlay>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'

const props = defineProps({
  projectId: {
    type: Number,
    required: true
  },
  spss_export_filepath: {
    type: String,
    required: true
  },
  method_dict: {
    type: Object,
    required: true
  }
})

const emit = defineEmits([
  'on-exported'
])

const is_loading = ref(false)

onMounted(() => {
  is_loading.value = false
})

async function onClick() {
  is_loading.value = true
  utility.is_dialog_opened = true

  await window.api.runPython(
    'get-sig-result-table',
    props.spss_export_filepath,
    JSON.stringify(props.method_dict),
  )
  .then(async res => {
    await utility.exportSignificantResult()
    utility.is_dialog_opened = false
    await window.api.updateProjectLastUsedTimeById(props.projectId)
    is_loading.value = false
    emit('on-exported')
  })
  .catch(err => {
    console.log('ERROR:', err)
    is_loading.value = false
    utility.is_dialog_opened = false
  })
}
</script>