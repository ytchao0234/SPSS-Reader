<template>
  <div class="select_button ml-auto d-flex ga-2">
      <v-btn
        v-if="!props.select_mode"
        color="primary"
        @click="enterSelectMode"
        :ripple="false"
        @keydown.enter.prevent="$event.target.blur()"
        @keydown.space.prevent="$event.target.blur()"
      >
        Select
      </v-btn>

      <template v-else>
        <v-btn
          color="grey-darken-3"
          @click="cancelSelect"
          :ripple="false"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          Cancel
        </v-btn>

        <v-btn
          v-if="props.select_all"
          color="primary"
          @click="selectAll"
          :ripple="false"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
        >
          <span v-if="!props.is_all_selected">
            Select All
          </span>

          <span v-else>
            Deselect All
          </span>
        </v-btn>

        <DeleteButton
          :disabled="props.selected.length === 0"
          :alert-msg="alertMsg"
          @update-alert-msg="emit('update-alert-msg')"
          @delete="deleteSelected"
        />
      </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DeleteButton from '@/components/Props/DeleteButton.vue'

const props = defineProps({
  select_all: {
    type: Boolean,
    default: false
  },
  is_all_selected: {
    type: Boolean,
    default: false
  },
  select_mode: {
    type: Boolean,
    default: false
  },
  selected: {
    type: Array,
    default: () => []
  },
  alertMsg: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'update:select_mode',
  'update:selected',
  'enter-select-mode',
  'cancel-select-mode',
  'select-all',
  'delete-selected',
  'update-alert-msg'
])

function enterSelectMode(){
  emit('enter-select-mode')
}

function cancelSelect(){
  emit('cancel-select-mode')
  emit('update:select_mode', false)
  emit('update:selected', [])
}

function selectAll(){
  emit('select-all')
}

function deleteSelected(){
  emit('delete-selected')
}
</script>