var rendererMD = new marked.Renderer();
marked.setOptions({
  renderer: rendererMD,
  gfm: true,
  tables: true,
  breaks: false,
  pedantic: false,
  sanitize: false,
  smartLists: true,
  smartypants: false
});//基本设置
var f = document.getElementById("form");
var xmlhttp;
if (window.XMLHttpRequest) {
  xmlhttp = new XMLHttpRequest();
} else {
  xmlhttp = new ActiveXObject('Microsoft.XMLHttp');
}

xmlhttp.onreadystatechange = () => {
if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
  var obj = document.getElementById('Markdown');
  obj.innerHTML = marked.marked(xmlhttp.responseText);
}
}
console.log(f.getAttribute('value'));
// 向服务器发送请求
xmlhttp.open('GET', f.getAttribute('value'), true);
xmlhttp.send();