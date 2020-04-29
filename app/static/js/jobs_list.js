var arrayReturn = [];
    $.ajax({
        url: "api/jobs",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                arrayReturn.push(
		    [`<a class="nav-link p-0" href="/jobs/${data[i].id}" title="View Details">`+data[i].id+'</a>', 
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

function inittable(data) {	
    $('#jobs').DataTable( {
        "responsive": true,
        "aaData": data,
        "columnDefs": [
            { className: "sidebar-nav", "targets": [0]}
        ],
        "autoWidth": true,
    } );
}
