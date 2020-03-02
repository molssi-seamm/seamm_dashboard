var arrayReturn = [];
    $.ajax({
        url: "api/jobs",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                console.log(data[i])
                arrayReturn.push([`<a class="nav-link p-0" href="/jobs/${data[i].id}" title="View Details">`+data[i].name+'</a>', 
                data[i].path, 
                `<a class="nav-link p-0" href="flowchart_details/id/${data[i].flowchart_id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`,
                `<a class="btn-sm btn-info icon mr-1 btn-nav-link" href="jobs/${data[i].id}/edit">
            <i class="fa fa-edit"></i><span class="d-none d-md-inline">&nbsp; Edit</span></a>
            <a class="btn-sm btn-danger icon btn-del-confirm" href="#">
                <i class="fa fa-trash-o "></i><span class="d-none d-md-inline">&nbsp; Delete</span></a>` ]);
            }
        inittable(arrayReturn);
        }
    });

function inittable(data) {	
    $('#jobs').DataTable( {
        "responsive": true,
        "aaData": data,
        "columnDefs": [
            { className: "sidebar-nav", "targets": [0, 1, 2, 3]}
        ]
    } );
}

function applyLinkStyle() {
    var elements = document.getElementsByClassName("joblink");
    //element.classList.add("nav-link");
    //element.classList.add("p-0");
  }

  $(document).ready(function(){
    //applyLinkStyle()
  })
