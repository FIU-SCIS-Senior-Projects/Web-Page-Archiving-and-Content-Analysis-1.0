const electron = require("electron");
const unzip = require("unzip");
const fs = require("fs");
const fstream = require("fstream");
const os = require("os");
// Module to control application life.
const app = electron.app;
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow;
const protocol = electron.protocol;

const PROTOCOL_STRING = "watapp://";
const PROTOCOL_PREFIX = PROTOCOL_STRING.split(":")[0];

const path = require("path");
const url = require("url");

let opened_file = process.argv[1];

function unzip_wat(file) {

  var temp_dest = os.tmpdir();
  devToolsLog(temp_dest);
  fs.createReadStream(file).pipe(unzip.Extract({ path: temp_dest }));

  return temp_dest
}

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow;

// app.on("open-url", (event, url) => {
//   devToolsLog(url);
// });

app.on("open-file", (event, path) => {
  opened_file = path;
});

function devToolsLog(s) {
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.executeJavaScript(`console.log("${s}")`);
  }
}

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({ width: 800, height: 600 });
  mainWindow.webContents.openDevTools();

  devToolsLog(opened_file);
  let temp_dest = unzip_wat(opened_file);

  protocol.registerFileProtocol(
    "wat",
    (req, cb) => {
      devToolsLog("Register file protocol", req.url);
      cb({ path: path.join(__dirname, "index.html") });
    },
    error => {
      if (error) {
        console.error("Something went wrong");
      }
    }
  );

  protocol.registerHttpProtocol(
    PROTOCOL_PREFIX,
    (req, callback) => {
      const reqUrl = req.url;
      devToolsLog(req);
      console.log(req);
      devToolsLog(`Received url: ${reqUrl}`);
      // and load the index.html of the app.
      callback({
        url: path.join(__dirname, "index.html"),
        method: "GET"
      });
    },
    err => {
      if (!err) {
        devToolsLog("registered watapp protocol");
      } else {
        console.error("couldn't register protocol");
        console.error(err);
      }
    }
  );

  mainWindow.loadURL(
    url.format({
      // pathname: path.join(__dirname, "index.html"),
      pathname: path.join(temp_dest, "/testfile/index.html"),
      protocol: "file:",
      slashes: true
    })
  );

  // Emitted when the window is closed.
  mainWindow.on("closed", function() {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null;
  });
}

function appReady() {
  createWindow();
  // unzip_wat(opened_file);
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on("ready", appReady);

// Quit when all windows are closed.
app.on("window-all-closed", function() {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", function() {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
