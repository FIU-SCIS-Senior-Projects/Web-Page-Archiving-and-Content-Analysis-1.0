var app = require("electron").remote;
var dialog = app.dialog;
const { ipcRenderer } = require("electron");
const Store = require("electron-store");
const store = new Store("userprefs");

let preferred_viewer = store.get("preferred_viewer");
if (!preferred_viewer) {
  preferred_viewer = "internal";
}
let viewer_options = [
  {
    id: "intenral",
    label: "Internal"
  },
  {
    id: "external",
    label: "External"
  }
];

document.getElementById("view-wat").addEventListener(
  "click",
  () => {
    dialog.showOpenDialog(
      {
        filters: [
          { name: "wat files", extensions: ["wat"] },
          { name: "All Files", extensions: ["*"] }
        ]
      },
      function(fileNames) {
        if (fileNames === undefined) {
          console.log("No file selected");
        } else {
          console.log(fileNames[0]);
          ipcRenderer.send("openWAT", fileNames[0]);
        }
      }
    );
  },
  false
);

const preferred_mnt = document.getElementById("preferred-viewer-mnt");

const selectChange = event => {
  const new_pref = event.target.value;
  ipcRenderer.send("viewer-pref-change", new_pref);
  console.log("sent ipc event", new_pref);
};

const getPrefMarkup = (selected = "internal") => {
  const pref_markup = `
    <select id="pref-viewer-select">
      <option ${selected === "internal" ? "selected" : ""} value="internal">WATViewer App</option>
      <option ${selected === "external" ? "selected" : ""} value="external">My default browser</option>
    </select>
  `;

  return pref_markup;
};

preferred_mnt.innerHTML = getPrefMarkup(preferred_viewer);
const preferred_select = document.getElementById("pref-viewer-select");
preferred_select.addEventListener("change", selectChange);
