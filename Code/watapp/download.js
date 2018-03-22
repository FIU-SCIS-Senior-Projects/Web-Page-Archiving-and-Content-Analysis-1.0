var app = require('electron').remote;
var dialog = app.dialog;
const {ipcRenderer} = require('electron');

document.getElementById('back-btn').addEventListener('click', (e) => {
  e.preventDefault();
  history.back();
});
var to_languages=["English","Russian"];
var from_languages=["Unknown", "English", "Russian"];
var to_select=document.getElementById('to');
var from_select=document.getElementById('from');
for(var i=0;i<to_languages.length;i++){
    var option = document.createElement("option");
    option.value=to_languages[i].toLowerCase()
    var textnode = document.createTextNode(to_languages[i]);
    option.appendChild(textnode);
    to_select.appendChild(option)
}
for(var i=0;i<from_languages.length;i++){
    var option = document.createElement("option");
    option.value=from_languages[i].toLowerCase()
    var textnode = document.createTextNode(from_languages[i]);
    option.appendChild(textnode);
    from_select.appendChild(option)
}

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
    console.log(output);
    var urlNum=output.slice(0,output.indexOf(" "))
    var button=document.createElement("button");
    button.innerHTML = "Open WAT &rarr;";
    button.addEventListener('click',()=>{
      ipcRenderer.send("openWAT",output.slice(output.indexOf(" ")));
    })
    document.getElementById("url-li-"+urlNum).appendChild(button);
  }else if(output.endsWith("URLS found")){
    console.log(output);
    var a = output.split(" ");
    var num = Number(a[a.length-3]);
    var ul=document.createElement("ul");

    for(var i =0; i < num; i++){
      var li=document.createElement("li");
      li.id="url-li-"+i;
      li.innerHTML=i+1 + " Downloading...";
      ul.appendChild(li)
    }
    document.getElementById('output').appendChild(ul);
  }else if(output.startsWith("Finished for URL")){
    console.log(output);
    a = output.split(" ");
    var urlNum = Number(a[3].slice(1,a[3].length-1))
    var li = document.getElementById("url-li-"+urlNum);
    a[3] = "#"+(urlNum+1)
    var textToShow =a.join(" ")
    li.innerHTML=textToShow;
  }else{
    var node = document.createElement("p");
    var textnode = document.createTextNode(`${output}`);
    node.appendChild(textnode);
    document.getElementById('output').appendChild(node);
    console.log(`${output}`);
  }
})
