<template>
  <div class="factor">
    <div
      @dragover.prevent="onDragOver"
      @drop.prevent="onDrop"
    >
      <FileUploadAlert
        v-model:show_success="show_success"
        v-model:show_warning="show_warning"
        v-model:show_error="show_error"
        success_message="The following files have been uploaded successfully:"
        warning_message="The following files were ignored because they are not vaild Json files:"
        error_message="Failed to upload the following files:"
        :valid_files="valid_files"
        :not_valid_files="not_valid_files"
        :failed_files="failed_files"
      />

      <v-card class="pa-4" flat>
        <div class="d-flex align-center flex-nowrap pb-2">
          <v-card-title>
            <div class="d-flex align-center ga-4">
              <h3 class="my-0">{{ props.title }}</h3>

              <IconTooltip
                type="info"
                location="bottom"
                :hint_message="hint_message"
              />
            </div>
          </v-card-title>

          <div class="ml-auto d-flex ga-2">
            <template v-if="!select_mode">
              <AddFactorGroupBtn
                @request-refresh="refresh"
              />

              <UploadFileBtn 
                type="json"
                v-model:result="uploaded_result"
                @update:result="importJsonFile"
              />
            </template>
            
            <SelectButton
              v-model:select_mode="select_mode"
              v-model:selected="selected"
              :alert-msg="deleteAlertMsg"
              @enter-select-mode="enterSelectMode"
              @update-alert-msg="updateDeleteAlertMsg"
              @delete-selected="deleteSelected"
            />
          </div>
        </div>

        <v-text-field
          v-model="search"
          label="Search"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          hide-details
          single-line
          @update:modelValue="onSearchUpdate"
        />

        <v-data-table-virtual
          v-model="selected"
          :headers="utility.factor_headers"
          :items="filtered_factor_groups"
          item-value="id"
          :height="props.height"
          :show-select="select_mode || single_select_mode"
          :select-strategy="single_select_mode ? 'single' : 'multiple'"
          v-model:expanded="expand"
          show-expand
          fixed-header
          :search="search"
          @click:row="onRowClick"
        >
          <template v-slot:item.actions="{ item }">
            <div class="d-flex align-center ga-2">
              <DeleteButton
                :id="item.id"
                icon
                :alert-msg="deleteAlertMsg"
                @update-alert-msg="updateDeleteAlertMsg(item.id)"
                @single-delete="singleDelete(item.id)"
              />

              <DownloadButton
                type="json"
                :args="[item.between_subjects_factors, item.within_subjects_factors]"
                :download="utility.exportFactorGroup"
              />

              <EditFactorGroupBtn
                :id="item.id"
                :bs_items="item.between_subjects_factors"
                :ws_items="item.within_subjects_factors"
                @request-refresh="refresh"
                @request-expand="expand"
              />
            </div>
          </template>

          <template #expanded-row="{ columns, item }">
            <tr class="table-expand">
              <td :colspan="columns.length">
                <div class="ma-4">
                  <FactorTable
                    type="between"
                    :items="item.between_subjects_factors"
                  />

                  <FactorTable
                    type="within"
                    :items="item.within_subjects_factors"
                  />
                </div>
              </td>
            </tr>
          </template>
        </v-data-table-virtual>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

// Props
import IconTooltip from '@/components/Props/IconTooltip.vue'
import UploadFileBtn from '@/components/Props/UploadFileBtn.vue'
import SelectButton from '@/components/Props/SelectButton.vue'
import DeleteButton from '@/components/Props/DeleteButton.vue'
import AddFactorGroupBtn from '@/components/Props/Factor/AddFactorGroupBtn.vue'
import EditFactorGroupBtn from '@/components/Props/Factor/EditFactorGroupBtn.vue'
import FactorTable from '@/components/Props/Factor/FactorTable.vue'
import FileUploadAlert from '@/components/Props/FileUploadAlert.vue'
import DownloadButton from '@/components/Props/DownloadButton.vue'

const props = defineProps({
  active: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: 'Factor'
  },
  single_select: {
    type: Boolean,
    default: false
  },
  single_selected: {
    type: Number,
    default: null
  },
  hint_message: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: 'calc(100vh - 230px)'
  }
})

const emit = defineEmits([
  'update:single_selected'
])

const hint_message = computed(() =>
  props.hint_message || utility.factor_hint_msg
)

