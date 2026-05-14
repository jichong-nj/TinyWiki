var ribbon = {
  OnLoad: function (ribbonUI) {
    console.log("TinyWiki AI 助手加载成功");
  },
  OnAction: function (control) {
    switch (control.Id) {
      case "btnOpenAIChat":
        this.OpenTaskPane();
        break;
    }
  },
  OpenTaskPane: function () {
    var tsId = "TinyWikiAIChat";
    var ts = wps.PluginStorage.getItem(tsId);
    if (ts) {
      ts.Visible = true;
    } else {
      var url = "taskpane.html";
      var width = 420;
      var taskpane = wps.CreateTaskPane(url, "TinyWiki AI 助手", width);
      taskpane.Visible = true;
      wps.PluginStorage.setItem(tsId, taskpane);
    }
  }
};
