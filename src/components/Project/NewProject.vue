<template>
  <div class="new_project">
    <v-stepper v-model="step" :items="pages">

      <template v-slot:item.1>
        <SetProjectName />
      </template>

      <template v-slot:item.2>
        <div class="select_factor_setting">
          <Factor
            :active="step === 2"
            v-model:single_selected="store.factor_setting_selected"
            title="Select Factor Setting"
            single_select
            :hint_message="utility.select_factor_hint_msg"
            height="calc(100vh - 400px)"
          />
        </div>
      </template>

      <template v-slot:item.3>
        <div class="select_user_data">
          <ExcelFileHandler
            :active="step === 3"
            v-model:single_selected="store.user_data_selected"
            title="Select User Data"
            table_name="user_data"
            single_select
            :hint_message="utility.select_user_data_hint_msg"
            height="calc(100vh - 400px)"/>
        </div>
      </template>

      <template v-slot:item.4>
        <SelectUserDataSheets 
          ref="select_user_data_sheets"
        />
      </template>

      <template v-slot:item.5>
        <div class="select_spss_export">
          <ExcelFileHandler
            :active="step === 5"
            v-model:single_selected="store.spss_export_selected"
            title="Select SPSS Export"
            table_name="spss_export"
            single_select
            :hint_message="utility.select_spss_export_hint_msg"
            height="calc(100vh - 400px)"/>
        </div>
      </template>

      <template v-slot:item.6>
        <SetAnalysisMethods />
      </template>

      <template v-slot:actions="{ next, prev }">
        <div class="d-flex align-center w-100 px-4 mb-4">
          <v-btn
            @click="prev"
            :variant="canPrev ? 'elevated' : 'text'"
            :color="canPrev ? 'grey-darken-3' : 'white'"
            :disabled="!canPrev"
            ref="prev_btn"
            :ripple="false"
            @keydown.enter.prevent="$event.target.blur()"
            @keydown.space.prevent="$event.target.blur()"
          >
            Previous
          </v-btn>

          <v-spacer />

          <v-btn
            v-if="step !== pages.length"
            @click="next"
            :variant="canNext ? 'elevated' : 'text'"
            :color="canNext ? 'grey-darken-3' : 'white'"
            :disabled="!canNext"
            ref="next_btn"
            :ripple="false"
            @keydown.enter.prevent="$event.target.blur()"
            @keydown.space.prevent="$event.target.blur()"
          >
            Next
          </v-btn>

          <v-btn
            v-else
            @click="saveProject"
            :variant="canNext ? 'elevated' : 'text'"
            color="primary"
            :disabled="!canNext"
            ref="done_btn"
          >
            Done
          </v-btn>
        </div>
      </template>
    </v-stepper>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

import { utilityStore } from '@/stores/utility'
import { newProjectStore } from '@/stores/newProject'
import { spssReaderStore } from '@/stores/spssReader'
import { pageStore } from '@/stores/page'
const utility = utilityStore()
const store = newProjectStore()
const spss_reader_store = spssReaderStore()
const page_store = pageStore()

// Pages from @components/Project/NewProject/
import SetProjectName from '@/components/Project/NewProject/SetProjectName.vue';
import Factor from '@/components/Data/Factor.vue';
import ExcelFileHandler from '@/components/Props/Data/ExcelFileHandler.vue';
import SelectUserDataSheets from './NewProject/SelectUserDataSheets.vue';
import SetAnalysisMethods from './NewProject/SetAnalysisMethods.vue';

const step = ref(1)
const pages = Array(6).fill('')
const prev_btn = ref()
const next_btn = ref()
const done_btn = ref()
const select_user_data_sheets = ref()

const canPrev = computed(() => {
  return step.value > 1
})

const canNext = computed(() => {
  if (store.is_loading) {
    return false
  }
  else if (step.value === 1) {
    return store.project_name.trim() !== ""
  }
  else if (step.value === 2) {
    return store.factor_setting_selected > 0
  }
  else if (step.value === 3) {
    return store.user_data_selected > 0
  }
  else if (step.value === 4) {
    return store.is_user_data_sheet_applied && !store.verify_result.err_msg
  }
  else if (step.value === 5) {
    return store.spss_export_selected > 0
  }
  else if (step.value === 6) {
    return store.is_spss_export_valid
  }

  return true
})

function onKeyDown(event) {
  if (utility.is_dialog_opened) {
    return
  }
  if (document.activeElement?.tagName === 'INPUT' && event.key !== 'Enter') {
    return
  }

  if (event.key === 'Enter' || event.key === 'ArrowRight') {
    if (step.value !== pages.length && canNext.value) {
      next_btn.value.$el.click()
    }
    else if (canNext.value) {
      done_btn.value.$el.click()
    }
  }
  else if (event.key === 'ArrowLeft' && canPrev.value) {
    prev_btn.value.$el.click()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', onKeyDown)

  document.documentElement.style.overflow = "hidden"
  document.body.style.overflow = "hidden"
  store.reset()
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)

  document.documentElement.style.overflow = ""
  document.body.style.overflow = ""
})

watch(step, (newStep, oldStep) => {
  store.is_loading = false

  if (newStep === 4 && oldStep < newStep) {
    select_user_data_sheets.value?.init()
  }
  else if (newStep === 6 && oldStep < newStep) {
    store.is_spss_export_sheet_loading = false
    store.triggerReadSPSSExportSheetNames()
  }
})

async function saveProject() {
  const project_id = await window.api.addProject(
    store.project_name,
    store.factor_setting_selected,
    store.user_data_selected,
    store.spss_export_selected,
    JSON.stringify(store.dpvar_dict),
    JSON.stringify(store.sheet_names_and_types),
  )

  spss_reader_store.project_id = project_id
  page_store.changePage('open_recent')
}
</script>