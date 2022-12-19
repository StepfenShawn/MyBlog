var db = openDatabase('mydb', '1.0', 'Myblog', 2 * 1024 * 1024);
/**
 * 创建表
 */
function dp_create() {
  db.transaction(function (tx) {
    tx.executeSql('CREATE TABLE IF NOT EXISTS BLOGS (date, url, title)');
  });
}

/**
 * 从表中插入数据
 * @param {String} e_date : 博客日期
 * @param {String} e_url  : 博客地址
 * @param {String} e_title : 博客标题
 * @param {String} e_category : 博客分类
 */
function insert(e_date, e_url, e_title, e_category) {
  db.transaction(function (tx) {
    tx.executeSql('INSERT INTO BLOGS VALUES (?, ?, ?, ?)', [e_date, e_url, e_title, e_category]);
  });
}

/**
 * 查询所有数据
 */
function query_all() {
  result = [];
  db.transaction(function (tx) {
    tx.executeSql('SELECT * FROM BLOGS', [], function (tx, results) {
      var len = results.rows.length;
      for (var i = 0; i < len; i++) {
        result.append(results.rows.item(i));
      }
    }, null);
  });
  return result;
}

/**
 * 创建索引, 快速查询
 */
function create_index() {
  db.transaction(function (tx) {
    tx.executeSql('CREATE INDEX DATE_INDEX');
    tx.executeSql('CREATE INDEX CATEGORY_INDEX');
  });
}
dp_create();
/**
 * TODO : auto insert after create markdown file
 */
insert("2022/11/30", "2022/11/30/hello-world.md", "Hello World", "test");

// query_all();

// Markdown parser
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

function ajax_parser() {
  var f = document.getElementById("form");
  var xmlhttp;
  if (window.XMLHttpRequest) {
    xmlhttp = new XMLHttpRequest();
  } else {
    xmlhttp = new ActiveXObject('Microsoft.XMLHttp');
  }

  console.log(f.getAttribute('value'));
  // 向服务器发送请求
  xmlhttp.open('GET', f.getAttribute('value'), true);
  xmlhttp.send();
  xmlhttp.onreadystatechange = () => {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      var obj = document.getElementById('Markdown');
      obj.innerHTML = marked.marked(xmlhttp.responseText);
    }
  }
}

/**
 * TODO: query in sql
 * @param {*} category 
 */
function change_ctx_by_category(category) {
  var article_list = document.getElementById("article-link-list");
  var html = "";
  switch (category) {
    case "asm":
      html += "<a href=\"javascript:change_ctx_by_name('archives/asm/note1');\">汇编语言学习笔记(一):内存与字节</a><br>";
      html += "<a href=\"javascript:change_ctx_by_name('archives/asm/note2');\">汇编语言学习笔记(二):Intel 8086cpu的通用寄存器</a><br>";
      html += "<a href=\"javascript:change_ctx_by_name('archives/asm/note3');\">汇编语言学习笔记(三):8086地址内存分配</a>";
      break;
    case "Information_theory":
      html +=  "<a href=\"javascript:change_ctx_by_name('archives/Information_Theory/note1');\">信息论学习笔记(一):认识通信系统</a><br>";
      html +=  "<a href=\"javascript:change_ctx_by_name('archives/Information_Theory/note2');\">信息论学习笔记(二):离散无噪声系统</a><br>";
      break;
    case "algo":
      html += "<a href=\"javascript:change_ctx_by_name('archives/algo/Euclidean');\">深入算法:从0开始证明欧几里得算法</a><br>";
      break;
  }
  article_list.innerHTML = html;
}

// TODO
function change_ctx_by_month(months) {
  /**
   * 
  <div id="Markdown">
  </div>
  <!--创建表单-->
  <form id = "form" action="" method="post" value = "hello-world.md">
  </form>
   */
  var article_list = document.getElementById("article-link-list");
  article_list.innerHTML = "<h1>Hello World</h1>"
}

function change_ctx_by_name(name) {
  var article_list = document.getElementById("article-link-list");
  article_list.innerHTML = "<div id=\"Markdown\"> \
  </div> \
  <form id = \"form\" action=\"\" method=\"post\" value = \"" + name + ".md" + "\"> \
  </form>";
  console.log(article_list.innerHTML);
  ajax_parser();
}