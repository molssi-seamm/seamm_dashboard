$(document).ready( function() { 
    var table = $('#users').DataTable( {
    "responsive": true,
    "ajax": {
        url: `api/users`,
        async: false,
        dataType: 'json',
        dataSrc: function (data) {
            let arrayReturn = [];
            for (var i = 0, len = data.length; i < len; i++) {
                arrayReturn.push(
                    [
                    data[i].id,
                    data[i].username, 
                    data[i].first_name,
                    data[i].last_name,
                    data[i].roles,
                    data[i].groups,
                    `<button type="button" class="btn btn-primary"> <i class="fas fa-edit"></i> Manage User</button>
                    `
                    ]
                )
            }
            return arrayReturn
        },
        error: function(xhr){
            console.log("There is an error")
            if (xhr.status == 401) {
                window.location = "401"
            }
        }
    },
    "buttons": [
        {
            className: "col-md-auto col-sm-12 btn btn-outline-success btn-lg m-1 float-right",
            text: '<i class="fas fa-user-plus mr-2"></i>Create New User',
            action: function ( ) {
                window.location='create_user'
                
            }
        },
    ],
    "select": {
        "style": "multi"
    },
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
} )

table.buttons().container()
    .appendTo( '#users_wrapper .col-md-6:eq(1)' );

});