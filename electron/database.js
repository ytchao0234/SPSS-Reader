const Database = require("better-sqlite3");
const path = require("path");
const { app } = require("electron");

const dbPath = path.join(
  app.getPath("userData"),
  "database.db"
);

const db = new Database(dbPath);
db.exec('PRAGMA foreign_keys = ON');

// factor
db.prepare(`
CREATE TABLE IF NOT EXISTS factor (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  between_subjects_factors TEXT,
  within_subjects_factors TEXT,
  created_time TEXT NOT NULL
)
`).run();

// user_data
db.prepare(`
CREATE TABLE IF NOT EXISTS user_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  stored_name TEXT NOT NULL,
  filepath TEXT NOT NULL,
  upload_time TEXT NOT NULL
)
`).run();


// spss export
db.prepare(`
CREATE TABLE IF NOT EXISTS spss_export (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  stored_name TEXT NOT NULL,
  filepath TEXT NOT NULL,
  upload_time TEXT NOT NULL
)
`).run();

db.prepare(`
CREATE TABLE IF NOT EXISTS project (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name TEXT NOT NULL,

  factor_id INTEGER NOT NULL,
  user_data_id INTEGER NOT NULL,
  spss_export_id INTEGER NOT NULL,

  dependent_variables TEXT,
  analysis_methods TEXT,

  created_time TEXT NOT NULL,
  last_used_time TEXT NOT NULL,

  FOREIGN KEY (factor_id)
    REFERENCES factor(id)
    ON DELETE CASCADE,

  FOREIGN KEY (user_data_id)
    REFERENCES user_data(id)
    ON DELETE CASCADE,

  FOREIGN KEY (spss_export_id)
    REFERENCES spss_export(id)
    ON DELETE CASCADE
)
`).run();

module.exports = db;