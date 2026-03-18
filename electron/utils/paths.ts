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
  
  const envExampleDest = path.join(userDataPath, 'env.example')
  if (!fs.existsSync(envExampleDest)) {
    const envExampleSrc = path.join(getResourcesPath(), 'env.example')
    if (fs.existsSync(envExampleSrc)) {
      fs.copyFileSync(envExampleSrc, envExampleDest)
      console.log('Copied env.example to:', envExampleDest)
    }
  }
  
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

export function getEnvFilePath(): string {
  return path.join(getUserDataPath(), '.env')
}

export function getEnvExamplePath(): string {
  const userDataExample = path.join(getUserDataPath(), 'env.example')
  if (fs.existsSync(userDataExample)) {
    return userDataExample
  }
  return path.join(getResourcesPath(), 'env.example')
}
