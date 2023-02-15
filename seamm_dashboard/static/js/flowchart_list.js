function ajaxFlowcharts(){
var arrayReturn = [];
    $.ajax({
        url: "api/flowcharts",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                var job_links = ''
                for (var j = 0, jlen = data[i].jobs.length; j < jlen; j++) {
                    var retrieved_link = ajaxJobs(data[i].jobs[j])
                    job_links = job_links + retrieved_link
                }
                arrayReturn.push([data[i].title, 
                data[i].description,
                job_links,
                `<a class="nav-link p-0 btn btn-secondary" href="flowcharts/${data[i].id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`,
                `<a class="nav-link p-0 btn btn-primary" href="/flowcharts/${data[i].id}/edit">
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
            job_link = `<a class="nav-link p-0" href="/jobs/${data.id}" title="View Details">`+data.id+'</a><br>'
        }
    })
    return job_link;
}

function inittable(data) {	
    $('#flowcharts').DataTable( {
        "responsive": true,
        "aaData": data,
        "columnDefs": [
            { className: "sidebar-nav", "targets": [0, 1, 2, 3]}
        ],
    } );
}

  $(document).ready(function(){
    ajaxFlowcharts();
    document.getElementById("view").classList.toggle("hidden");
    previous = window.location;

  })
