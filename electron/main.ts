import { app, BrowserWindow, ipcMain, dialog, shell, Tray, Menu, nativeImage } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'
import http from 'http'
import { startPythonBackend, stopPythonBackend, isBackendRunning, waitForBackend, forceKillBackend, checkBackendHealth } from './utils/pythonProcess'
import { getUserDataPath, getBackendExePath, getResourcesPath } from './utils/paths'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason)
})

let mainWindow: BrowserWindow | null = null
let splashWindow: BrowserWindow | null = null
let tray: Tray | null = null
let isQuitting = false
let isCleaningUp = false
let splashReady = false

const isDev = !app.isPackaged
const QUIT_TIMEOUT = 10000

function createSplashWindow(): BrowserWindow {
  splashWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    center: true,
    backgroundColor: '#667eea',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          overflow: hidden;
        }
        .logo {
          width: 60px;
          height: 60px;
          margin-bottom: 20px;
        }
        .logo-icon {
          width: 100%;
          height: 100%;
        }
        .title {
          font-size: 24px;
          font-weight: 600;
          margin-bottom: 30px;
        }
        .progress-container {
          width: 280px;
          height: 6px;
          background: rgba(255,255,255,0.3);
          border-radius: 3px;
          overflow: hidden;
          margin-bottom: 15px;
        }
        .progress-bar {
          width: 0%;
          height: 100%;
          background: white;
          border-radius: 3px;
          transition: width 0.3s ease;
        }
        .status {
          font-size: 14px;
          opacity: 0.9;
        }
        .version {
          position: absolute;
          bottom: 15px;
          font-size: 12px;
          opacity: 0.7;
        }
      </style>
    </head>
    <body>
      <div class="logo">
        <svg viewBox="0 0 24 24" class="logo-icon">
          <path d="M12 2C12 2 4 8 4 14C4 20 8 22 12 22C16 22 20 20 20 14C20 8 12 2 12 2Z" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12 2V22" stroke="white" stroke-width="1" stroke-linecap="round"/>
          <path d="M12 14Q6 10 4.5 13" stroke="white" stroke-width="0.8" stroke-linecap="round" fill="none"/>
          <path d="M12 14Q18 10 19.5 13" stroke="white" stroke-width="0.8" stroke-linecap="round" fill="none"/>
        </svg>
      </div>
      <div class="title">XivMind</div>
      <div class="progress-container">
        <div class="progress-bar" id="progress"></div>
      </div>
      <div class="status" id="status">Initializing...</div>
      <div class="version">v${app.getVersion()}</div>
      <script>
        const { ipcRenderer } = require('electron');
        ipcRenderer.on('splash-progress', (event, data) => {
          document.getElementById('progress').style.width = data.progress + '%';
          document.getElementById('status').textContent = data.message;
        });
      </script>
    </body>
    </html>
  `

  splashWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(htmlContent))

  splashWindow.webContents.on('did-finish-load', () => {
    splashReady = true
    console.log('Splash window ready')
  })

  splashWindow.on('closed', () => {
    splashWindow = null
  })

  return splashWindow
}

function updateSplashProgress(progress: number, message: string): void {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.webContents.send('splash-progress', { progress, message })
  }
  console.log(`[Splash] ${progress}% - ${message}`)
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: 'XivMind',
    icon: path.join(getResourcesPath(), 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    show: false,
    autoHideMenuBar: true,
  })

  Menu.setApplicationMenu(null)

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    if (splashWindow) {
      splashWindow.close()
      splashWindow = null
    }
    mainWindow?.show()
  })

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault()
      mainWindow?.hide()
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function createTray(): void {
  let iconPath = path.join(getResourcesPath(), 'icon.png')
  
  if (!fs.existsSync(iconPath)) {
    iconPath = path.join(__dirname, '../resources/icon.png')
  }
  
  const icon = nativeImage.createFromPath(iconPath)
  
  if (icon.isEmpty()) {
    tray = new Tray(nativeImage.createEmpty())
  } else {
    tray = new Tray(icon.resize({ width: 16, height: 16 }))
  }
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Window',
      click: () => {
        mainWindow?.show()
        mainWindow?.focus()
      },
    },
    {
      label: 'Restart Backend',
      click: async () => {
        await stopPythonBackend()
        await startPythonBackend()
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true
        performQuit()
      },
    },
  ])
  
  tray.setToolTip('XivMind')
  tray.setContextMenu(contextMenu)
  
  tray.on('double-click', () => {
    mainWindow?.show()
    mainWindow?.focus()
  })
}

function forceQuit(): void {
  console.log('Force quit triggered')
  forceKillBackend()
  
  if (tray) {
    tray.destroy()
    tray = null
  }
  
  app.exit(0)
}

async function performQuit(): Promise<void> {
  if (isCleaningUp) {
    console.log('Already cleaning up, waiting...')
    return
  }
  
  isCleaningUp = true
  console.log('Starting quit process...')
  
  const forceQuitTimer = setTimeout(() => {
    console.log('Quit timeout reached, forcing exit')
    forceQuit()
  }, QUIT_TIMEOUT)

  try {
    if (!isDev) {
      console.log('Stopping Python backend...')
      await stopPythonBackend()
      console.log('Backend stopped successfully')
    }
  } catch (error) {
    console.error('Error during cleanup:', error)
    forceKillBackend()
  }

  clearTimeout(forceQuitTimer)

  if (tray) {
    tray.destroy()
    tray = null
  }

  console.log('Quit process completed')
  app.quit()
}

async function initializeApp(): Promise<void> {
  createSplashWindow()
  
  try {
    updateSplashProgress(10, 'Initializing application...')
    await new Promise(resolve => setTimeout(resolve, 200))
    
    const userDataPath = getUserDataPath()
    updateSplashProgress(20, 'Setting up data directories...')
    await new Promise(resolve => setTimeout(resolve, 200))
    
    if (!isDev) {
      updateSplashProgress(30, 'Starting backend service...')
      console.log('Starting Python backend...')
      await startPythonBackend()
      
      updateSplashProgress(50, 'Waiting for backend...')
      console.log('Waiting for backend to be ready...')
      
      const startTime = Date.now()
      const maxWait = 30000
      const checkInterval = 500
      
      while (Date.now() - startTime < maxWait) {
        const elapsed = Date.now() - startTime
        const progress = 50 + Math.min(40, (elapsed / maxWait) * 40)
        updateSplashProgress(Math.round(progress), 'Connecting to backend...')
        
        const isHealthy = await isBackendRunning()
        if (isHealthy) {
          const healthCheck = await checkBackendHealth()
          if (healthCheck) break
        }
        
        await new Promise(resolve => setTimeout(resolve, checkInterval))
      }
      
      const isReady = await waitForBackend(5000)
      
      if (!isReady) {
        updateSplashProgress(100, 'Failed to start backend')
        await new Promise(resolve => setTimeout(resolve, 1000))
        dialog.showErrorBox(
          'Startup Failed',
          'Failed to start backend service. Please check the log files.'
        )
        app.quit()
        return
      }
      
      updateSplashProgress(90, 'Backend ready')
      console.log('Backend is ready!')
    } else {
      updateSplashProgress(90, 'Development mode ready')
    }
    
    updateSplashProgress(95, 'Loading main window...')
    await new Promise(resolve => setTimeout(resolve, 200))
    
    createWindow()
    createTray()
    
    updateSplashProgress(100, 'Welcome to XivMind')
    
  } catch (error) {
    console.error('Failed to initialize app:', error)
    updateSplashProgress(100, 'Startup failed')
    await new Promise(resolve => setTimeout(resolve, 1000))
    dialog.showErrorBox(
      'Startup Error',
      `Application startup failed: ${error}`
    )
    app.quit()
  }
}

app.whenReady().then(initializeApp)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    isQuitting = true
    performQuit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  } else {
    mainWindow?.show()
  }
})

app.on('before-quit', (event) => {
  if (isQuitting) {
    return
  }
  
  event.preventDefault()
  isQuitting = true
  performQuit()
})

app.on('will-quit', () => {
  forceKillBackend()
  
  if (tray) {
    tray.destroy()
    tray = null
  }
})

ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

ipcMain.handle('get-user-data-path', () => {
  return getUserDataPath()
})

ipcMain.handle('open-external', async (_event, url: string) => {
  await shell.openExternal(url)
})

ipcMain.handle('show-item-in-folder', (_event, fullPath: string) => {
  shell.showItemInFolder(fullPath)
})

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory', 'createDirectory'],
  })
  
  if (result.canceled || result.filePaths.length === 0) {
    return null
  }
  
  return result.filePaths[0]
})

ipcMain.handle('backend-status', async () => {
  return isBackendRunning()
})

ipcMain.handle('restart-backend', async () => {
  await stopPythonBackend()
  await startPythonBackend()
  return waitForBackend(30000)
})
