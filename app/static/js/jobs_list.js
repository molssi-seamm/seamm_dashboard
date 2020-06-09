function inittable(data) {	

    var table = $('#jobs').DataTable( {
        "responsive": true,
        "aaData": data,
        "select": {
            "style": "multi"
        },
        "columnDefs": [
            { "className": "sidebar-nav", 
            "targets": [1]},
            {
                orderable: false,
                className: 'select-checkbox',
                targets:   0
            },
        ],
        "autoWidth": true,
        "order": [[ 1, "desc"]]
    } );
}


$(document).ready(function () {
    var arrayReturn = [];
    $.ajax({
        url: "api/jobs",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                arrayReturn.push(
		    ['', `<a class="nav-link p-0" href="/jobs/${data[i].id}" title="View Details">`+data[i].id+'</a>', 
		     data[i].title, 
		     data[i].status,
		     data[i].submitted,
		     data[i].started,
		     data[i].finished
		    ]
		)
            }
        inittable(arrayReturn);
        }
    });
    
})

