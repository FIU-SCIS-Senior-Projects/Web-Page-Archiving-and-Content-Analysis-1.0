const electron = require("electron");
const unzip = require("unzip");
var DecompressZip = require("decompress-zip");
const fs = require("fs");
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

const temp_dest = os.tmpdir();

function unzip_wat(file) {
  devToolsLog(temp_dest);
  // var unzipper = unzip.Extract({ path: temp_dest })
  // fs.createReadStream(file).pipe(unzipper);
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

function getWatLink(dir) {
  var url = fs.readFileSync(path.join(dir, "wat_link.txt"));
  return url.toString();
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

function openWAT(opened_file) {
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
    let dest_file = getWatLink(fileLocation);
    console.log(dest_file);

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
  mainWindow = new BrowserWindow({ width: 800, height: 600 });
  // mainWindow.webContents.openDevTools();
  if (opened_file && opened_file != ".") {
    devToolsLog(opened_file);
    mainWindow.maximize();
    openWAT(opened_file);
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
  openWAT(file);
});

ipcMain.on("download", (event, downloadOptions) => {
  const script = path.join(process.resourcesPath, "CLI", "wat.py");
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

  const downloader = spawn("python", optionsArray);

  downloader.stdout.on("data", data => {
    data = String(data).split("\n");
    console.log(`stdout: ${data}`);
    for (var i = 0; i < data.length; i++) {
      if (data[i].startsWith("Finished for URL")) {
        event.sender.send("downloadOutput", data[i]);
      } else if (data[i].endsWith("URLS found")) {
        event.sender.send("downloadOutput", data[i]);
      } else if (data[i].startsWith("It can be found at ")) {
        event.sender.send(
          "downloadOutput",
          data[i].substr("It can be found at ".length)
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

ipcMain.on("viewer-pref-change", (event, preference) => {
  if (preferred_viewer !== preference) {
    preferred_viewer = preference;
    store.set("preferred_viewer", preference);
  }
});
