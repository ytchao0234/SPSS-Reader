<template>
  <div class="delete_button">
    <v-dialog
      v-model="dialog"
      max-width="400"
      persistent
      @keydown.backspace.prevent="onCancel"
      @keydown.enter.prevent="confirmDelete"
    >
      <template v-slot:activator="{ props: props }">
        <v-btn
          v-if="icon"
          icon
          v-bind="props"
          color="red"
          variant="text"
          :disabled="disabled"
          size="x-small"
          :ripple="false"
          @click="onOpenDialog"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          <v-icon>
            mdi-delete
          </v-icon>
        </v-btn>

        <v-btn
          v-else
          v-bind="props"
          color="red"
          :disabled="disabled"
          @click="onOpenDialog"
        >
          Delete
        </v-btn>
      </template>

      <v-card
        prepend-icon="mdi-alert"
        title="Confirm deletion"
        :class="alertMsg ? 'text-warning' : ''"
        :text="alertMsg ? alertMsg : defaultAlertMsg"
        color="grey-darken-3"
      >

        <template v-slot:actions>
          <v-spacer></v-spacer>

          <v-btn 
            color="grey-lighten-1" 
            @click="onCancel"
          >
            Cancel
          </v-btn>

          <v-btn 
            color="red" 
            @click="confirmDelete"
          >
            Delete
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
  id: {
    type: Number,
    default: -1
  },
  icon: {
    type: Boolean,
    default: false
  },
  alertMsg: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'update-alert-msg',
  'delete',
  'single-delete'
])

const dialog = ref(false)
const defaultAlertMsg = 'Are you sure you want to delete the selected items? This action cannot be undone.'

function onOpenDialog() {
  utility.is_dialog_opened = true
  emit('update-alert-msg')
}

function onCancel() {
  dialog.value = false
  utility.is_dialog_opened = false
}

function confirmDelete() {
  if (props.id > 0) {
    emit('single-delete', props.id)
  }
  else {
    emit('delete')
  }
  dialog.value = false

  setTimeout(() => {
    utility.is_dialog_opened = false
  }, 0)
}
</script>