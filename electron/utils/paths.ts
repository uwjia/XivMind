import { app } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const isDev = !app.isPackaged

export function getResourcesPath(): string {
  if (isDev) {
    return path.join(__dirname, '../../resources')
  }
  return process.resourcesPath
}

export function getBackendExePath(): string {
  const resourcesPath = getResourcesPath()
  return path.join(resourcesPath, 'backend', 'xivmind-backend.exe')
}

export function getUserDataPath(): string {
  const appDataPath = app.getPath('appData')
  const userDataPath = path.join(appDataPath, 'XivMind')
  
  if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true })
  }
  
  const subDirs = ['data', 'logs', 'config', 'downloads']
  subDirs.forEach(dir => {
    const dirPath = path.join(userDataPath, dir)
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true })
    }
  })
  
  return userDataPath
}

export function getDataPath(): string {
  return path.join(getUserDataPath(), 'data')
}

export function getLogsPath(): string {
  return path.join(getUserDataPath(), 'logs')
}

export function getConfigPath(): string {
  return path.join(getUserDataPath(), 'config')
}

export function getDownloadsPath(): string {
  return path.join(getUserDataPath(), 'downloads')
}

export function getLanceDBPath(): string {
  return path.join(getDataPath(), 'lancedb')
}
