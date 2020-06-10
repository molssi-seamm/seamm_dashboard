function inittable(data) {	

    var table = $('#jobs').DataTable( {
        "responsive": true,
        "aaData": data,
        "select": {
            "style": "multi"
        },
        "buttons": [
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-success m-1",
                text: '<i class="fas fa-play mr-1"></i>Start',
                action: function ( e, dt, node, config ) {
                    alert( 'Button activated' );
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-info m-1",
                text: '<i class="fas fa-redo mr-1"></i>Rerun',
                action: function ( e, dt, node, config ) {
                    alert( 'Button activated' );
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-secondary m-1",
                text: '<i class="fas fa-pause mr-1"></i>Pause',
                action: function ( e, dt, node, config ) {
                    alert( 'Button activated' );
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-danger m-1",
                text: '<i class="fas fa-trash mr-1"></i>Delete',
                action: function ( e, dt, node, config ) {
                    alert( 'This action will delete all files with the selected job(s). Are you sure?' );
                }
            },
        ],
        "columnDefs": [
            { "className": "sidebar-nav", 
            "targets": [1]},
            {
                orderable: false,
                className: 'select-checkbox p-2',
                targets:   0
            },
        ],
        "autoWidth": true,
        "order": [[ 1, "desc"]]
    } );

    table.buttons().container()
    .appendTo( '#jobs_wrapper .col-md-6:eq(1)' );
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

    var tableButtons = document.getElementsByClassName("dt-buttons")
    tableButtons[0].className = "row justify-content-end"
    
})

