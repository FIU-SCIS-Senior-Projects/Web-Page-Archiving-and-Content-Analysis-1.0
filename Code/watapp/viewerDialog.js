var app = require('electron').remote;
var dialog = app.dialog;
const {ipcRenderer} = require('electron');

document.getElementById('view-wat').addEventListener('click',()=>{
  dialog.showOpenDialog({
    filters: [
        {name: 'wat files', extensions: ['wat']},
        {name: 'All Files', extensions: ['*']}
      ]
    },function (fileNames) {
      if(fileNames === undefined){
        console.log("No file selected");
      }else{
        console.log(fileNames[0]);
        ipcRenderer.send("openWAT",fileNames[0])
      }
    });
  },false);
