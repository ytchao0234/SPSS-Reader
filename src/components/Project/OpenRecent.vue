<template>
  <div class="open_recent">
    <v-card class="pa-4" flat>
      <div class="d-flex align-center flex-nowrap pb-2">
        <v-card-title>
          <div class="d-flex align-center">
              <h3 class="my-0">Projects</h3>
          </div>
        </v-card-title>

        <div class="ml-auto d-flex ga-2">
          <SelectButton
            v-model:select_mode="select_mode"
            v-model:selected="selected"
            @enter-select-mode="enterSelectMode"
            @cancel-select-mode="cancelSelectMode"
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
        :items="project_items"
        item-value="id"
        height="calc(100vh - 230px)"
        :show-select="select_mode"
        :search="search"
        show-expand
        v-model:expanded="expanded"
        @click:row="onRowClick"
      >
        <template v-if="!select_mode" v-slot:item.actions="{ item }">
          <div class="d-flex align-center ga-2">
            <DeleteButton
              :id="item.id"
              icon
              @single-delete="singleDelete"
            />

            <ExportSigBtn 
              :project-id="item.id"
              :spss_export_filepath="item.spss_export[0].filepath"
              :method_dict="item.method_dict"
              @on-exported="lastUsed(item.id)"
            />

            <QueryDetailBtn
              :project-id="item.id"
              :project-title="item.project_name"
              :user_data_filepath="item.user_data[0].filepath"
              :spss_export_filepath="item.spss_export[0].filepath"
              :between_subjects_factors="item.factor[0].between_subjects_factors"
              :within_subjects_factors="item.factor[0].within_subjects_factors"
              :dpvar_dict="item.dpvar_dict"
              :method_dict="item.method_dict"
              @on-close="lastUsed(item.id)"
            />
          </div>
        </template>

        <template #expanded-row="{ columns, item }">
          <tr class="table-expand">
            <td :colspan="columns.length">
              <v-data-table-virtual
                class="table-expand"
                :headers="utility.factor_headers_in_projects"
                :items="item.factor"
                item-value="key"
                show-expand
                hide-default-header
                hide-default-footer
              >
                <template v-slot:item.actions="{ item }">
                  <DownloadButton 
                    type="json"
                    :args="[item.between_subjects_factors, item.within_subjects_factors]"
                    :download="utility.exportFactorGroup"
                  />
                </template>

                <template #expanded-row="{ columns, item }">
                  <tr>
                    <td :colspan="columns.length">
                      <div class="ma-2">
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

              <v-divider></v-divider>

              <v-data-table-virtual
                class="table-expand"
                :headers="utility.file_headers_in_projects"
                :items="item.user_data"
                item-value="key"
                hide-default-header
                hide-default-footer
              >
                <template v-slot:item.actions="{ item }">
                  <DownloadButton
                    type="excel"
                    :args="[item.filename, item.filepath]"
                    :download="utility.exportExcelFile"
                  />
                </template>
              </v-data-table-virtual>

              <v-divider></v-divider>

              <v-data-table-virtual
                class="table-expand"
                :headers="utility.file_headers_in_projects"
                :items="item.spss_export"
                item-value="key"
                hide-default-header
                hide-default-footer
              >
                <template v-slot:item.actions="{ item }">
                  <DownloadButton
                    type="excel"
                    :args="[item.filename, item.filepath]"
                    :download="utility.exportExcelFile"
                  />
                </template>
              </v-data-table-virtual>
            </td>
          </tr>
        </template>
      </v-data-table-virtual>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

import { utilityStore } from '@/stores/utility'
import { spssReaderStore } from '@/stores/spssReader'
const utility = utilityStore()
const store = spssReaderStore()

// Props
import IconTooltip from '@/components/Props/IconTooltip.vue'
import SelectButton from '@/components/Props/SelectButton.vue'
import DeleteButton from '@/components/Props/DeleteButton.vue'
import FactorTable from '@/components/Props/Factor/FactorTable.vue'
import DownloadButton from '@/components/Props/DownloadButton.vue'
import ExportSigBtn from '@/components/Props/Project/ExportSigBtn.vue'
import QueryDetailBtn from '@/components/Props/Project/QueryDetailBtn.vue'

const headers = [
  {
    title: '',
    key: 'actions',
    width: '10%'
  },
  {
    title: 'Project Name',
    key: 'project_name',
    width: '40%'
  },
  {
    title: 'Last Used Time',
    key: 'last_used_time',
    width: '25%'
  },
  {
    title: 'Created Time',
    key: 'created_time',
    width: '25%'
  }
]

const project_items = ref([])
const factor_items = ref([])
const search = ref('')
const select_mode = ref(false)
const selected = ref([])
const expanded = ref([])

const filtered_project_items = computed(() => {
  if (!search.value) return project_items.value

  const keyword = search.value.toLowerCase()

  return project_items.value.filter(item =>
    item.project_name.toLowerCase().includes(keyword)
  )
})

const ids = computed(() =>
  filtered_project_items.value.map(item => item.id)
)

onMounted(async () => {
  document.documentElement.style.overflow = "hidden"
  document.body.style.overflow = "hidden"
  store.reset()

  await refresh()
})

onUnmounted(() => {
  document.documentElement.style.overflow = ""
  document.body.style.overflow = ""
})

async function refresh() {
  const projects = await window.api.getProjects()

  project_items.value = await Promise.all(
    projects.map(async (group) => {
      const factor = await window.api.getFactorGroupById(group.factor_id)
      const user_data = await window.api.getFileById('user_data', group.user_data_id)
      const spss_export = await window.api.getFileById('spss_export', group.spss_export_id)

      return {
        ...group,
        factor: [{
          key: factor?.id ?? 1,
          title: 'Factor',
          factor: factor?.title ?? '',
          between_subjects_factors: JSON.parse(factor?.between_subjects_factors ?? "[]"),
          within_subjects_factors: JSON.parse(factor?.within_subjects_factors ?? "[]")
        }],
        user_data: [{
          key: user_data?.id ?? 1,
          title: 'User Data',
          filename: user_data?.filename ?? '',
          filepath: user_data?.filepath ?? '',
          upload_time: user_data?.upload_time ?? ''
        }],
        spss_export: [{
          key: spss_export?.id ?? 1,
          title: 'SPSS Export',
          filename: spss_export?.filename ?? '',
          filepath: spss_export?.filepath ?? '',
          upload_time: spss_export?.upload_time ?? ''
        }],
        dpvar_dict: JSON.parse(group.dependent_variables),
        method_dict: JSON.parse(group.analysis_methods)
      }
    }
  )
)
}

async function lastUsed(id) {
  const project = await window.api.getProjectById(id)
  const index = project_items.value.findIndex(item => item.id === id)
  project_items.value[index].last_used_time = project.last_used_time
}

function onSearchUpdate(value) {
  const idSet = new Set(ids.value)

  selected.value = selected.value.filter(id =>
    idSet.has(id)
  )
}

function onRowClick(event, row) {
  const id = row.item.id
  const index = expanded.value.indexOf(id)

  if (index === -1) {
    expanded.value.push(id)
  } else {
    expanded.value.splice(index, 1)
  }
}

function enterSelectMode() {
  expanded.value = []
  selected.value = []
  select_mode.value = true
}

function cancelSelectMode() {
  expanded.value = []
}

async function singleDelete(id) {
  await window.api.deleteProject(id)
  await refresh()
}

async function deleteSelected() {
  for(const id of selected.value){
    await window.api.deleteProject(id)
  }

  select_mode.value = false
  selected.value = []
  await refresh()
}
</script>