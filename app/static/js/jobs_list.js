function jobAction(selectedRows, action) {

    var actionInformation = {
        "run": {
            "request": {
                "status": "Starting",
                "started": "",
                "finished": "",
            },
            "description":
        `

This action will submit all selected jobs which are paused to be run starting at their current step. Jobs which are currently running will be unaffected. 

Do you wish to continue?
        `,

        },

        "re-run": {
            "request":{
                "status": "Submitted",
                "submitted": Date.now(),
                "started": "",
                "finished": "",
            },
            "description":
        `

This action will stop all selected jobs are run them from the beginning of their flowchart.
        
Any progress from previous runs will be lost.

Do you wish to continue?
        `,
        },

        "pause": {
            "request": {
                "status": "",
                },
            "description": `Pausing is not yet available.`,},

        "delete": {
            "request":{
                "status": "deleted",
            },
            
            "description": `


This action will delete all selected jobs.
        
The jobs will be stopped if running and the associated files will be deleted from the file system.

This action cannot be undone. 
        
Do you wish to continue?
        `,},

    };

    var numberSelected = selectedRows.count()

    // Send alert if no jobs selected
    if (numberSelected == 0) {
        alert(`No jobs selected for ${action} action`)
    }
    // If jobs have been selected.
    else {
        var selectedData = selectedRows.data()

        // Create a temporary div so we can read link text
        var temp = document.createElement('div')
        var jobNumbers = [];
        for (i=0; i<numberSelected; i++) {
            
            temp.innerHTML = selectedData[i]
            var jobNum = temp.children[0].textContent
            jobNumbers.push(jobNum)
        }

        // Confirm this is what they want
         if (confirm(`You have chosen to ${action} job(s): ${jobNumbers}. ${actionInformation[action]["description"]}`)) {
                for (let i=0; i<jobNumbers.length; i++) {
                    let jobID = jobNumbers[i]
                    if (action === "run" || action === "re-run" ) {
                        let putData = JSON.stringify(actionInformation[action]["request"])
                        $.ajax({
                            url: `api/jobs/${jobID}`,
                            type: 'PUT',
                            dataType: 'json',
                            headers: { 
                                'Accept': 'application/json',
                                'Content-Type': 'application/json' 
                            },
                            data: putData,
                        });
                    } else if (action === "delete") {
                        console.log("Deleting")
                        $.ajax({
                            url: `api/jobs/${jobID}`,
                            type: 'DELETE',
                        })
                    };
            } 
            location.reload()
         }
    }
}

function inittable(data) {	

    var table = $('#jobs').DataTable( {
        "responsive": true,
        "aaData": data,
        "select": {
            "style": "multi"
        },
        "buttons": [
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-success m-1 confirmation",
                text: '<i class="fas fa-play mr-1"></i>Continue',
                action: function ( ) {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "run")
                    
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-info m-1 confirmation",
                text: '<i class="fas fa-redo mr-1"></i>Restart',
                action: function () {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "re-run")
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-secondary m-1 confirmation",
                text: '<i class="fas fa-pause mr-1"></i>Pause',
                action: function () {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "pause")
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-danger m-1 confirmation",
                text: '<i class="fas fa-trash mr-1"></i>Delete',
                action: function () {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "delete")
                }
            },
        ],
        "columnDefs": [
            { "className": "sidebar-nav", 
            "targets": [1]},
            {
                orderable: false,
                className: 'select-checkbox p-2',
                targets:   0
            },
        ],
        "autoWidth": true,
        "order": [[ 1, "desc"]]
    } );

    table.buttons().container()
    .appendTo( '#jobs_wrapper .col-md-6:eq(1)' );
}


$(document).ready(function () {
    var arrayReturn = [];
    $.ajax({
        url: "api/jobs",
        async: false,
        dataType: 'json',
        success: function (data) {
            for (var i = 0, len = data.length; i < len; i++) {
                arrayReturn.push(
		    ['', `<a class="nav-link p-0" href="/jobs/${data[i].id}" title="View Details">`+data[i].id+'</a>', 
		     data[i].title, 
		     data[i].status,
		     data[i].submitted,
		     data[i].started,
		     data[i].finished
		    ]
		)
            }
        inittable(arrayReturn);
        }
    });

    var tableButtons = document.getElementsByClassName("dt-buttons")
    tableButtons[0].className = "row justify-content-end"
    
})

