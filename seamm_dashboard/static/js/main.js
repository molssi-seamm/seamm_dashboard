/**
 * --------------------------------------------------------------------------
 * mainjs - javascript for home view
 * 
 * --------------------------------------------------------------------------
 */

 function inittable() {	

    var table = $('#jobs').DataTable( {
        "responsive": true,
        "ajax": {
            url: `api/jobs?order=desc&limit=10&sortby=last_update`,
            async: false,
            dataType: 'json',
            dataSrc: function (data) {
                let arrayReturn = [];
                for (var i = 0, len = data.length; i < len; i++) {
                    arrayReturn.push(
                        [`<a class="nav-link p-0" href="/jobs/${data[i].id}" title="View Details">`+data[i].id+'</a>', 
                        data[i].title, 
                        data[i].status,
                        data[i].submitted,
                        data[i].started,
                        data[i].finished
                        ]
                    )
                }
                return arrayReturn
            }
        },
        "columnDefs": [
            { "className": "sidebar-nav", 
            "targets": [0]},
        ],
        "autoWidth": true,
        "order": [[ 0, "desc"]]
    } );

    return table
}



 $(document).ready( function() {

    let dashboardStatus = {};
    $.ajax({
    url: `api/status`,
    dataType: 'json',
    async: false,
    success: function (data) {
        dashboardStatus = data;
        },
    })

    // Load table
    my_table = inittable()
    
    // Add action to refresh button
    $("#refresh").click(my_table.ajax.reload)

    // Load info into divs
    document.getElementById('num-jobs-in-dashboard').textContent = dashboardStatus.jobs.total
    document.getElementById('num-jobs-running').textContent = dashboardStatus.jobs.running
    document.getElementById('num-jobs-finished').textContent = dashboardStatus.jobs.finished
    document.getElementById('num-projects').textContent = dashboardStatus.projects
    document.getElementById('num-flowcharts').textContent = dashboardStatus.flowcharts

    document.getElementById("view").classList.toggle("hidden")
 })

