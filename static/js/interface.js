$(function() {
   $(".movement").click(function(e) {
      e.preventDefault()
      var me = $(this);
      
      ws.send("move " + me.data("dim") +  " " + me.data("delta"))
   });
   $("#console-input").keypress(function(e) {
       if(e.which == 13) {
           var command = $(this).val()
           if (command.length > 0) {
              ws.send(command)
              $(this).val("")
           }
       }
   });
});