<template>
  <div class="query_analysis_detail_button">
    <v-dialog
      v-model="dialog"
      max-width="1200"
      persistent
      @keydown.backspace.prevent.stop="onClose"
      @keydown.enter.prevent.stop="onApply"
    >
      <template v-slot:activator="{ props }">
        <IconTooltip
          :dialog-props="props"
          type="read_file"
          hint_message="Query Analysis Details"
          density="default"
          is-button
          :on-btn-click="onOpenDialog"
        />
      </template>

      <v-card
        :title="projectTitle ? `Query Analysis Detail from &quot;${projectTitle}&quot;` : 'Query Analysis Detail'"
        color="grey-darken-3"
        class="pa-1 overflow-y-auto"
        height="600"
      >
        <v-card-text class="overflow-y-auto d-flex flex-grow-1 ga-2">
          <div class="w-40 d-flex flex-column">
            <!-- Left -->
            <div class="flex-grow-1">
              <v-autocomplete
                v-model="sheet_selected"
                :items="sheet_items"
                label="Sheet"
                clearable
                style="width: 100%;"
                @keydown.enter.prevent="$event.target.blur()"
                @keydown.space.prevent="$event.target.blur()"
              />

              <v-autocomplete
                v-model="dpvar_selected"
                :items="dpvar_items"
                label="Dependent Variable"
                clearable
                style="width: 100%;"
                @keydown.enter.prevent="$event.target.blur()"
                @keydown.space.prevent="$event.target.blur()"
              />

              <v-autocomplete
                :disabled="!dpvar_selected"
                v-model="effect_selected"
                :items="effect_items"
                label="Effect"
                clearable
                style="width: 100%;"
                @keydown.enter.prevent="$event.target.blur()"
                @keydown.space.prevent="$event.target.blur()"
              />

              <div v-if="method.includes('ANOVA')" class="d-flex flex-column">
                <GridSelector
                  v-for="(item, index) in option_items"
                  class="mb-1 flex-grow-1"
                  title="Options (Multi-select)"
                  :items="item"
                  :disabled="!effect_selected"
                  :valid="isValidGridSelector(index)"
                  v-model:grid-selected="grid_selected_list[index]"
                  multiple
                />
              </div>
            </div>
          </div>

          <div class="w-60">
            <!-- Right -->
            <div class="flex-grow-1 h-100">
              <v-card class="h-100 overflow-y-auto" :loading="loading">
                <v-card-title style="font-size: 18px;">
                  Output
                </v-card-title>

                <v-card-text>
                  <template v-if="test_statistics">
                    <TextCopySheet
                      v-for="item in test_statistics"
                      :text="item"
                      color="grey-darken-3"
                    />
                  </template>

                  <v-data-table-virtual
                    v-if="descriptive_statistics_items.length > 0"
                    :headers="descriptive_statistics_headers"
                    :items="descriptive_statistics_items"
                    item-value="id"
                    class="rounded-md mt-2 border bg-grey-darken-3"
                    show-expand
                    hide-default-footer
                    density="compact"
                    :expanded="expand"
                    @update-expanded="onRowClick"
                    @click:row="onRowClick"
                  >
                    <template #headers="{ columns }">
                      <tr class="bg-grey-darken-2">
                        <th
                          v-for="column in columns"
                          :key="column.key"
                        >
                          {{ column.title }}
                        </th>
                      </tr>
                    </template>

                    <template #expanded-row="{ columns, item }">
                      <tr>
                        <td :colspan="columns.length">
                          <div class="my-1" density="compact">
                              <v-alert
                                v-if="item.err_msg"
                                class="mb-1"
                                :text="item.err_msg"
                                type="warning"
                                variant="tonal"
                                density="compact"
                              >
                                <template #prepend>
                                  <v-icon size="18">
                                    mdi-alert
                                  </v-icon>
                                </template>
                              </v-alert>

                              <TextCopySheet :text="item.MeanSD" color="#333" />
                              <v-divider/>
                              <TextCopySheet :text="item.MdnIQR" color="#333" />
                              <v-divider/>

                              <v-expansion-panels flat rounded="md">
                                <v-expansion-panel color="#333">
                                  <v-expansion-panel-title
                                    class="justify-center"
                                    density="compact"
                                    style="min-height: 38px; padding-top: 0; padding-bottom: 0; padding-left: 12px;"
                                  >
                                    Fields Used in Descriptive Statistics
                                  </v-expansion-panel-title>
                                  <v-expansion-panel-text class="bg-grey-darken-4">
                                    <ul>
                                      <li v-for="data_field in item.Data_Fields">
                                        {{ data_field }}
                                      </li>
                                    </ul>
                                  </v-expansion-panel-text>
                                </v-expansion-panel>
                              </v-expansion-panels>
                          </div>
                        </td>
                      </tr>
                    </template>
                  </v-data-table-virtual>

                  <div v-if="descriptive_statistics_items.length > 0">
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </div>
        </v-card-text>

        <template v-slot:actions>
          <v-spacer></v-spacer>
            <v-btn
              color="primary"
              :disabled="!canApply()"
              @click="onApply"
              :ripple="false"
              @keydown.enter.prevent="$event.target.blur()"
              @keydown.space.prevent="$event.target.blur()"
            >
              Apply
            </v-btn>

            <v-btn 
              color="grey-lighten-4" 
              @click="onClose"
            >
              Close
            </v-btn>
        </template>
      </v-card>
    </v-dialog>

    <v-overlay
      :model-value="loading"
      persistent
    >
    </v-overlay>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'
