<template>
  <div class="factor_table">
    <v-data-table-virtual
      :headers="headers"
      :items="items"
      density="compact"
      hide-default-footer
    >
      <template #headers="{ columns }">
        <tr class="bg-grey-darken-3">
          <th
            v-for="column in columns"
            :key="column.key"
            :style="{ width: column.width }"
          >
            {{ column.title }}
          </th>
        </tr>
      </template>
    </v-data-table-virtual>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

const props = defineProps({
  type: {
    type: String,
    default: 'between',
    required: true
  },
  items: {
    type: Array,
    default: () => [],
    required: true
  },
})

const headers = computed(() => {
  switch (props.type) {
    case 'between':
      return utility.bs_headers
    case 'within':
      return utility.ws_headers
    default:
      return utility.bs_headers
  }
})
</script>