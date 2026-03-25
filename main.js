const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 800,
    webPreferences: {
      nodeIntegration: true, // Permite usar módulos de red como 'net' [cite: 502]
      contextIsolation: false 
    }
  });

  mainWindow.loadFile('index.html'); // Carga la interfaz visual [cite: 515]
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});