import TextCopySheet from '@/components/Props/TextCopySheet.vue'
import GridSelector from '@/components/Props/GridSelector.vue'

const props = defineProps({
  projectId: {
    type: Number,
    required: true
  },
  projectTitle: {
    type: String,
    default: ""
  },
  user_data_filepath: {
    type: String,
    required: true
  },
  spss_export_filepath: {
    type: String,
    required: true
  },
  dpvar_dict: {
    type: Object,
    required: true
  },
  method_dict: {
    type: Object,
    required: true
  }
})

const emit = defineEmits([
  'on-close'
])

const dialog = ref(false)
const loading = ref(false)
const expand = ref([])

const method = computed(() => {
  return props.method_dict[sheet_selected.value]?.['Analysis Method'] ?? ''
})

const dpvar_items = ref(
  Object.values(props.dpvar_dict)
    .filter((item) => item.use)
    .map((item => item.dpvar_name))
)
const dpvar_selected = ref(null)

const sheet_items = ref(
  Object.keys(props.method_dict)
)
const sheet_selected = ref(null)

const active_item = computed(() => {
  if (!sheet_selected.value) {
    dpvar_selected.value = null
    effect_selected.value = null
    grid_selected_list.value = []
    return []
  }
  const sheet = props.method_dict[sheet_selected.value]
  const item = sheet[method.value]
  dpvar_items.value = item.dpvar_list ? item.dpvar_list : [sheet.dpvar_name]
  return item
})

const effect_items = computed(() => {
  return Object.keys(active_item?.value.effects ?? [])
})
const effect_selected = ref(null)

const option_items = computed(() => {
  if (!sheet_selected.value) return []
  if (!dpvar_selected.value) return []
  if (!effect_selected.value) return []
  if (!active_item.value?.effects) return []

  const options = active_item.value.effects[effect_selected.value]

  const bs_factors = new Set(Object.keys(props.method_dict[sheet_selected.value].bs_dict))
  const ws_factors = new Set(Object.keys(props.method_dict[sheet_selected.value].ws_dict))
  const between_options = options.filter(option => bs_factors.has(option))
  const within_options = options.filter(option => ws_factors.has(option))

  return effect_selected.value.toLowerCase().includes('within-subjects')
    ? [between_options, within_options]
    : effect_selected.value.toLowerCase().includes('between-subjects')
    ? [between_options]
    : []
})
const grid_selected_list = ref([])

function isValidGridSelector(index) {
  if (index < option_items.value.length - 1) {
    return true
  }
  return grid_selected_list.value[index]?.length > 0 ?? false
}

const preview = ref()
const test_statistics = ref([])
const descriptive_statistics_headers = ref([])
const descriptive_statistics_items = ref([])

function init() {
  expand.value = []
  dpvar_items.value = Object.values(props.dpvar_dict)
    .filter((item) => item.use)
    .map((item => item.dpvar_name))
  dpvar_selected.value = null
  sheet_selected.value = null
  effect_selected.value = null
  grid_selected_list.value = []
  test_statistics.value = []
  descriptive_statistics_items.value = []
}

watch(
  () => sheet_selected.value,
  value => {
    dpvar_selected.value = null
  },
  { immediate: true }
)

watch(
  () => dpvar_selected.value,
  value => {
    effect_selected.value = null
  },
  { immediate: true }
)

watch(
  () => effect_selected.value,
  value => {
    grid_selected_list.value = []
  },
  { immediate: true }
)

function onRowClick(event, row) {
  const id = row.item.id
  const index = expand.value.indexOf(id)

  if (index === -1) {
    expand.value = [id]
  } else {
    expand.value.splice(index, 1)
  }
}

async function onOpenDialog() {
  utility.is_dialog_opened = true
  await window.api.updateProjectLastUsedTimeById(props.projectId)
}

function onClose(event) {
  dialog.value = false
  utility.is_dialog_opened = false
  emit('on-close')
  init()

  setTimeout(() => {
    document.activeElement?.blur()
  }, 0)
}

function canApply() {
  return props.user_data_filepath && props.spss_export_filepath &&
         dpvar_selected.value && sheet_selected.value &&
         effect_selected.value && 
         (!method.value.includes('ANOVA') || isValidGridSelector(option_items.value.length - 1))
}

async function onApply() {
  if (!canApply()) return
  loading.value = true
  preview.value = ''
  expand.value = []

  const args = {
    dpvar: dpvar_selected.value,
    data_sheet: props.dpvar_dict[dpvar_selected.value].data_sheet_name,
    spss_sheet: sheet_selected.value,
    method: method.value,
    effect: effect_selected.value,
    options: grid_selected_list.value.flat()
  }

  test_statistics.value = []
  descriptive_statistics_headers.value = []
  descriptive_statistics_items.value = []

  await window.api.runPython(
    'query-analysis-detail', 
    props.user_data_filepath, props.spss_export_filepath, JSON.stringify(args)
  )
  .then(res => {
    const result = JSON.parse(res)
    test_statistics.value = result.test_statistics

    descriptive_statistics_headers.value = result.descriptive_statistics[0].factors.map(item => {
      return {
        title: item,
        key: item
      }
    })
    descriptive_statistics_items.value = result.descriptive_statistics.map((item, index) => ({
      id: index,
      ...item
    }))

    loading.value = false
  })
  .catch(err => {
    console.log('ERROR:', err)
    loading.value = false
  })
}
</script>