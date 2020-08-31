function ajaxProjects(){
var arrayReturn = [];
    $.ajax({
        url: "api/projects",
        async: false,
        dataType: 'json',
        success: function (data) {
            let col_string = {
                0 : 'col-xl-12',
                1 : 'col-xl-12',
                2 : 'col-xs-12 col-xl-6'
            }
            let num_projects = data.length

            if (num_projects < 3) {
                column_string = col_string[num_projects]
            } else {
                column_string =  "col-xs-12 col-lg-6 col-xl-4"
            }

            let card_string = ''
            for (var i = 0, len = data.length; i < len; i++) {
                card_string += `<div class=${column_string}>
                    <div class="card text-white bg-projects" style="min-height:300px;">
                    <div class="card-body pb-0">
                        <div class="text-value-lg"><a class='nav-link' href="projects" style="color:white" class="card-title">${data[i].name}</a></div>
                        <div class="card-description fade-text" style="height:100px; overflow:hidden">${data[i].description}</div>
                        <div class="mt-4 px-3">
                        <div class="row">
                            <div class="col">
                            <div class="text-value-lg" class="job-number">${data[i].jobs.length}</div> jobs 
                            </div>
                            <div class="col">
                            <div class="text-value-lg" class="flowchart-number">${data[i].flowcharts.length}</div> flowcharts
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>
                </div>`
            }
        $('#project-cards').html(card_string)
        inittable(arrayReturn);
        }
    });
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
