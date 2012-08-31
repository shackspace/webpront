function appendToConsole(cls, text) {
   var container = $("#console-output");
   container.append('<span class="console-line ' + cls + '">' + text + '</span>');
   container.scrollTop(container[0].scrollHeight);
}

function sendCommand(command) {
   appendToConsole("in", command);
   ws.send(command);
}

$(function() {
   $(".movement").click(function(e) {
      e.preventDefault()
      var me = $(this);
      var command = "move " + me.data("dim") +  " " + me.data("delta");
      sendCommand(command);
   });
   $("#console-input input").keypress(function(e) {
       if(e.which == 13) {
           var command = $(this).val()
           if (command.length > 0) {
              sendCommand(command);
              $(this).val("");
           }
       }
   });
});