<template>
  <div class="edit_factor_group_btn">
    <v-btn
      icon
      size="36"
      color="primary"
      @click="uploadFile"
      :ripple="false"
      @keydown.enter.prevent="$event.target.blur()"
      @keydown.space.prevent="$event.target.blur()"
    >
      <v-icon>
        mdi-plus
      </v-icon>
    </v-btn>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

const props = defineProps({
  type: {
    type: String,
    default: "excel",
    required: true
  },
  table_name: {
    type: String,
    default: ""
  },
  result: {
    type: Object,
    default: () => {}
  }
})

const emit = defineEmits([
  'update:result',
])

async function uploadFile() {
  utility.is_dialog_opened = true

  const filepath = await window.api.selectFile()
  if (!filepath) return // Cancel

  let res

  switch (props.type) {
    case 'excel':
      res = await utility.uploadExcelFile(filepath, props.table_name)
      break
    case 'json':
      res = await utility.readJsonFile(filepath)
      break
    default:
      break
  }

  if (!res) { // Canceled
    utility.is_dialog_opened = false
    return
  }

  emit('update:result', {
    success: res.success,
    valid: res.valid,
    filename: res.filename
  })
  utility.is_dialog_opened = false
}
</script>