const factor_groups = ref([])
const expand = ref([])
const show_success = ref(false)
const show_warning = ref(false)
const show_error = ref(false)
const valid_files = ref([])
const not_valid_files = ref([])
const failed_files = ref([])
const uploaded_result = ref({})
const search = ref('')
const select_mode = ref(false)
const selected = ref([])
const deleteAlertMsg = ref('')

const single_select_mode = computed(() =>
  props.single_select && !select_mode.value
)

async function refresh() {
  const res = await window.api.getFactorGroups()
  factor_groups.value = res.map(group => (
    {
      ...group,
      between_subjects_factors: JSON.parse(group.between_subjects_factors),
      within_subjects_factors: JSON.parse(group.within_subjects_factors)
    }
  ))
}

function init() {
  factor_groups.value = []
  expand.value = []
  show_success.value = false
  show_warning.value = false
  show_error.value = false
  valid_files.value = []
  not_valid_files.value = []
  failed_files.value = []
  uploaded_result.value = {}
  search.value = ''
  if (select_mode.value) {
    selected.value = []
  }
  select_mode.value = false
  refresh()
}

onMounted(() => {
  document.documentElement.style.overflow = "hidden"
  document.body.style.overflow = "hidden"
  init()
})

onUnmounted(() => {
  document.documentElement.style.overflow = ""
  document.body.style.overflow = ""
})

watch(() => props.active, (active) => {
  if (active) {
    init()
  }
})

watch(
  () => props.single_selected,
  value => {
    if (single_select_mode.value && value !== null) {
      selected.value = [value]
    }
  },
  { immediate: true }
)

watch(selected, value => {
  if (single_select_mode.value) {
    emit('update:single_selected', value.length ? value[0] : null)
  }
})

function onRowClick(event, row) {
  const id = row.item.id
  const index = expand.value.indexOf(id)

  if (index === -1) {
    expand.value.push(id)
  } else {
    expand.value.splice(index, 1)
  }
}

function onDragOver(event) {
  event.dataTransfer.dropEffect = 'copy'
}

async function onDrop(event) {
  const dropped_files = Array.from(event.dataTransfer.files)
  if (!dropped_files.length)
    return

  const filepaths = dropped_files.map(file =>
    window.api.getFilePath(file)
  )

  valid_files.value = []
  not_valid_files.value = []
  failed_files.value = []

  const result = await utility.readJsonFiles(filepaths)

  for (const res of result) {
    handleUpload(res)
  }

  await refresh()
}

async function importJsonFile() {
  handleUpload(uploaded_result.value)
  await refresh()
}

function handleUpload(res) {
  if (res === null) { // Cancel
    return
  }
  else if (!res.success) {
    failed_files.value.push(res.filename)
  }
  else if (!res.valid) {
    not_valid_files.value.push(res.filename)
  }
  else {
    valid_files.value.push(res.filename)
  }

  show_success.value = valid_files.value.length > 0
  show_warning.value = not_valid_files.value.length > 0
  show_error.value = failed_files.value.length > 0
}

const filtered_factor_groups = computed(() => {
  if (!search.value) return factor_groups.value

  const keyword = search.value.toLowerCase()

  return factor_groups.value.filter((item =>
    item.title.toLowerCase().includes(keyword)
  ))
})

const ids = computed(() =>
  Object.keys(filtered_factor_groups.value).map(Number)
)

function onSearchUpdate(value) {
  const idSet = new Set(ids.value)

  selected.value = selected.value.filter(id =>
    idSet.has(id)
  )
}

function enterSelectMode() {
  expand.value = []
  selected.value = []
  select_mode.value = true
}

async function updateDeleteAlertMsg(id) {
  let count

  if (id) {
    count = await window.api.deleteFactorGroupDependCount(id)

    if (count > 0) {
      deleteAlertMsg.value = `This factor setting is still used in ${count} projects. Do you still want to delete it? (The dependent projects will be deleted as well.)`
    }
    else {
      deleteAlertMsg.value = ''
    }
  }
  else if (selected.value) {
    count = 0

    for (const item of selected.value) {
      count += await window.api.deleteFactorGroupDependCount(item)
    }

    if (count > 0) {
      deleteAlertMsg.value = `These factor settings are still used in ${count} projects. Do you still want to delete them? (The dependent projects will be deleted as well.)`
    }
    else {
      deleteAlertMsg.value = ''
    }
  }
}

async function singleDelete(id) {
  await window.api.deleteFactorGroup(id)
  await refresh()
}

async function deleteSelected() {
  for(const id of selected.value){
    await window.api.deleteFactorGroup(id)
  }

  select_mode.value = false
  selected.value = []
  await refresh()
}
</script>