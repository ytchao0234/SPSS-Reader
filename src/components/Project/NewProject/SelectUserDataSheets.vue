<template>
  <div class="select_user_data_sheets">
    <v-card 
      flat
      class="pa-4"
      :loading="store.is_user_data_sheet_loading"
    >
      <v-card-title>
        <div class="d-flex align-center ga-4">
          <h3 class="my-0">Select User Data Sheets</h3>

          <IconTooltip
            type="info"
            location="bottom"
            :hint_message="utility.select_user_data_sheet_hint_msg"
          />
        </div>
      </v-card-title>

      <div class="d-flex align-start w-100" v-if="!store.is_user_data_sheet_loading">
        <v-card class="w-40">
          <template v-slot:text>
            <v-text-field
              v-model="sheet_search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              hide-details
              single-line
              @update:modelValue="onSearchUpdate"
            ></v-text-field>
          </template>

          <div :class="{ 'table-disabled': store.is_user_data_sheet_applied }">
            <v-data-table-virtual
              v-model="store.user_data_sheets_selected"
              :headers="sheet_headers"
              :items="sheet_items"
              item-value="sheet_name"
              show-select
              height="calc(100vh - 480px)"
              fixed-header
              :search="sheet_search"
            />
          </div>

          <div class="d-flex justify-center mt-4">
            <v-btn 
              color="primary" 
              v-if="!store.is_user_data_sheet_applied"
              :disabled="store.user_data_sheets_selected.length === 0"
              @click="ApplyUserDataSheets"
              :ripple="false"
              @keydown.enter.prevent="$event.target.blur()"
              @keydown.space.prevent="$event.target.blur()"
            >
              Apply
            </v-btn>
            <template v-else>
              <v-btn 
                color="primary" 
                variant="outlined" 
                @click="CancelApplySheets"
                :ripple="false"
                @keydown.enter.prevent="$event.target.blur()"
                @keydown.space.prevent="$event.target.blur()"
              >
                Cancel
              </v-btn>
            </template>
          </div>
        </v-card>

        <v-card 
          class="w-60" 
          v-if="store.is_user_data_sheet_applied"
          :loading="store.is_verify_user_data_loading"
        >
          <v-card-title v-if="store.is_verify_user_data_loading" class="text-center">
            {{ store.is_verify_user_data_loading ? 'Loading...' : '' }}
          </v-card-title>

          <div v-if="!store.is_verify_user_data_loading">
            <v-card v-if="!store.verify_result.success">
              <v-alert
                type="error"
                border="top"
                height="calc(100vh - 340px)"
                class="overflow-y-auto text-pre-wrap err-msg-alert"
              >
                {{ store.verify_result.err_msg }}
              </v-alert>
            </v-card>

            <template v-else>
              <v-text-field
                v-model="dpvar_search"
                label="Search"
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                hide-details
                single-line
              ></v-text-field>

              <div class="mt-4" style="height: calc(100vh - 410px); overflow-y: auto; padding: 10px;">
                <template v-for="(group, index) in dpvar_filtered_groups" :key="index">
                  <v-text-field
                    v-model="group.title"
                    label="Category"
                    variant="outlined"
                    class="py-0 px-2"
                    @update:model-value="onCategoryChange($event, index)"
                  />

                  <v-row density="compact" class="mb-4 pa-0">
                    <v-col
                      v-for="item in group.items"
                      :key="item.name"
                      cols="12"
                      class="ma-0 px-4"
                    >
                      <v-list-item
                        :title="item.name"
                        density="compact"
                        class="ma-0 pa-0"
                        :class="store.dpvar_dict[item.name].use ? 'text-white' : 'text-grey'"
                      >
                        <template v-slot:prepend>
                          <v-btn
                            icon
                            size="small"
                            @click="onDPVarUseChange($event, item.name)"
                            :ripple="false"
                            @keydown.enter.prevent="$event.target.blur()"
                            @keydown.space.prevent="$event.target.blur()"
                          >
                            <v-icon>
                              {{ store.dpvar_dict[item.name].use ? 'mdi-eye' : 'mdi-eye-off' }}
                            </v-icon>
                          </v-btn>
                        </template>

                        <template v-slot:append>
                          <div :class="store.dpvar_dict[item.name].use ? '' : 'list-item-disabled'" style="width: 100px;"> 
                            <v-number-input
                              v-model="store.dpvar_dict[item.name].count"
                              control-variant="stacked"
                              inset
                              hide-details
                              :min="1"
                              :step="1"
                              @update:model-value="onDPVarCountChange($event, item.name)"
                              @keydown.enter.prevent="$event.target.blur()"
                              @keydown.space.prevent="$event.target.blur()"
                            ></v-number-input>
                          </div>
                        </template>
                      </v-list-item>
                    </v-col>
                  </v-row>
                </template>
              </div>
            </template>
          </div>
        </v-card>
      </div>
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


const sheet_headers = [
  {
    title: "Sheet Name",
    key: "sheet_name"
  }
]

