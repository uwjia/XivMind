import { spawn, ChildProcess } from 'child_process'
import { app } from 'electron'
import http from 'http'
import { getBackendExePath, getLogsPath, getUserDataPath } from './paths'
import fs from 'fs'
import path from 'path'

let backendProcess: ChildProcess | null = null
let logStream: fs.WriteStream | null = null
let backendPid: number | null = null

const isDev = !app.isPackaged
const BACKEND_PORT = 8000
const BACKEND_HOST = 'localhost'

export function isBackendRunning(): boolean {
  return backendProcess !== null && !backendProcess.killed
}

export async function checkBackendHealth(timeout: number = 5000): Promise<boolean> {
  return new Promise((resolve) => {
    const options = {
      hostname: BACKEND_HOST,
      port: BACKEND_PORT,
      path: '/health',
      method: 'GET',
      timeout,
    }

    let resolved = false

    const req = http.request(options, (res) => {
      if (resolved) return
      resolved = true
      
      let data = ''
      res.on('data', chunk => data += chunk)
      res.on('end', () => {
        resolve(res.statusCode === 200)
      })
    })

    req.on('error', (err) => {
      if (resolved) return
      resolved = true
      console.log('Backend health check error:', err.message)
      resolve(false)
    })

    req.on('timeout', () => {
      if (resolved) return
      resolved = true
      req.destroy()
      resolve(false)
    })

    req.on('close', () => {
      if (!resolved) {
        resolved = true
        resolve(false)
      }
    })

    req.end()
  })
}

export async function waitForBackend(maxWaitMs: number = 30000): Promise<boolean> {
  const startTime = Date.now()
  const checkInterval = 500

  while (Date.now() - startTime < maxWaitMs) {
    const isHealthy = await checkBackendHealth()
    if (isHealthy) {
      return true
    }
    await new Promise(resolve => setTimeout(resolve, checkInterval))
  }

  return false
}

export async function startPythonBackend(): Promise<void> {
  if (isBackendRunning()) {
    console.log('Backend is already running')
    return
  }

  const backendExePath = getBackendExePath()
  
  if (!fs.existsSync(backendExePath)) {
    throw new Error(`Backend executable not found at: ${backendExePath}`)
  }

  const userDataPath = getUserDataPath()
  const logsPath = getLogsPath()
  
  const logFile = path.join(logsPath, 'backend.log')
  logStream = fs.createWriteStream(logFile, { flags: 'a' })

  const env = {
    ...process.env,
    DATABASE_TYPE: 'lancedb',
    LANCEDB_PATH: path.join(userDataPath, 'data', 'lancedb'),
    DOWNLOAD_DIR: path.join(userDataPath, 'downloads'),
    LOG_DIR: logsPath,
    LOG_FILE_ENABLED: 'true',
    LOG_CONSOLE_ENABLED: 'true',
    SKILLS_DIR: path.join(userDataPath, 'skills'),
    SUBAGENTS_DIR: path.join(userDataPath, 'subagents'),
  }

  console.log('Starting backend with environment:', {
    DATABASE_TYPE: env.DATABASE_TYPE,
    LANCEDB_PATH: env.LANCEDB_PATH,
    DOWNLOAD_DIR: env.DOWNLOAD_DIR,
  })

  backendProcess = spawn(backendExePath, [], {
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false,
  })

  backendPid = backendProcess.pid || null
  console.log('Backend process started with PID:', backendPid)

  backendProcess.stdout?.on('data', (data) => {
    try {
      const message = `[Backend stdout]: ${data.toString()}`
      console.log(message)
      logStream?.write(`${new Date().toISOString()} ${message}\n`)
    } catch (e) {
      console.error('Error writing stdout:', e)
    }
  })

  backendProcess.stderr?.on('data', (data) => {
    try {
      const message = `[Backend stderr]: ${data.toString()}`
      console.error(message)
      logStream?.write(`${new Date().toISOString()} ${message}\n`)
    } catch (e) {
      console.error('Error writing stderr:', e)
    }
  })

  backendProcess.on('error', (error) => {
    console.error('Backend process error:', error)
    logStream?.write(`${new Date().toISOString()} [ERROR]: ${error.message}\n`)
  })

  backendProcess.on('exit', (code, signal) => {
    console.log(`Backend process exited with code ${code}, signal ${signal}`)
    logStream?.write(`${new Date().toISOString()} Backend exited with code ${code}, signal ${signal}\n`)
    backendProcess = null
    backendPid = null
    if (logStream && !logStream.destroyed) {
      logStream.end()
      logStream = null
    }
  })

  console.log('Backend process started')
}

function killProcessTree(pid: number): void {
  if (process.platform === 'win32') {
    try {
      spawn('taskkill', ['/pid', String(pid), '/f', '/t'], {
        stdio: 'ignore',
        detached: true
      })
    } catch (e) {
      console.error('Failed to kill process tree:', e)
    }
  } else {
    try {
      process.kill(-pid, 'SIGKILL')
    } catch (e) {
      console.error('Failed to kill process group:', e)
    }
  }
}

export async function stopPythonBackend(): Promise<void> {
  if (!backendProcess || backendProcess.killed) {
    console.log('Backend is not running')
    return
  }

  const pid = backendPid
  console.log('Stopping backend process (PID:', pid, ')...')

  return new Promise((resolve) => {
    const process = backendProcess
    if (!process) {
      resolve()
      return
    }

    let resolved = false

    const cleanup = () => {
      if (resolved) return
      resolved = true
      backendProcess = null
      backendPid = null
      if (logStream && !logStream.destroyed) {
        logStream.end()
        logStream = null
      }
      console.log('Backend process stopped')
      resolve()
    }

    const forceKillTimeout = setTimeout(() => {
      console.log('Force killing backend process tree...')
      if (pid) {
        killProcessTree(pid)
      }
      setTimeout(cleanup, 500)
    }, 3000)

    process.once('exit', () => {
      clearTimeout(forceKillTimeout)
      cleanup()
    })

    try {
      process.kill('SIGTERM')
    } catch (e) {
      console.error('Error sending SIGTERM:', e)
      clearTimeout(forceKillTimeout)
      cleanup()
    }
  })
}

export function forceKillBackend(): void {
  const pid = backendPid
  
  if (backendProcess && !backendProcess.killed) {
    console.log('Force killing backend process (PID:', pid, ')...')
    try {
      if (pid) {
        killProcessTree(pid)
      } else {
        backendProcess.kill('SIGKILL')
      }
    } catch (e) {
      console.error('Error force killing backend:', e)
    }
    backendProcess = null
    backendPid = null
  }
  
  if (logStream && !logStream.destroyed) {
    logStream.end()
    logStream = null
  }
}
