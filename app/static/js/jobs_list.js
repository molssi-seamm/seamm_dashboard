var arrayReturn = [];
    $.ajax({
        url: "api/jobs",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                arrayReturn.push([`<a class="nav-link p-0" href="/jobs/${data[i].id}" title="View Details">`+data[i].name+'</a>', 
                data[i].status,
                data[i].path, 
                `<a class="nav-link p-0 btn btn-secondary" href="flowcharts/${data[i].flowchart_id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`,
                `<a class="nav-link p-0 btn btn-primary" href="/jobs/${data[i].id}/edit">
            <i class="fa fa-edit"></i><span class="d-none d-md-inline">&nbsp; Edit</span></a>
            <a class="nav-link p-0 btn btn-danger" href="#">
                <i class="fa fa-trash "></i><span class="d-none d-md-inline">&nbsp; Delete</span></a>` ]);
            }
        inittable(arrayReturn);
        }
    });

function inittable(data) {	
    $('#jobs').DataTable( {
        "responsive": true,
        "aaData": data,
        "columnDefs": [
            { className: "sidebar-nav", "targets": [0, 2, 3, 4 ]}
        ],
        "autoWidth": false,
    } );
}
