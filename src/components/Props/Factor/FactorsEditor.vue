<template>
  <div class="d-flex align-start">
    <v-data-table-virtual
      :headers="utility.bs_headers"
      :items="my_bs_items"
      style="background-color: transparent;"
      hide-default-footer
    >
      <template #item.factor="{ item }">
        <v-text-field
          v-model="item.factor"
          name="quantity"
          density="compact"
          hide-details
        />
      </template>

      <template #item.condition="{ item }">
        <v-text-field
          v-model="item.condition"
          name="quantity"
          density="compact"
          hide-details
        />
      </template>
    </v-data-table-virtual>

    <div class="ml-auto mt-auto d-flex ga-2 mb-2">
      <v-btn
          icon="mdi-plus"
          size="x-small"
          color="primary"
          @click="addBSFactor"
          :ripple="false"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
      />
      <v-btn
          icon="mdi-minus"
          size="x-small"
          color="red"
          @click="deleteBSFactor"
          :ripple="false"
          @keydown.enter.prevent="$event.target.blur()"
          @keydown.space.prevent="$event.target.blur()"
      />
    </div>
  </div>

  <div class="d-flex align-start">
    <v-data-table-virtual
      :headers="utility.ws_headers"
      :items="my_ws_items"
      style="background-color: transparent;"
      hide-default-footer
    >
      <template #item.factor="{ item }">
        <v-text-field
          v-model="item.factor"
          name="quantity"
          density="compact"
          hide-details
        />
      </template>

      <template #item.condition="{ item }">
        <v-text-field
          v-model="item.condition"
          name="quantity"
          density="compact"
          hide-details
        />
      </template>
    </v-data-table-virtual>

      <div class="ml-auto mt-auto d-flex ga-2 mb-2">
        <v-btn
            icon="mdi-plus"
            size="x-small"
            color="primary"
            @click="addWSFactor"
            :ripple="false"
            @keydown.enter.prevent="$event.target.blur()"
            @keydown.space.prevent="$event.target.blur()"
        />
        <v-btn
            icon="mdi-minus"
            size="x-small"
            color="red"
            @click="deleteWSFactor"
            :ripple="false"
            @keydown.enter.prevent="$event.target.blur()"
            @keydown.space.prevent="$event.target.blur()"
        />
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

const props = defineProps({
  immediate_update: {
    type: Boolean,
    default: false
  },
  bs_items: {
    type: Array,
    default: () => []
  },
  ws_items: {
    type: Array,
    default: () => []
  },
})

const emit = defineEmits([
  'update:bs_items',
  'update:ws_items'
])

const my_bs_items = ref([])
const my_ws_items = ref([])

const is_valid = computed(() => {
  const hasBS = my_bs_items.value.length > 0
  const hasWS = my_ws_items.value.length > 0

  if (!hasBS && !hasWS) {
    return false
  }

  const bsValid = my_bs_items.value.every(item =>
    item.factor.trim() !== "" &&
    item.condition.trim() !== ""
  )

  const wsValid = my_ws_items.value.every(item =>
    item.factor.trim() !== "" &&
    item.condition.trim() !== ""
  )

  return bsValid && wsValid
})

function init() {
  my_bs_items.value = props.bs_items.map(item => ({ ...item }))
  my_ws_items.value = props.ws_items.map(item => ({ ...item }))
}

onMounted(() => {
  init()
})

function addBSFactor() {
  const newItems = [...my_bs_items.value]

  if (newItems.length === 0) {
    newItems.push({
      factor: "",
      condition: ""
    })
  } else {
    newItems.push({
      ...newItems[newItems.length - 1]
    })
  }

  my_bs_items.value = newItems

  if (props.immediate_update) {
    updateItems()
  }
}

function deleteBSFactor() {
  if (my_bs_items.value.length === 0) return

  const newItems = [...my_bs_items.value]
  newItems.pop()

  my_bs_items.value = newItems

  if (props.immediate_update) {
    updateItems()
  }
}

function addWSFactor() {
  const newItems = [...my_ws_items.value]

  if (newItems.length === 0) {
    newItems.push({
      factor: "",
      condition: ""
    })
  } else {
    const lastItem = newItems[newItems.length - 1]
    newItems.push({
      ...lastItem
    })
  }

  my_ws_items.value = newItems

  if (props.immediate_update) {
    updateItems()
  }
}

function deleteWSFactor() {
  if (my_ws_items.value.length === 0) return

  const newItems = [...my_ws_items.value]
  newItems.pop()
  my_ws_items.value = newItems

  if (props.immediate_update) {
    updateItems()
  }
}

function updateItems() {
  emit('update:bs_items', my_bs_items.value)
  emit('update:ws_items', my_ws_items.value)
}

function getItems() {
  return {
    bs: my_bs_items.value,
    ws: my_ws_items.value
  }
}

function clearItems() {
  my_bs_items.value = []
  my_ws_items.value = []
}

defineExpose({
  is_valid,
  init,
  updateItems,
  getItems,
  clearItems,
})
</script>