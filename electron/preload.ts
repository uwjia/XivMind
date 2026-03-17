import { contextBridge, ipcRenderer } from 'electron'

export interface ElectronAPI {
  getAppVersion: () => Promise<string>
  getUserDataPath: () => Promise<string>
  openExternal: (url: string) => Promise<void>
  showItemInFolder: (fullPath: string) => void
  selectDirectory: () => Promise<string | null>
  backendStatus: () => Promise<boolean>
  restartBackend: () => Promise<boolean>
  platform: NodeJS.Platform
  onSplashProgress: (callback: (data: { progress: number; message: string }) => void) => () => void
}

const electronAPI: ElectronAPI = {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  showItemInFolder: (fullPath) => ipcRenderer.send('show-item-in-folder', fullPath),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  backendStatus: () => ipcRenderer.invoke('backend-status'),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  platform: process.platform,
  onSplashProgress: (callback) => {
    const handler = (_event: Electron.IpcRendererEvent, data: { progress: number; message: string }) => {
      callback(data)
    }
    ipcRenderer.on('splash-progress', handler)
    return () => ipcRenderer.removeListener('splash-progress', handler)
  },
}

contextBridge.exposeInMainWorld('electronAPI', electronAPI)
