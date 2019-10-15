<script>
jQuery(document).ready(function(){
  function getData(){
    console.log("Calling MolSSI APIs");  
    var response = jQuery.ajax({
            type: "GET",
            //url: "http://api.molssi.org/test",
            url: "http://localhost:5000/test",
            //async: false,   
            dataType: "jsonp",
            data: {},
            jsonpCallback: "processData",
            success: function(data){
                console.log("Success..., Data:", data);                
            },
            fail: function(data){
                console.error('Error ', data);               
            }
        });
  }
  window.processData = function(response) {
    console.log("In processData..");
    console.log(response.msg);
  }
  jQuery('#api-link').click(getData);
});
</script>
<a id='api-link' href="#">Get the API call</a>