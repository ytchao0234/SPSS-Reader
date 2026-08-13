const { table } = require('console')
const { contextBridge, ipcRenderer, webUtils, clipboard } = require('electron')
const fs = require('fs')
const path = require('path')
const { json } = require('stream/consumers')

contextBridge.exposeInMainWorld('api', {
  basename: (filepath) => path.basename(filepath),
  copyText: (text) => clipboard.writeText(text),
  checkForeignKey: () => ipcRenderer.invoke('check-foreign-key'),
  readJsonFile: (json_path) => ipcRenderer.invoke('read-json-file', json_path),
  exportJson: (json_data) => ipcRenderer.invoke('export-json', json_data),
  exportExcelFile: (filename, filepath) => ipcRenderer.invoke('export-excel-file', filename, filepath),

  // Home
  readMe: () => ipcRenderer.invoke('readme'),

  // Data/Factor
  getFactorGroups: () => ipcRenderer.invoke('get-factor-groups'),
  getFactorGroupById: (id) => ipcRenderer.invoke('get-factor-group-by-id', id),
  addFactorGroup: (title, bs_factor_items, ws_factor_items) => {
    return ipcRenderer.invoke('add-factor-group', title, bs_factor_items, ws_factor_items)
  },
  updateFactorGroup: (title, between_subjects_factors, within_subjects_factors, id) => {
    return ipcRenderer.invoke('update-factor-group', title, between_subjects_factors, within_subjects_factors, id)
  },
  deleteFactorGroupDependCount: (id) => ipcRenderer.invoke('delete-factor-group-depend-count', id),
  deleteFactorGroup: (id) => ipcRenderer.invoke('delete-factor-group', id),

  // Data/UserData, Data/SPSSExport
  getFilePath: (file) => {
    return webUtils.getPathForFile(file)
  },
  getFiles: (tableName) => ipcRenderer.invoke('get-files', tableName),
  getFileById: (tableName, id) => ipcRenderer.invoke('get-file-by-id', tableName, id),
  selectFile: () => ipcRenderer.invoke('select-file'),
  uploadFile: (filePath, tableName) => ipcRenderer.invoke('upload-file', filePath, tableName),
  deleteFileDependCount: (id, tableName) => ipcRenderer.invoke('delete-file-depend-count', tableName, id),
  deleteFile: (id, tableName) => ipcRenderer.invoke('delete-file', tableName, id),

  // Project
  getProjects: () => ipcRenderer.invoke('get-projects'),
  getProjectById: (id) => ipcRenderer.invoke('get-project-by-id', id),
  addProject: (project_name, factor_id, user_data_id, spss_export_id, dpvar_dict, method_dict) =>
    ipcRenderer.invoke('add-project', project_name, factor_id, user_data_id, spss_export_id, dpvar_dict, method_dict),
  updateProjectLastUsedTimeById: (id) => ipcRenderer.invoke('update-project-last-used-time-by-id', id),
  deleteProject: (id) => ipcRenderer.invoke('delete-project', id),

  // python
  runPython: (action, ...rest) => {
    return ipcRenderer.invoke('run-python', action, ...rest)
  }
})