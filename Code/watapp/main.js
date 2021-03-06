const electron = require("electron");
var DecompressZip = require("decompress-zip");
const fs = require('fs-extra')
const fstream = require("fstream");
const os = require("os");
// Module to control application life.
const app = electron.app;
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow;
const protocol = electron.protocol;
const { ipcMain } = require("electron");
const { spawn } = require("child_process");

const Store = require("electron-store");
const store = new Store("userprefs");
let preferred_viewer = store.get("preferred_viewer");
if (!preferred_viewer) {
  preferred_viewer = "internal";
}

const PROTOCOL_STRING = "watapp://";
const PROTOCOL_PREFIX = PROTOCOL_STRING.split(":")[0];

const path = require("path");
const url = require("url");

let opened_file = process.argv[1];

const temp_dest = path.join(os.tmpdir(),'Web Archive');
const electronLocalshortcut = require('electron-localshortcut');
let extractLocation;
/*
This function is asynchronous due to the DecompressZip module
It returns the unzipper and that unzipper has event handlers for when it finishes, errors or makes progress
*/
function unzip_wat(file) {
  devToolsLog(temp_dest);
  var unzipper = new DecompressZip(file);
  unzipper.extract({
    path: temp_dest,
    filter: function(file) {
      return file.type !== "SymbolicLink";
    }
  });
  console.log(file);
  return unzipper;
}

function getWatLink_v1(dir) {
  var url = fs.readFileSync(path.join(dir, "wat_link.txt"));
  return url.toString();
}

function getWatLink_v2(dir) {
  var wat_json = JSON.parse(fs.readFileSync(path.join(dir, "wat.json")));
  return wat_json.index;
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

// unzips wat to temp, determines main html, renders in preferred viewer
function openWAT_v2(opened_file) {
  const watfile_path = opened_file.split("/");
  const full_filename = watfile_path[watfile_path.length - 1]; // file.wat
  const filename = full_filename.substr(0, full_filename.indexOf(".wat"));

  let unzipper = unzip_wat(opened_file);
  unzipper.on("error", function(err) {
    console.log("Caught an error");
    console.log(err);
  });
  unzipper.on("extract", e => {
    var fileLocation;
    console.log(e);
    if (fs.existsSync(path.join(temp_dest, `${filename}`))) {
      fileLocation = path.join(temp_dest, `${filename}`);
    } else {
      fileLocation = temp_dest;
    }
    console.log(fileLocation);
    let destfile;
    if (fs.existsSync(path.join(fileLocation,"wat_link.txt"))) {
      dest_file = getWatLink_v1(fileLocation);
    }else if (fs.existsSync(path.join(fileLocation,"wat.json"))) {
      dest_file = path.join("files",getWatLink_v2(fileLocation));
    }
    console.log(dest_file);
    extractLocation= path.join(fileLocation,"extraction","meta.json")

    let url_to_load = url.format({
      pathname: path.join(fileLocation, `${dest_file}`),
      protocol: "file:",
      slashes: true
    });
    if (preferred_viewer == "external") {
      electron.shell.openExternal(url_to_load);
    } else {
      mainWindow.loadURL(url.format(url_to_load));
    }
  });
}

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({ width: 1140, height: 800, icon: path.join(__dirname, 'assets/icons/png/64x64.png') });
  // mainWindow.webContents.openDevTools();
  if (opened_file && opened_file != ".") { // If app opened with argument (either command line or double clicked)
    devToolsLog(opened_file);
    mainWindow.maximize();
    openWAT_v2(opened_file);
    if(preferred_viewer=="external"){
      mainWindow.loadURL(
        url.format({
          pathname: path.join(__dirname, "index.html"),
          protocol: "file:",
          slashes: true
        })
      );
    }
  } else {
    mainWindow.loadURL(
      url.format({
        pathname: path.join(__dirname, "index.html"),
        protocol: "file:",
        slashes: true
      })
    );
  }

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

  // Emitted when the window is closed.
  mainWindow.on("closed", function() {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null;
    //cleaning up temp directory
    if (fs.existsSync(temp_dest)) {
      fs.removeSync(temp_dest);
    }
  });
  electronLocalshortcut.register(mainWindow, 'Alt+Left', () => {
      mainWindow.webContents.goBack();
  });
  electronLocalshortcut.register(mainWindow, 'Alt+U', () => {
      mainWindow.loadURL(
        url.format({
          pathname: extractLocation,
          protocol: "file:",
          slashes: true
        })
      );
  });
}

function appReady() {
  console.log("onReady", preferred_viewer);
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
ipcMain.on("openWAT", (event, file) => {
  if (preferred_viewer == "internal") {
    mainWindow.maximize();
  }
  openWAT_v2(file);
});

// When other process sends download message
ipcMain.on("download", (event, downloadOptions) => {
  var noPython=true;
  let script;
  if(noPython){
    script = ""
  }else{
    script = path.join(process.resourcesPath, "CLI", "wat.py");
  }
  // const script = path.join("../", "CLI", "wat.py");
  var optionsArray = [
    script,
    "-f",
    downloadOptions.filename,
    "-d",
    downloadOptions.outdir,
    "-m",
    downloadOptions.threads
  ];
  if (downloadOptions.rateLimit) {
    optionsArray.push("--rate-limit=" + downloadOptions.rateLimit);
  }
  if (downloadOptions.videos) {
    optionsArray.push("--videos");
  }
  event.sender.send("downloadOutput", "Beginning download");
  let downloader;
  if(noPython){
    downloader = spawn(path.join(process.resourcesPath, "CLIBuild", "wat"), optionsArray.slice(1));
  }else{
    downloader = spawn("python", optionsArray);
  }

  downloader.stdout.on("data", data => { // Send data based on console output of download
    data = String(data).split("\n");
    console.log(`stdout: ${data}`);
    for (var i = 0; i < data.length; i++) {
      if (data[i].startsWith("Finished for URL")) {
        event.sender.send("downloadOutput", data[i]);
      }else if (data[i].startsWith("Downloading URL #")) {
        event.sender.send("downloadOutput", data[i]);
      } else if (data[i].endsWith("URLS found")) {
        event.sender.send("downloadOutput", data[i]);
      } else if (data[i].includes("can be found at ")) {
        event.sender.send(
          "downloadOutput",
          data[i].slice(data[i].indexOf("#")+1, data[i].indexOf(":")) + " " + data[i].substr(data[i].indexOf("can be found at ")+ "can be found at ".length)
        );
      }
    }
  });

  downloader.stderr.on("data", data => {
    console.log(`stderr: ${data}`);
  });

  downloader.on("close", code => {
    console.log(`child process exited with code ${code}`);
    event.sender.send("downloadOutput", `Finished download with code ${code}`);
  });
});

// Handle user preference of viewer
ipcMain.on("viewer-pref-change", (event, preference) => {
  if (preferred_viewer !== preference) {
    preferred_viewer = preference;
    store.set("preferred_viewer", preference);
  }
});
