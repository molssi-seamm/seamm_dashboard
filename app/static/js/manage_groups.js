$(document).ready( function() { 
    var table = $('#groups').DataTable( {
    "responsive": true,
    "ajax": {
        url: `${location.origin}/api/groups`,
        async: false,
        dataType: 'json',
        dataSrc: function (data) {
            let arrayReturn = [];
            for (var i = 0, len = data.length; i < len; i++) {
                arrayReturn.push(
                    [
                    data[i].id,
                    data[i].name, 
                    data[i].users.length,
                    `<span class="d-flex justify-content-around"><a href="${location.origin}/admin/manage_group/${data[i].id}"><button type="button" class="btn btn-primary"> <i class="fas fa-edit"></i> Manage Group</button></a></span>
                    `
                    ]
                )
            }
            return arrayReturn
        },
        error: function(xhr){
            if (xhr.status == 401) {
                window.location = `${location.origin}/401`
            }
        }
    },
    "buttons": [
        {
            className: "col-md-auto col-sm-12 btn btn-outline-success m-1 float-right",
            text: '<i class="fas fa-user-plus mr-2"></i>Create New Group',
            action: function ( ) {
                window.location=`${location.origin}/admin/create_group`
                
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
    .appendTo( '#groups_wrapper .col-md-6:eq(1)' );

});
