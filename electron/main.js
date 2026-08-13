const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs');
const db = require("./database.js");
const { execSync, spawn } = require('child_process')
const { randomUUID } = require('crypto');
const { json } = require('stream/consumers');

let mainWindow
const cache_path = path.join(
  app.getPath('userData'),
  'cache'
)

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // mainWindow.webContents.on('did-finish-load', () => {
  //   mainWindow.webContents.openDevTools()
  // })

  if (app.isPackaged) {
    const target = path.join(process.resourcesPath, 'dist', 'index.html')
    mainWindow.loadFile(target) 
  } else {
    mainWindow.loadURL('http://localhost:5173')
  }
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

ipcMain.handle('check-foreign-key', () => {
  return db.prepare('PRAGMA foreign_keys').get()
})

ipcMain.handle("readme", () => {
  let readmePath
  if (app.isPackaged) {
    readmePath = path.join(process.resourcesPath, 'README.md')
  }
  else {
    readmePath = path.join(__dirname, '../README.md')
  }

  if (!fs.existsSync(readmePath)) {
    throw new Error(`README.md not found: ${readmePath}`)
  }

  return fs.readFileSync(
    readmePath,
    'utf-8'
  )
})

ipcMain.handle('read-json-file', (event, json_path) => {
  return JSON.parse(
    fs.readFileSync(json_path, 'utf8')
  )
})

ipcMain.handle('export-json', async (event, data) => {
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Save JSON File',
    defaultPath: 'Factor.json',
    filters: [
      {
        name: 'JSON File',
        extensions: ['json']
      }
    ]
  })

  if (canceled) return false

  fs.writeFileSync(
    filePath,
    JSON.stringify(data, null, 2),
    'utf8'
  )

  return true
})

ipcMain.handle("get-factor-groups", () => {
  return db.prepare(`
    SELECT * FROM factor ORDER BY created_time DESC
  `)
  .all();
})

ipcMain.handle("get-factor-group-by-id", (event, id) => {
  if (!id) return null

  const result = db.prepare(`
    SELECT * FROM factor WHERE id = ?
  `).get(id)

  return result || null
})

ipcMain.handle("add-factor-group", (event, title, bs_factor_items, ws_factor_items) => {
  const now = new Date()
  const localTime = 
    `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ` +
    `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

  db.prepare(`
  INSERT INTO factor
    (title, between_subjects_factors, within_subjects_factors, created_time)
    VALUES (?, ?, ?, ?)
  `)
  .run(title, bs_factor_items, ws_factor_items, localTime);
})

ipcMain.handle("update-factor-group", (event, title, between_subjects_factors, within_subjects_factors, id) => {
  const result = db.prepare(`
    UPDATE factor SET
      title = ?,
      between_subjects_factors = ?,
      within_subjects_factors = ?
    WHERE id = ?
  `).run(
    title,
    between_subjects_factors,
    within_subjects_factors,
    id
  )
  return result.changes > 0
})

ipcMain.handle("delete-factor-group-depend-count", (event, id) => {
  return db.prepare(`
    SELECT COUNT(*) AS cnt FROM project WHERE factor_id = ?
  `)
  .get(id).cnt;
})

ipcMain.handle("delete-factor-group", (event, id) => {
  db.prepare(`
    DELETE FROM factor WHERE id = ?
  `)
  .run(id);
})

ipcMain.handle("get-files", (event, tableName)=>{
  const allowedTables = [
    "user_data",
    "spss_export"
  ];

  if (!allowedTables.includes(tableName)) {
    throw new Error("Invalid table name");
  }

  return db.prepare(`
    SELECT * FROM ${tableName} ORDER BY upload_time DESC
  `)
  .all();
});

ipcMain.handle("get-file-by-id", (event, tableName, id)=>{
  if (!id) return null

  const allowedTables = [
    "user_data",
    "spss_export"
  ];

  if (!allowedTables.includes(tableName)) {
    throw new Error("Invalid table name");
  }

  const result = db.prepare(`
    SELECT * FROM ${tableName} WHERE id = ?
  `).get(id)

  return result || null;
});

ipcMain.handle("select-file", async ()=>{
  const result =
  await dialog.showOpenDialog(mainWindow, {
    properties:["openFile"],
    // filters: [
    //   { name: 'Excel', extensions: ['xlsx', 'xls'] }
    // ]
  });

  if(result.canceled)
      return;

  return result.filePaths[0];
})

ipcMain.handle("upload-file", (event, originalPath, tableName) => {
  const allowedTables = [
    "user_data",
    "spss_export"
  ];

  if (!allowedTables.includes(tableName)) {
    throw new Error("Invalid table name");
  }

  const filename = path.basename(originalPath);
  const uploadDir = path.join(
    app.getPath("userData"),
    "uploads"
  );

  if(!fs.existsSync(uploadDir)){
      fs.mkdirSync(uploadDir);
  }

  const ext = path.extname(filename)
  const storedName = `${randomUUID()}${ext}`
  const newPath = path.join(uploadDir, storedName);
  fs.copyFileSync(originalPath, newPath);

  const now = new Date()
  const localTime = 
    `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ` +
    `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

  db.prepare(`
  INSERT INTO ${tableName}
    (filename, stored_name, filepath, upload_time)
    VALUES (?, ?, ?, ?)
  `)
  .run(filename, storedName, newPath, localTime);

  return true;
});

