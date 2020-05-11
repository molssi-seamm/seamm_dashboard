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
                    var retrieved_link = ajaxJobs(data[i].jobs[j])
                    job_links = job_links + retrieved_link
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

function ajaxJobs(job_id) {
    var job_link = ''
    $.ajax({
        url: `api/jobs/${job_id}`,
        async: false,
        dataType: 'json',
        success: function(data){
            job_link = `<a class="nav-link p-0 my-1" href="/jobs/${data.id}" title="View Details">${data.id}</a>`
        }
    })
    return job_link;
}

function ajaxFlowcharts(flowchart_id) {
    var flowchart_link = ''
    $.ajax({
        url: `api/flowcharts/${flowchart_id}`,
        async: false,
        dataType: 'json',
        success: function(data){
            flowchart_link = `<a class="nav-link p-0 btn btn-secondary my-1" href="flowcharts/${data.id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`

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
