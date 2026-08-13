<template>
  <div class="edit_factor_group_btn">
    <v-dialog
      v-model="dialog"
      max-width="800"
      persistent
    >
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn 
          v-bind="activatorProps"
          icon
          size="x-small"
          variant="text"
          color="orange"
          @click.stop="init"
          :ripple="false"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          <v-icon>
            mdi-pencil
          </v-icon>
        </v-btn>
      </template>

      <v-card
        title="Set Factors"
        color="grey-darken-3"
        class="pa-1 overflow-y-auto"
        height="600"
      >
        <v-card-text class="overflow-y-auto flex-grow-1">
          <FactorsEditor
            ref="factorEditor"
            v-model:bs_items="my_bs_items"
            v-model:ws_items="my_ws_items"
          />
        </v-card-text>

        <template v-slot:actions>
          <v-spacer></v-spacer>

          <v-btn @click="cancelEdit">
            Cancel
          </v-btn>

          <v-btn 
            color="primary" 
            @click="saveFactorGroup"
            :disabled="!factorEditor?.is_valid"
          >
            Save
          </v-btn>
          
          <div v-if="err_msg" class="ml-4">
            <IconTooltip
              type="error"
              location="top"
              :hint_message="err_msg"
            />
          </div>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import FactorsEditor from '@/components/Props/Factor/FactorsEditor.vue'
import IconTooltip from '@/components/Props/IconTooltip.vue'

const props = defineProps({
  id: {
    type: Number,
    required: true
  },
  bs_items: {
    type: Array,
    default: () => []
  },
  ws_items: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'request-refresh',
  'request-expand'
])

const dialog = ref(false)
const factorEditor = ref()
const my_bs_items = ref([])
const my_ws_items = ref([])
const err_msg = ref('')

function init() {
  utility.is_dialog_opened = true

  my_bs_items.value = props.bs_items.map(item => ({ ...item }))
  my_ws_items.value = props.ws_items.map(item => ({ ...item }))
  err_msg.value = ''
}

function cancelEdit() {
  dialog.value = false
  utility.is_dialog_opened = false
  err_msg.value = ''
}

async function saveFactorGroup() {
  const factors = factorEditor.value?.getItems()
  if (!factors) {
    console.error('Failed to get factor items')
    return
  }

  const bsFactorString = Object.entries(
  factors.bs.reduce((count, item) => {
      count[item.factor] = (count[item.factor] || 0) + 1
      return count
    }, {})
  )
  .map(([factor, count]) => `${count}${factor}`)
  .join(' x ')

  const wsFactorString = Object.entries(
  factors.ws.reduce((count, item) => {
      count[item.factor] = (count[item.factor] || 0) + 1
      return count
    }, {})
  )
  .map(([factor, count]) => `${count}${factor}`)
  .join('  x  ')

  const title = [bsFactorString, wsFactorString].filter(Boolean).join(' x ')
  const between_subjects_factors = JSON.stringify(factors.bs)
  const within_subjects_factors = JSON.stringify(factors.ws)

  const success = await window.api.updateFactorGroup(
    title, between_subjects_factors, within_subjects_factors, props.id
  )
  if (!success) {
    err_msg.value = 'Failed to update'
    return
  }

  emit('request-refresh')
  emit('request-expand', props.id)

  dialog.value = false
  utility.is_dialog_opened = false
  err_msg.value = ''
  factorEditor.value?.clearItems()
  factorEditor.value?.updateItems()
}
</script>