ipcMain.handle("delete-file-depend-count", (event, tableName, id) => {
  const allowedTables = [
    "user_data",
    "spss_export"
  ];

  if (!allowedTables.includes(tableName)) {
    throw new Error("Invalid table name");
  }

  return db.prepare(`
    SELECT COUNT(*) AS cnt FROM project WHERE ${tableName}_id = ?
  `)
  .get(id).cnt;
})

ipcMain.handle("delete-file", (event, tableName, id) => {
  const allowedTables = [
    "user_data",
    "spss_export"
  ];

  if (!allowedTables.includes(tableName)) {
    throw new Error("Invalid table name");
  }

  const file = db.prepare(`
    SELECT filepath FROM ${tableName} WHERE id = ?
  `)
  .get(id);

  if (!file) {
    return false;
  }

  if (fs.existsSync(file.filepath)) {
    fs.unlinkSync(file.filepath);
  }

  db.prepare(`
    DELETE FROM ${tableName} WHERE id = ?
  `)
  .run(id);

  return true;
});

ipcMain.handle('export-excel-file', async (event, filename, src_filepath) => {
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Export Excel File',
    defaultPath: filename,
    filters: [
      {
        name: 'Excel Workbook',
        extensions: ['xlsx']
      }
    ]
  })

  if (canceled) return false

  let source_path

  if (src_filepath) {
    source_path = src_filepath
  }
  else {
    source_path = path.join(
      cache_path,
      'result.xlsx'
    )
  }

  if (fs.existsSync(source_path)) {
    fs.copyFileSync(source_path, filePath)
    return true
  }

  return false
})

ipcMain.handle("get-projects", () => {
  return db.prepare(`
    SELECT * FROM project ORDER BY last_used_time DESC
  `)
  .all();
})

ipcMain.handle("get-project-by-id", (event, id)=>{
  if (!id) return null

  const result = db.prepare(`
    SELECT * FROM project WHERE id = ?
  `).get(id)

  return result || null;
});

ipcMain.handle("update-project-last-used-time-by-id", (event, id)=>{
  if (!id) return null

  const now = new Date()
  const localTime = 
    `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ` +
    `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

  const result = db.prepare(`
    UPDATE project
    SET last_used_time = ?
    WHERE id = ?
  `)
  .run(localTime, id)

  return result.changes > 0;
});

ipcMain.handle("add-project", (event, project_name, factor_id, user_data_id, spss_export_id, dpvar_dict, method_dict) => {
  const now = new Date()
  const localTime = 
    `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ` +
    `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

  const result = db.prepare(`
    INSERT INTO project (
      project_name,
      factor_id, user_data_id, spss_export_id,
      dependent_variables, analysis_methods,
      created_time, last_used_time
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `)
  .run(
    project_name,
    factor_id, user_data_id, spss_export_id,
    dpvar_dict, method_dict, 
    localTime, localTime
  );

  const project_id = result.lastInsertRowid;
  return project_id;
});

ipcMain.handle("delete-project", (event, id) => {
  db.prepare(`
    DELETE FROM project WHERE id = ?
  `)
  .run(id);
})

ipcMain.handle('run-python', (event, action, ...rest) => {
  return new Promise((resolve, reject) => {
    if(!fs.existsSync(cache_path)){
        fs.mkdirSync(cache_path);
    }

    let command
    let args

    if (app.isPackaged) {
      command = path.join(
        process.resourcesPath,
        'python',
        'analyzer',
        process.platform === 'win32'
          ? 'analyzer.exe'
          : 'analyzer'
      )
      args = [action, cache_path, ...rest]
    }
    else {
      command = 'pipenv'

      args = [
        'run', 'python',
        path.join(__dirname, 'python/analyzer.py'),
        action, cache_path, ...rest
      ]
    }

    const py = spawn(command, args, {
      cwd: path.dirname(command)
    })

    py.on('error', (err) => {
      reject(err)
    })

    py.stdout.on('data', (data) => {
      // ignore
    })

    py.stderr.on('data', (err) => {
      reject(err)
    })

    py.on('close', (code) => {
      if (code === 0) {
        const result = fs.readFileSync(path.join(
            cache_path,
            'result.json'
          ), 
          'utf8'
        )
  
        resolve(result)
      }
      else {
        reject(new Error(`Python process exited with code ${code}`))
      }
    })
  })
})