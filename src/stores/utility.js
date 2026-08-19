import { defineStore } from 'pinia'
import { ref } from 'vue'

export const utilityStore = defineStore('utility', () => {
  // State
  const is_dialog_opened = ref(false)

  // Tables
  const factor_headers = [
    {
      title: "",
      key: "actions",
      width: "10%"
    },
    {
      title: "Factor",
      key: "title",
      width: "70%"
    },
    {
      title: "Created Time",
      key: "created_time",
      width: "20%"
    },
  ]
  const file_headers = [
    {
        title: "Filename",
        key: "filename",
        width: "50%"
    },
    {
        title: "Upload Time",
        key: "upload_time",
        width: "50%"
    }
  ];
  const project_headers = [
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
  const bs_headers = [
    {
        title: "Between-subjects Factor",
        key: "factor",
        width: "50%"
    },
    {
        title: "Condition",
        key: "condition",
        width: "50%"
    },
  ]
  const ws_headers = [
    {
        title: "Within-subjects Factor",
        key: "factor",
        width: "50%"
    },
    {
        title: "Condition",
        key: "condition",
        width: "50%"
    },
  ]
  const factor_headers_in_projects = [
    {
      title: "",
      key: "actions",
      width: "10%"
    },
    {
        title: "Title",
        key: "title",
        width: "21.5%"
    },
    {
        title: "Factor",
        key: "factor",
        width: "68.5%"
    },
  ]
  const file_headers_in_projects = [
    {
      title: "",
      key: "actions",
      width: "10%"
    },
    {
        title: "Title",
        key: "title",
        width: "20%"
    },
    {
        title: "Filename",
        key: "filename",
        width: "40%"
    },
    {
        title: "Upload Time",
        key: "upload_time",
        width: "30%"
    }
  ];
  const analysis_methods = [
    'Repeated Measures ANOVA',
    'Univariate ANOVA',
    'Nonparametric (Kruskal-Wallis H Test, Mann-Whitney U Test)'
  ]
  const analysis_method_headers = [
    {
      title: "SPSS Export Sheet Name",
      key: "spss_export_sheet_name",
      width: '20%'
    },
    {
      title: "User Data Dependent Variable",
      key: "dpvar_name",
      width: '60%'
    },
    {
      title: "Analysis Method",
      key: "analysis_method",
      width: '20%'
    },
  ]

  // Hint Messages
  const set_project_name_hint_msg = ref(`Please enter a name for this project.`)

  const factor_hint_msg_base = `
Note: 
1. Between-subjects factor names must exactly match those used in User Data.
2. Within-subjects factor names must exactly match those used in SPSS Export.
3. Condition names must exactly match those used in User Data.

Example:
Between-subjects Factor  -   Condition
FactorA                  -   A1 Condition
FactorA                  -   A2 Condition
FactorB                  -   B1 Condition
...
Within-subjects Factor   -   Condition
FactorC                  -   C1 Condition
FactorC                  -   C2 Condition
FactorD                  -   D1 Condition
...
`
  const factor_hint_msg = ref(`Use the "+ pencil" button to create factor settings and apply them to new projects.\nYou can also use the "+" button to browse files or drag and drop files directly to upload them (Only JSON files are supported).\n${factor_hint_msg_base}`)
  const select_factor_hint_msg = ref(`Select a factor setting or use the '+' button to create new ones.\n${factor_hint_msg_base}`)

  const excel_file_handler_hint_msg = ref(`Use the '+' button to browse files or drag and drop files directly to upload (Only Excel files are supported).`)

  const select_user_data_hint_msg = `Please select the user data Excel file for this project. 
  
Note:
1. Each row should represent one user. 
2. The file must include all between-subjects factors as columns and the dependent variable data organized according to all within-subjects factor combinations.
3. In all data fields, the underscore character ('_') must be used exclusively as a separator between within-subjects conditions and dependent variable names (e.g. 'ConditionA1_ConditionB1_DependentVariable1').

If your user data Excel file does not follow this format, please modify the file and upload it again.
You can use the '+' button to browse files or drag and drop files directly to upload. Only Excel files are supported.`

  const select_spss_export_hint_msg = `Please select the SPSS export Excel file for this project.

Note:
1. Please ensure that each sheet corresponds to one SPSS analysis output for a single dependent variable.
2. Multiple sheets may contain SPSS analysis outputs for the same dependent variable. In this case, please ensure that these sheets are placed consecutively and are not separated by sheets for other dependent variables.`

  const select_user_data_sheet_hint_msg = `1. The table on the left displays all sheet names in the selected user data Excel file. Please select the sheets used in the SPSS analysis, then click Apply.
2. If the data is rejected, please modify the factors table on Page 2 based on the error messages displayed on the right, or select a different user data Excel file on Page 3.
3. If the data is accepted, you can review the table on the right and make the following adjustments:
\t(1) Modify the categories to improve the readability of the tables generated by this program.
\t(2) Hide dependent variables that were not used in the SPSS analysis.
\t(3) Reorder the sheets in the SPSS export Excel file to match the order of the dependent variables.
\t(4) If a dependent variable is analyzed multiple times and corresponds to multiple sheets in the SPSS export Excel file, adjust the number of analyses on the right. The corresponding sheets in the SPSS export Excel file must be arranged consecutively.`

  const select_analysis_method_hint_msg = `Please confirm that the dependent variables corresponding to the SPSS export sheet names are correct.
If any errors are found, please modify the SPSS export Excel file on Page 5 or adjust the dependent variables and the number of analyses used in the SPSS analysis on Page 4.`
  // Functions
  async function readJsonFile(filepath) {
    const filename = window.api.basename(filepath)

    try {
      let valid = filepath.endsWith('.json')
      let res

      if (valid) {
        res = await window.api.readJsonFile(filepath)
        const factor_res = parseJsonToFactor(res)

        if (factor_res.success) {
          await saveFactorGroup(factor_res.bs_items, factor_res.ws_items)
        }
        else {
          valid = false
        }
      }

      return {success: true, valid: valid, filename: filename}
    }
    catch (err) {
      console.error(err)
      return {success: false, valid: false, filename: filename}
    }
  }

  async function readJsonFiles(filepaths) {
    if (!filepaths || filepaths.length === 0) return null

    let result = []

    for (const filepath of filepaths) {
      const res = await readJsonFile(filepath)
      result.push(res)
    }

    return result
  }

  function isStringArrayObject(obj) {
    return obj !== null &&
           typeof obj === 'object' && 
           !Array.isArray(obj) &&
           Object.entries(obj).every(([key, value]) =>
             typeof key === 'string' && Array.isArray(value)
           )
  }

  function parseJsonToFactor(src_json) {
    const bs_key = Object.keys(src_json).find(key =>
      ['between', 'subject', 'factor'].every(word =>
        key.toLowerCase().includes(word)
      )
    )
    const ws_key = Object.keys(src_json).find(key =>
      ['within', 'subject', 'factor'].every(word =>
        key.toLowerCase().includes(word)
      )
    )

    let result = {success: false, bs_items: null, ws_items: null}

    if (bs_key && isStringArrayObject(src_json[bs_key])) {
      result.bs_items = Object.entries(src_json[bs_key])
        .flatMap(([factor, conditions]) =>
          conditions.map(condition => ({
            factor,
            condition
          }))
        )
      result.success = true
    }

    if (ws_key && isStringArrayObject(src_json[ws_key])) {
      result.ws_items = Object.entries(src_json[ws_key])
        .flatMap(([factor, conditions]) =>
          conditions.map(condition => ({
            factor,
            condition
          }))
        )
      result.success = true
    }

    return result
  }

  async function saveFactorGroup(bs_items, ws_items) {
    let bsFactorString = ''
    let wsFactorString = ''

    if (bs_items) {
      bsFactorString = Object.entries(
        bs_items.reduce((count, item) => {
            count[item.factor] = (count[item.factor] || 0) + 1
            return count
          }, {})
      )
      .map(([factor, count]) => `${count}${factor}`)
      .join(' x ')
    }
    if (ws_items) {
      wsFactorString = Object.entries(
        ws_items.reduce((count, item) => {
            count[item.factor] = (count[item.factor] || 0) + 1
            return count
          }, {})
      )
      .map(([factor, count]) => `${count}${factor}`)
      .join(' x ')
    }

    const title = [bsFactorString, wsFactorString].filter(Boolean).join(' x ')
    const between_subjects_factors = JSON.stringify(bs_items ?? [])
    const within_subjects_factors = JSON.stringify(ws_items ?? [])
    await window.api.addFactorGroup(title, between_subjects_factors, within_subjects_factors)
  }

  async function exportFactorGroup(bs_items, ws_items) {
    const bs_object = bs_items.reduce((acc, { factor, condition }) => {
      if (!acc[factor]) {
        acc[factor] = []
      }
      acc[factor].push(condition)

      return acc
    }, {})

    const ws_object = ws_items.reduce((acc, { factor, condition }) => {
      if (!acc[factor]) {
        acc[factor] = []
      }
      acc[factor].push(condition)

      return acc
    }, {})

    const factor = {
      [bs_headers[0].title]: bs_object,
      [ws_headers[0].title]: ws_object
    }

    await window.api.exportJson(factor)
  }

  async function exportExcelFile(filename, filepath) {
    await window.api.exportExcelFile(filename, filepath)
  }

  async function exportSignificantResult() {
    await window.api.exportExcelFile('Significant Results.xlsx')
  }

  async function uploadExcelFile(filepath, table_name) {
    const filename = window.api.basename(filepath)

    try {
      const valid = filepath.endsWith('.xlsx') || filepath.endsWith('.xls')

      if (valid) {
        await window.api.uploadFile(filepath, table_name)
      }

      return {success: true, valid: valid, filename: filename}
    }
    catch (err) {
      console.error(err)
      return {success: false, valid: false, filename: filename}
    }
  }

  async function uploadExcelFiles(filepaths, table_name) {
    if (!filepaths || filepaths.length === 0) return null

    let result = []

    for (const filepath of filepaths) {
      const res = await uploadExcelFile(filepath, table_name)
      result.push(res)
    }

    return result
  }

  return {
    // State
    is_dialog_opened,

    // Tables
    factor_headers, file_headers, project_headers,
    bs_headers, ws_headers,
    factor_headers_in_projects, file_headers_in_projects,
    analysis_methods, analysis_method_headers,

    // Hint Messages
    set_project_name_hint_msg,
    factor_hint_msg, select_factor_hint_msg,
    excel_file_handler_hint_msg,
    select_user_data_hint_msg,
    select_user_data_sheet_hint_msg,
    select_analysis_method_hint_msg,
    
    // Functions
    uploadExcelFile, uploadExcelFiles,
    readJsonFile, readJsonFiles,
    isStringArrayObject, parseJsonToFactor,
    saveFactorGroup, exportFactorGroup,
    exportExcelFile, exportSignificantResult
  }
})