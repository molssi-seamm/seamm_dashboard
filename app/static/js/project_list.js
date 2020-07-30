function ajaxProjects(){
var arrayReturn = [];
    $.ajax({
        url: "api/projects",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                var job_links = ''
                for (var j = 0, jlen = data[i].jobs.length; j < jlen; j++) {
                    let job_link = `<a class="nav-link p-0 my-1" href="/jobs/${data[i].jobs[j]}" title="View Details">${data[i].jobs[j]}</a>`
                    job_links = job_links + job_link
                }

                var flowchart_links = ''
                for (var j = 0, jlen = data[i].jobs.length; j < jlen; j++) {
                    var retrieved_link = ajaxFlowcharts(data[i].flowcharts[j])
                    flowchart_links = flowchart_links + retrieved_link
                }

                arrayReturn.push([data[i].name, 
                data[i].description,
                job_links,
                flowchart_links,
                `<a class="nav-link p-0 btn btn-primary my-1" href="/projects/${data[i].id}/edit">
            <i class="fa fa-edit"></i><span class="d-none d-md-inline">&nbsp; Edit</span></a>
            <a class="nav-link p-0 btn btn-danger" href="#">
                <i class="fa fa-trash"></i><span class="d-none d-md-inline">&nbsp; Delete</span></a>` ]);
            }
        inittable(arrayReturn);
        }
    });
}

function ajaxFlowcharts(flowchart_id) {
    var flowchart_link = ''
    $.ajax({
        url: `api/flowcharts/${flowchart_id}`,
        async: false,
        dataType: 'json',
        success: function(data){
            
        }
    })
    return flowchart_link;
}

function inittable(data) {	
    $('#projects').DataTable( {
        "responsive": true,
        "aaData": data,
        "columnDefs": [
            { className: "sidebar-nav", "targets": [0, 2, 3]}
        ],
        "autoWidth": true,
    } );
}

  $(document).ready(function(){
    ajaxProjects()
  })
