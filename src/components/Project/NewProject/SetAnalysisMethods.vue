<template>
  <div class="set_analysis_methods">
    <v-card flat :loading="store.is_spss_export_sheet_loading">
      <v-card-title>
        <div class="d-flex align-center ga-4">
          <h3 class="my-0">Set Analysis Methods</h3>

          <IconTooltip
            type="info"
            location="bottom"
            :hint_message="utility.select_analysis_method_hint_msg"
          />

          <IconTooltip
            v-if="error_message"
            type="error"
            location="bottom"
            :hint_message="error_message"
          />

          <template v-else>
            <IconTooltip
              v-if="!store.is_spss_export_sheet_loading"
              type="success"
            />
          </template>
        </div>
      </v-card-title>

      <v-data-table-virtual
        v-if="!store.is_spss_export_sheet_loading"
        :headers="utility.analysis_method_headers"
        :items="dpvars_items"
        item-value="id"
        height="calc(100vh - 300px)"
        fixed-header
        style="overflow-x: auto;"
      >
        <template #headers="{ columns }">
          <tr class="bg-grey-darken-3">
            <th
              v-for="column in columns"
              :key="column.key"
              :style="`width: ${column.width} !important; min-width: 300px !important;`"
            >
              {{ column.title }}
            </th>
          </tr>
        </template>

        <template #item.dpvar_name="{ item, index }">
          <div class="d-flex align-center ga-4">
            <GridContainer
              v-if="item.analysis_method.includes('Nonparametric')"
              :index="index"
              :items="item.dpvar_list"
              :source-items="dpvar_name_list"
              @update-passed="handleDpvarMatched"
            />

            <template v-else>
              <span>{{ item.dpvar_name }}</span>
            </template>
          </div>
        </template>

        <template #item.analysis_method="{ item, index }">
          <div class="d-flex align-center ga-4">
            <span>{{ item.analysis_method }}</span>

            <IconTooltip
              :type="item.valid_type"
              location="top"
              :hint_message="item.err_msg"
            />
          </div>
        </template>
      </v-data-table-virtual>
    </v-card>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { utilityStore } from '@/stores/utility'
import { newProjectStore } from '@/stores/newProject'
const utility = utilityStore()
const store = newProjectStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'
import GridContainer from '@/components/Props/GridContainer.vue'

const error_message = ref('')

const dpvars_items = ref([])
const is_dpvar_matched = ref([])
const analysis_method = ref('')

const dpvar_name_list = computed(() => {
  return Object.values(store.dpvar_dict)
    .filter(item => item.use !== false)
    .flatMap(item =>
      Array(item.count).fill(item.dpvar_name)
    )
})

watch(
  () => store.readSPSSExportSheetNames,
  () => {
    error_message.value = ''
    ReadSPSSExportSheetNamesAndTypes()
  },
  { immediate: true }
)

watch(
  () => is_dpvar_matched.value,
  () => {
    if (!is_dpvar_matched.value || is_dpvar_matched.value.every(item => item != null)) {
      updateErrorMsg()
    }
  },
  { deep: true }
)

function handleDpvarMatched({index, value}) {
  is_dpvar_matched.value[index] = value
}

function updateErrorMsg() {
  error_message.value = ''

  if (dpvars_items.value.some(item => item.analysis_method === 'Count mismatch')) {
    error_message.value +=
      '• The number of SPSS export sheet names does not match the number of dependent variables. Please correct the settings.\n'
  }

  if (is_dpvar_matched.value.some(value => value === false)) {
    error_message.value += 
      '• Some dependent variables in the SPSS Export file were not found in the User Data file.'
  }

  if (dpvars_items.value.some(item => item.err_msg)) {
    error_message.value +=
      '• Some sheets do not have a valid analysis method. Please adjust the settings.'
  }

  store.is_spss_export_valid = (error_message.value === '')
}

async function ReadSPSSExportSheetNamesAndTypes() {
  store.is_spss_export_sheet_loading = true
  const spss_export_file = await window.api.getFileById('spss_export', store.spss_export_selected)
  store.sheet_names_and_types = []
  let sheet_names = []

  await window.api.runPython(
    'read_sheet_names_and_types',
    spss_export_file.filepath
  )
  .then(res => {
    store.sheet_names_and_types = JSON.parse(res)
    sheet_names = Object.keys(store.sheet_names_and_types)
    if (sheet_names) {
      analysis_method.value = store.sheet_names_and_types[sheet_names[0]]['Analysis Method']
    }
  })
  .catch(err => {
    console.log('ERROR:', err)
  })

  store.is_spss_export_sheet_loading = false
  let maxLength

  if (analysis_method.value?.includes('Nonparametric')) {
    maxLength = sheet_names.length
  }
  else {
    maxLength = Math.max(dpvar_name_list.value.length, sheet_names.length)
  }

  dpvars_items.value = Array.from({ length: maxLength }, (_, i) => {
    const dpvar_name = dpvar_name_list.value[i] ?? ''
    const sheet_name = sheet_names[i] ?? ''
    const sheet = store.sheet_names_and_types[sheet_name]
    const dpvar_list = sheet?.[analysis_method.value].dpvar_list

    if (dpvar_name && sheet) {
      sheet.dpvar_name = dpvar_name

      if (analysis_method.value?.includes('ANOVA')) {
        sheet.category = store.dpvar_dict[dpvar_name].category
        store.dpvar_dict[dpvar_name].sheet_name = sheet_name
      }
    }

    if (analysis_method.value?.includes('Nonparametric')) {
      dpvar_list.forEach(item => {
        store.dpvar_dict[item].sheet_name = sheet_name
      });
    }

    const method = (!dpvar_name || !sheet_name) ? 'Count mismatch' : analysis_method.value

    const obj = {
      dpvar_name: dpvar_name,
      spss_export_sheet_name: sheet_name,
      analysis_method: method,
      dpvar_list: dpvar_list ?? [],
      valid_type: sheet?.[method]?.can_do ? 'success' : 'error',
      err_msg: method ? sheet?.[method]?.err_msg ?? '' : '',
    }
    return obj
  })

  if (analysis_method.value?.includes('Nonparametric')) {
    is_dpvar_matched.value = Array.from( {length: maxLength}, () => null )
  }
  else {
    is_dpvar_matched.value = []
  }
}
</script>