function buildTree() {
    var elements = [];
    var url = location.href.split('/')
    var job_id = url.slice(-1)[0]
        $.ajax({
            url: `api/jobs/${job_id}/files`,
            async: false,
            dataType: 'json',
            success: function (data) {
                elements = data
            }
        });
        $('#js-tree').jstree({ 'core' : {
            'data' : elements,
            },

        "plugins" : ["search"],
        
        "search": {
                "case_insensitive": true,
                "show_only_matches" : true
            },
    })
}

buildTree()

$('#search').keyup(function(){
	$('#js-tree').jstree('search', $(this).val());
});


