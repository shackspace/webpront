$(function() {
   $(".movement").click(function(e) {
      e.preventDefault()
      var me = $(this);
      
      ws.send("move " + me.data("dim") +  " " + me.data("delta"))
   });
});