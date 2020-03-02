var arrayReturn = [];
    $.ajax({
        url: "api/flowcharts",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                console.log(data[i])
                arrayReturn.push([data[i].title, 
                data[i].description,
                `<a class="nav-link p-0 btn btn-secondary" href="flowcharts/${data[i].id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`,
                `<a class="nav-link p-0 btn btn-primary" href="/flowcharts/${data[i].id}/edit">
            <i class="fa fa-edit"></i><span class="d-none d-md-inline">&nbsp; Edit</span></a>
            <a class="nav-link p-0 btn btn-danger" href="#">
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
            { className: "sidebar-nav", "targets": [0, 1, 2]}
        ],
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
