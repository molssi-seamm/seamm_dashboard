function jobAction(selectedRows, action) {
    var numberSelected = selectedRows.count()

    if (numberSelected == 0) {
        alert(`No jobs selected for ${action} action`)
    }
    else {
        var selectedData = selectedRows.data()

        // Create a temporary div so we can read link text
        var temp = document.createElement('div')
        var jobNumbers = [];
        for (i=0; i<numberSelected; i++) {
            
            temp.innerHTML = selectedData[i]
            var jobNum = temp.children[0].textContent

            console.log(jobNum)
            jobNumbers.push(jobNum)
        }

        alert(`You have chosen to ${action} job(s): ${jobNumbers}` );

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
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-success m-1",
                text: '<i class="fas fa-play mr-1"></i>Start',
                action: function ( ) {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "run")
                    
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-info m-1",
                text: '<i class="fas fa-redo mr-1"></i>Rerun',
                action: function () {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "re-run")
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-secondary m-1",
                text: '<i class="fas fa-pause mr-1"></i>Pause',
                action: function () {
                    var rows = table.rows( { selected: true } );
                    jobAction(rows, "pause")
                }
            },
            {
                className: "col-lg-2 col-md-3 col-sm-12 btn btn-danger m-1",
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

