var app = require('electron').remote;
var dialog = app.dialog;
const {ipcRenderer} = require('electron');

document.getElementById('back-btn').addEventListener('click', (e) => {
  e.preventDefault();
  history.back();
});

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

document.getElementById('translate').addEventListener('click',()=>{
  document.getElementById('languages').hidden=!document.getElementById('languages').hidden;
},false);

  document.getElementById('download').addEventListener('click',()=>{
      if(!document.getElementById('url-file').value){
        alert("Please provide a file with a list of URLs");
      }else if(!document.getElementById('outdir').value){
        alert("Please specify an output directory")
      }else{
        downloadOptions = {
          filename: document.getElementById('url-file').value,
          outdir: document.getElementById('outdir').value,
          rateLimit: document.getElementById('rate-limit').value,
          videos: document.getElementById('videos').value,
          threads: document.getElementById('threads').value
        }
        ipcRenderer.send('download', downloadOptions);
      }
  },false);
ipcRenderer.on('downloadOutput', (event, output) => {
  //var output = str(output).trim();
  console.log("last 4: " + output.slice(-4));
  if(output.slice(-4)==".wat"){
    //        ipcRenderer.send("openWAT",output)
    var button=document.createElement("button");
    button.innerHTML = "Open WAT &rarr;";
    button.addEventListener('click',()=>{
      ipcRenderer.send("openWAT",output);
    })
    document.getElementById('output').appendChild(button);
  }else{
    var node = document.createElement("p");
    var textnode = document.createTextNode(`${output}`);
    node.appendChild(textnode);
    document.getElementById('output').appendChild(node);
    console.log(`${output}`);
  }
})