const user_data_res_dict = ref({})
const sheet_items = ref([])

const filtered_sheet_items = computed(() => {
  if (!sheet_search.value) return sheet_items.value

  const keyword = sheet_search.value.toLowerCase()

  return sheet_items.value.filter(item =>
    item.sheet_name.toLowerCase().includes(keyword)
  )
})

const sheet_names = computed(() =>
  filtered_sheet_items.value.map(item => item.sheet_name)
)

const sheet_search = ref('')
const is_sheets_valid = ref(true)

const dpvar_groups = ref([])
const dpvar_search = ref('')
const dpvar_filtered_groups = computed(() => {
  if (!dpvar_search.value) return dpvar_groups.value

  return dpvar_groups.value
    .map(group => ({
      ...group,
      items: group.items.filter(item =>
        item.name.toLowerCase().includes(dpvar_search.value.toLowerCase())
      )
    }))
    .filter(group => group.items.length > 0)
})

function init() {
  sheet_search.value = ''
  dpvar_search.value = ''
  store.is_user_data_sheet_loading = false
  store.is_user_data_sheet_applied = false
  store.is_verify_user_data_loading = false
  store.user_data_sheets_selected = []
  dpvar_groups.value = []
  store.dpvar_dict = {}
  store.verify_result = {
    'success': true,
    'err_msg': ''
  }
  store.triggerReadUserData()
}

function onSearchUpdate(value) {
  const sheet_name_set = new Set(sheet_names.value)

  store.user_data_sheets_selected = store.user_data_sheets_selected.filter(sheet_name =>
    sheet_name_set.has(sheet_name)
  )
}

watch(
  () => store.readUserData,
  () => {
    store.verify_result.success = false
    store.verify_result.err_msg = ''
    ReadUserData()
  },
  { immediate: true }
)

async function ReadUserData() {
  if (!store.user_data_selected) return

  store.is_user_data_sheet_loading = true
  const user_data_file = await window.api.getFileById('user_data', store.user_data_selected)

  await window.api.runPython('read_user_data', user_data_file.filepath)
  .then(res => {
    user_data_res_dict.value = JSON.parse(res)
    const keys = Object.keys(user_data_res_dict.value)
    sheet_items.value = keys.map(x => ({
      sheet_name: x
    }))
    store.is_user_data_sheet_loading = false
  })
  .catch(err => {
    console.log('ERROR:', err)
    store.is_user_data_sheet_loading = false
  })
}

async function ApplyUserDataSheets() {
  store.is_user_data_sheet_applied = true
  store.is_verify_user_data_loading = true
  await VerifyUserData(store.user_data_sheets_selected)

  const selectedSheets = new Set(store.user_data_sheets_selected)
  store.dpvar_dict = {}
  let itemId = 0

  dpvar_groups.value = Object.entries(user_data_res_dict.value)
    .filter(([sheet_name]) => selectedSheets.has(sheet_name))
    .map(([sheet_name, dpvars], index) => ({
      title: sheet_name,
      items: dpvars.map(item => ({
        id: itemId++,
        category_id: index,
        category: sheet_name,
        name: item
      }))
    }))

  dpvar_groups.value.forEach(group => {
    group.items.forEach(item => {
      store.dpvar_dict[item.name] = {
        category_id: item.category_id,
        category: item.category,
        data_sheet_name: item.category,
        dpvar_name: item.name,
        use: true,
        count: 1,
      }
    })
  })
}

function CancelApplySheets() {
  store.is_user_data_sheet_applied = false
  store.verify_result.success = false
  store.verify_result.err_msg = ''
}

async function VerifyUserData(sheetNameList) {
  if (!store.user_data_selected) return

  const user_data_file = await window.api.getFileById('user_data', store.user_data_selected)
  const sheet_name_list = JSON.stringify(sheetNameList)
  const factor_setting = await window.api.getFactorGroupById(store.factor_setting_selected)

  store.verify_result.err_msg = ''

  try {
    const res = await window.api.runPython(
      'verify_user_data', 
      user_data_file.filepath, 
      sheet_name_list, 
      factor_setting.between_subjects_factors, 
      factor_setting.within_subjects_factors)

    store.verify_result = JSON.parse(res)
  } catch (err) {
    console.log('ERROR:', err)
  } finally {
    await new Promise(resolve => setTimeout(resolve, 200))
    store.is_verify_user_data_loading = false
  }
}

function onCategoryChange(newValue, index) {
  Object.values(store.dpvar_dict).forEach(item => {
    if (item.category_id === index) {
      item.category = newValue
    }
  })
}

function onDPVarUseChange(newValue, dpvar_name) {
  store.dpvar_dict[dpvar_name].use = !store.dpvar_dict[dpvar_name].use
}

function onDPVarCountChange(newValue, dpvar_name) {
  store.dpvar_dict[dpvar_name].count = Math.max(1, newValue)
}

defineExpose({
  init
})
</script>