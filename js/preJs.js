this.empython = (function () {

  var root = {
    empython: function () {
      var Module = {
        noInitialRun: true,
        noExitRuntime: true,
        preRun: [],
        postRun: []
      };
