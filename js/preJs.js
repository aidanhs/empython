this.init_empython = function (initialized_callback, print_hook) {

  var root = {
    Module: (function () {
      var Module = {
        noInitialRun: true,
        noExitRuntime: true,
        preRun: [],
        postRun: [],
        print: print_hook,
        printErr: print_hook,
      };
