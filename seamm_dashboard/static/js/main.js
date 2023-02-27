/**
 * --------------------------------------------------------------------------
 * mainjs - javascript for home view
 * 
 * --------------------------------------------------------------------------
 */


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
    my_table = inittable("jobs?order=desc&sortby=last_update&limit=10", paging=false);
    
    // Add action to refresh button
    $("#refresh").click(my_table.ajax.reload);

    // Adjust buttons
    let tableButtons = document.getElementsByClassName("dt-buttons");
    tableButtons[0].className = "row justify-content-end";


    // Load info into divs
    document.getElementById('num-jobs-in-dashboard').textContent = dashboardStatus.jobs.total;
    document.getElementById('num-jobs-running').textContent = dashboardStatus.jobs.running;
    document.getElementById('num-jobs-finished').textContent = dashboardStatus.jobs.finished;
    document.getElementById('num-projects').textContent = dashboardStatus.projects;
    document.getElementById('num-flowcharts').textContent = dashboardStatus.flowcharts;

    document.getElementById("view").classList.toggle("hidden");
    previous = window.location.href;
 })

