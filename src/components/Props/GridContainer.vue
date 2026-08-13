<template>
  <div class="grid_container">
    <v-container>
      <v-row gap="4" class="justify-start">
        <v-col
          v-for="(item, index) in items"
          :key="item"
          cols="auto"
        >
          <v-sheet
            :class="getGridClass(item, index)"
            color="grey-darken-2"
            style="font-size: 14px;"
          >
            {{ item }}
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  index: {
    type: Number,
    default: -1
  },
  items: {
    type: Array,
    default: () => []
  },
  sourceItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'update-passed'
])

const passed = computed(() => {
  return props.items.every(item => props.sourceItems.includes(item))
})

function getGridClass(item, index) {
  let class_str = 'pa-2 border rounded-lg'

  if (props.sourceItems.includes(item)) {
    class_str += ' grid-success'
  }
  else {
    class_str += ' grid-error'
  }

  emit('update-passed', {
    index: props.index,
    value: passed.value
  })

  return class_str
}
</script>