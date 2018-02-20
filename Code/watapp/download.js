var app = require('electron').remote;
var dialog = app.dialog;
const {ipcRenderer} = require('electron');

document.getElementById('get-url-file').addEventListener('click',()=>{
  dialog.showOpenDialog({
    filters: [
        {name: 'Text files', extensions: ['txt']},
        {name: 'All Files', extensions: ['*']}
      ]
    },function (fileNames) {
      if(fileNames === undefined){
        console.log('No file selected');
      }else{
        console.log(fileNames[0]);
        document.getElementById('url-file').value = fileNames[0];
      }
    });
  },false);


document.getElementById('select-outdir').addEventListener('click',()=>{
  dialog.showOpenDialog({
    properties:['openDirectory']
    },function (fileNames) {
      if(fileNames === undefined){
        console.log('No file selected');
      }else{
        console.log(fileNames[0]);
        document.getElementById('outdir').value = fileNames[0];
      }
    });
  },false);

  document.getElementById('download').addEventListener('click',()=>{
      downloadOptions = {
        filename: document.getElementById('url-file').value,
        outdir: document.getElementById('outdir').value,
        rateLimit: document.getElementById('rate-limit').value,
        videos: document.getElementById('videos').value,
        threads: document.getElementById('threads').value
      }
      ipcRenderer.send('download', downloadOptions);
  },false);
