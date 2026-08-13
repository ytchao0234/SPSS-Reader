<template>
  <div class="add_factor_group_btn">
    <v-dialog
      v-model="dialog"
      max-width="800"
      persistent
    >
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn 
          v-bind="activatorProps"
          icon
          size="36"
          color="primary"
          :ripple="false"
          @click="onOpenDialog"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          <v-icon>
              mdi-pencil-plus
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
            v-model:bs_items="bs_items"
            v-model:ws_items="ws_items"
          />
        </v-card-text>

        <template v-slot:actions>
          <v-spacer></v-spacer>

          <v-btn @click="onCancel">
            Cancel
          </v-btn>

          <v-btn 
            color="primary" 
            @click="saveFactorGroup"
            :disabled="!factorEditor?.is_valid"
          >
            Save
          </v-btn>
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

const emit = defineEmits([
  'request-refresh'
])

const dialog = ref(false)
const factorEditor = ref()
const bs_items = ref([])
const ws_items = ref([])

function onOpenDialog() {
  utility.is_dialog_opened = true
}

function onCancel() {
  dialog.value = false
  utility.is_dialog_opened = false
}

async function saveFactorGroup() {
  const factors = factorEditor.value?.getItems()
  if (!factors) {
    console.error('Failed to get factor items')
    return
  }

  await utility.saveFactorGroup(factors.bs, factors.ws)

  emit('request-refresh')
  dialog.value = false
  utility.is_dialog_opened = false
  factorEditor.value?.clearItems()
  factorEditor.value?.updateItems()
}
</script>