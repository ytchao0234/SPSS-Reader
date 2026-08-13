<template>
  <div class="grid_selector">
    <v-container :class="grid_selector_class">
      <div class="d-flex align-start justify-space-between">
        <p
          :class="disabled ? 'mt-0 half-opacity' : 'mt-0'" 
          style="font-size: 12px; color: #dddddd;"
        >
          {{ title }}
        </p>

        <IconTooltip
          type="close"
          location="top"
          hint_message="Clear Selection"
          density="default"
          is-button
          :on-btn-click="onClear"
        />
      </div>

      <v-row gap="16" class="justify-start">
        <v-col
          v-for="item in items"
          :key="item"
          cols="auto"
        >
          <v-sheet
            :class="getGridClass(item)"
            color="grey-darken-2"
            style="font-size: 14px;"
            @click="onGridClicked(item)"
          >
            {{ item }}
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'

const props = defineProps({
  title: {
    type: String,
    default: "Options (Multi-select)",
  },
  disabled: {
    type: Boolean,
    default: false
  },
  valid: {
    type: Boolean,
    default: true
  },
  items: {
    type: Array,
    default: () => []
  },
  gridSelected: {
    type: Array,
    default: () => []
  },
  multiple: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'update:grid-selected'
])

function onGridClicked(item) {
  let selected = new Set(props.gridSelected)

  if (selected.has(item)) {
    selected.delete(item)
  }
  else {
    if (props.multiple) {
      selected.add(item)
    }
    else {
      selected = new Set([item])
    }
  }

  emit('update:grid-selected', Array.from(selected))
}

const grid_selector_class = computed(() => {
  if (props.valid) {
    return 'grid-selector overflow-y-auto'
  }
  else {
    return 'grid-selector-alert overflow-y-auto'
  }
})

function getGridClass(item) {
  let class_str = 'pa-2 selectable border rounded-lg'

  if (props.disabled) {
    class_str += ' half-opacity'
  }
  if (props.gridSelected.includes(item)) {
    class_str += ' grid-selected'
  }
  return class_str
}

function onClear() {
  if (props.gridSelected.length > 0) {
    emit('update:grid-selected', [])
  }
}
</script>