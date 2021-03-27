$(document).ready( function() { 
    var table = $('#users').DataTable( {
    "responsive": true,
    "ajax": {
        url: `${location.origin}/api/users`,
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
                    data[i].email,
                    `<a href="${location.origin}/admin/manage_user/${data[i].id}"><button type="button" class="btn btn-primary"> <i class="fas fa-edit"></i> Manage User</button></a>
                    `
                    ]
                )
            }
            return arrayReturn
        },
        error: function(xhr){
            console.log("There is an error")
            if (xhr.status == 401) {
                window.location = `${location.origin}/401`
            }
        }
    },
    "buttons": [
        {
            className: "col-md-auto col-sm-12 btn btn-outline-success m-1 float-right",
            text: '<i class="fas fa-user-plus mr-2"></i>Create New User',
            action: function ( ) {
                window.location=`${location.origin}/admin/create_user`
                
            }
        },
    ],
    "select": {
        "style": "multi"
    },
    "autoWidth": true,
    "order": [[ 1, "desc"]]
} )

table.buttons().container()
    .appendTo( '#users_wrapper .col-md-6:eq(1)' );

});
