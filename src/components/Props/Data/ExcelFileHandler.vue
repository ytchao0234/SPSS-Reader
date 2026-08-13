<template>
  <div class="excel_file_handler">
    <div
      @dragover.prevent="onDragOver"
      @drop.prevent="onDrop"
    >
      <FileUploadAlert
        v-model:show_success="show_success"
        v-model:show_warning="show_warning"
        v-model:show_error="show_error"
        success_message="The following files have been uploaded successfully:"
        warning_message="The following files were ignored because they are not Excel files:"
        error_message="Failed to upload the following files:"
        :valid_files="valid_files"
        :not_valid_files="not_valid_files"
        :failed_files="failed_files"
      />

      <v-card class="pa-4">
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
            <UploadFileBtn 
              v-if="!select_mode"
              type="excel"
              :table_name="props.table_name"
              v-model:result="uploaded_result"
              @update:result="uploadExcelFile"
            />
            
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
          :headers="headers"
          :items="files"
          item-value="id"
          :show-select="select_mode || single_select_mode"
          :select-strategy="single_select_mode ? 'single' : 'multiple'"
          :height="props.height"
          fixed-header
          :search="search"
        >
          <template v-if="!select_mode" v-slot:item.actions="{ item }">
            <div class="d-flex align-center ga-2">
              <DeleteButton
                :id="item.id"
                icon
                :alert-msg="deleteAlertMsg"
                @update-alert-msg="updateDeleteAlertMsg(item.id)"
                @single-delete="singleDelete"
              />

              <DownloadButton
                type="excel"
                :args="[item.filename, item.filepath]"
                :download="utility.exportExcelFile"
              />
            </div>
          </template>
        </v-data-table-virtual>
      </v-card>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'
import UploadFileBtn from '@/components/Props/UploadFileBtn.vue'
import FileUploadAlert from '@/components/Props/FileUploadAlert.vue'
import SelectButton from '@/components/Props/SelectButton.vue'
import DeleteButton from '@/components/Props/DeleteButton.vue'
import DownloadButton from '@/components/Props/DownloadButton.vue'

const props = defineProps({
  active: {
    type: Boolean,
    default: true
  },
  table_name: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: 'Excel File Handler'
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
  props.hint_message || utility.excel_file_handler_hint_msg
)

const headers = computed(() => {
  const list = []

  if (!select_mode.value) {
    list.push({
      title: "",
      key: "actions",
      width: "10%",
      sortable: false
    })
  }

  list.push(...utility.file_headers)

  return list
})

const show_success = ref(false)
const show_warning = ref(false)
const show_error = ref(false)
const valid_files = ref([])
const not_valid_files = ref([])
const failed_files = ref([])
const files = ref([])
const selected = ref([])
const select_mode = ref(false)
const search = ref('')
const uploaded_result = ref({})
const deleteAlertMsg = ref('')

const single_select_mode = computed(() =>
  props.single_select && !select_mode.value
)

async function refresh() {
  files.value = await window.api.getFiles(props.table_name)
}

function init() {
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

  const result = await utility.uploadExcelFiles(filepaths, props.table_name)

  for (const res of result) {
    if (res === null) {
      continue
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
  }

  show_success.value = valid_files.value.length > 0
  show_warning.value = not_valid_files.value.length > 0
  show_error.value = failed_files.value.length > 0

  await refresh()
}

async function uploadExcelFile() {
  show_success.value = false
  show_warning.value = false
  show_error.value = false

  if (uploaded_result.value === null) { // Cancel
    return
  }
  else if (!uploaded_result.value.success) {
    show_error.value = true
    failed_files.value = [uploaded_result.value.filename]
  }
  else if (!uploaded_result.value.valid) {
    show_warning.value = true
    not_valid_files.value = [uploaded_result.value.filename]
  }
  else {
    show_success.value = true
    valid_files.value = [uploaded_result.value.filename]
  }

  await refresh()
}

const filtered_files = computed(() => {
  if (!search.value) return files.value

  const keyword = search.value.toLowerCase()

  return files.value.filter(item =>
    item.filename.toLowerCase().includes(keyword)
  )
})

const ids = computed(() =>
  filtered_files.value.map(item => item.id)
)

function onSearchUpdate(value) {
  const idSet = new Set(ids.value)

  selected.value = selected.value.filter(id =>
    idSet.has(id)
  )
}

async function updateDeleteAlertMsg(id) {
  let count

  if (id) {
    count = await window.api.deleteFileDependCount(id, props.table_name)

    if (count > 0) {
      deleteAlertMsg.value = `This file is still used in ${count} projects. Do you still want to delete it? (The dependent projects will be deleted as well.)`
    }
    else {
      deleteAlertMsg.value = ''
    }
  }
  else if (selected.value) {
    count = 0

    for (const item of selected.value) {
      count += await window.api.deleteFileDependCount(item, props.table_name);
    }

    if (count > 0) {
      deleteAlertMsg.value = `These files are still used in ${count} projects. Do you still want to delete them? (The dependent projects will be deleted as well.)`
    }
    else {
      deleteAlertMsg.value = ''
    }
  }
}

async function singleDelete(id) {
  await window.api.deleteFile(id, props.table_name)
  selected.value = []
  await refresh()
}

function enterSelectMode(){
  select_mode.value = true
  selected.value = []
}

function cancelSelect(){
  select_mode.value = false
  selected.value = []
}

async function deleteSelected(){
  for(const id of selected.value){
    await window.api.deleteFile(id, props.table_name)
  }

  select_mode.value = false
  selected.value = []
  await refresh()
}
</script>