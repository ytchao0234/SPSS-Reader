<template>
  <div class="delete_button">
    <v-dialog
      v-model="dialog"
      max-width="400"
      persistent
      @keydown.backspace="onPressBackspace"
      @keydown.enter.prevent="onApply"
    >
      <template v-slot:activator="{ props: props }">
        <v-btn
          icon
          v-bind="props"
          color="orange"
          variant="text"
          :disabled="disabled"
          size="x-small"
          :ripple="false"
          @click="onOpenDialog"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          <v-icon>
            mdi-pencil
          </v-icon>
        </v-btn>
      </template>

      <v-card
        :title="title"
        color="grey-darken-3"
      >
        <v-card-subtitle>
          <v-text-field 
            v-model="text" 
            :label="label"
            style="--v-field-input-font-size: 16px;" 
            autofocus
          />
        </v-card-subtitle>

        <template v-slot:actions>
          <v-btn 
            color="grey-lighten-1" 
            @click="onCancel"
          >
            Cancel
          </v-btn>

          <v-btn 
            color="primary" 
            @click="onApply"
          >
            Apply
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

const props = defineProps({
  title: {
    type: String,
    default: "Edit Text"
  },
  label: {
    type: String,
    default: "Edit Text"
  },
  srcText: {
    type: String,
    default: ""
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'update:src-text',
])

const dialog = ref(false)
const text = ref("")

async function onOpenDialog() {
  utility.is_dialog_opened = true
  text.value = props.srcText
}

function onCancel() {
  dialog.value = false
  utility.is_dialog_opened = false
}

function onPressBackspace() {
  if (document.activeElement?.tagName === 'INPUT') {
    return
  }

  onCancel()
}

function onApply() {
  emit('update:src-text', text.value)
  dialog.value = false

  setTimeout(() => {
    utility.is_dialog_opened = false
  }, 0)
}
</script>