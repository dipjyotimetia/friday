const { app, BrowserWindow } = require('electron')
const { updateElectronApp, UpdateSourceType } = require('update-electron-app')
updateElectronApp({
  updateSource: {
    host: 'https://github.com',
    repo: 'dipjyotimetia/friday',
    type: UpdateSourceType.ElectronPublicUpdateService,
  },
  logger: require('electron-log'),
  updateInterval: '1 hour',
  notifyUser: true,
})

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  })

  win.loadFile('index.html')
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