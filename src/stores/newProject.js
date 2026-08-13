import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const newProjectStore = defineStore('new_project', () => {
  // Step 1 Set Project Name
  const project_name = ref('')

  // Step 2 Set Factors
  const factor_setting_selected = ref(null)

  // Step 3 Select User Data
  const user_data_selected = ref(null)

  // Step 4 Select User Data Sheets
  const is_user_data_sheet_loading = ref(false)
  const is_verify_user_data_loading = ref(false)
  const is_user_data_sheet_applied = ref(false)
  const user_data_sheets_selected = ref([])
  const readUserData = ref(0) // event
  function triggerReadUserData() {
    readUserData.value++
  }
  const verify_result = ref({
    success: true,
    err_msg: '',
  })
  const dpvar_dict = ref({})

  // Step 5 Select SPSS Export
  const spss_export_selected = ref(null)

  // Step 6 Set Analysis Methods
  const is_spss_export_sheet_loading = ref(false)
  const readSPSSExportSheetNames = ref(0) // event
  function triggerReadSPSSExportSheetNames() {
    readSPSSExportSheetNames.value++
  }
  const is_spss_export_valid = ref(false)
  const sheet_names_and_types = ref({})

  function reset() {
    project_name.value = ''
    factor_setting_selected.value = null
    user_data_selected.value = null
    is_user_data_sheet_loading.value = false
    is_user_data_sheet_applied.value = false
    is_verify_user_data_loading.value = false
    user_data_sheets_selected.value = []
    readUserData.value = 0
    verify_result.value = {
      success: true,
      err_msg: '',
    }
    dpvar_dict.value = {}
    spss_export_selected.value = null
    is_spss_export_sheet_loading.value = false
    readSPSSExportSheetNames.value = 0
    is_spss_export_valid.value = false
    sheet_names_and_types.value = {}
  }

  const is_loading = computed({
    get () {
      return is_user_data_sheet_loading.value ||
             is_verify_user_data_loading.value ||
             is_spss_export_sheet_loading.value
    },
    set (value) {
      is_user_data_sheet_loading.value = value
      is_verify_user_data_loading.value = value
      is_spss_export_sheet_loading.value = value
    }
  })

  return {
    reset, is_loading,

    // Step 1 Set Project Name
    project_name,

    // Step 2 Set Factors
    factor_setting_selected,

    // Step 3 Select User Data
    user_data_selected,

    // Step 4 Select User Data Sheets
    is_user_data_sheet_loading, 
    is_user_data_sheet_applied, is_verify_user_data_loading,
    user_data_sheets_selected,
    readUserData, triggerReadUserData,
    verify_result, dpvar_dict,

    // Step 5 Select SPSS Export
    spss_export_selected,

    // Step 6 Set Analysis Methods
    is_spss_export_sheet_loading, 
    readSPSSExportSheetNames, triggerReadSPSSExportSheetNames,
    is_spss_export_valid,
    sheet_names_and_types
  }
})