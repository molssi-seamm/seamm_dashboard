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

    // Load info into divs
    document.getElementById('num-jobs-in-dashboard').textContent = dashboardStatus.jobs.total
    document.getElementById('num-jobs-running').textContent = dashboardStatus.jobs.running
    document.getElementById('num-jobs-finished').textContent = dashboardStatus.jobs.finished
    document.getElementById('num-projects').textContent = dashboardStatus.projects
    document.getElementById('num-flowcharts').textContent = dashboardStatus.flowcharts

    document.getElementById("view").classList.toggle("hidden")
 })

