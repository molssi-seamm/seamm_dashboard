function cardView(data){

    $('#project-cards').html('')
    $('#table-holder').html('<table id="projects" class="table table-responsive-sm table-bordered table-striped table-sm" style="width:100%"></table>')

    let col_string = {
        0 : "col-xl-12",
        1 : "col-xl-12",
        2 : "col-xs-12 col-xl-6"
    }
    let num_projects = data.length
    let column_string;

    if (num_projects < 3) {
        column_string = col_string[num_projects]
    } else {
        column_string =  "col-xs-12 col-lg-6 col-xl-4"
    }

    let card_string = ''
    for (var i = 0, len = data.length; i < len; i++) {
        card_string += `<div class="${column_string}">
            <div class="card text-white bg-projects" style="min-height:300px;">
            <div class="card-body pb-0 sidebar-nav">
                <div class="text-value-lg"><a class="nav-link" href="projects/${data[i].id}/jobs" style="color:white" class="card-title">${data[i].name}</a></div>
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

    if (data.length == 0) {
        card_string = `<p>You have no projects.</p>`
    }

    $('#project-cards').html(card_string)
}

var load_data = {
    'card' : cardView,
    'list': inittable,
}


function ajaxProjects(viewType){
        $.ajax({
            url: "api/projects",
            async: false,
            dataType: 'json',
            success: function (data) {
                load_data[viewType](data)
                
            }
        });
}

function inittable(data) {
    
    if ( ! $.fn.DataTable.isDataTable( '#projects' ) ) {
        let table_header = `
        <thead>
        <tr>
            <th>
            Project Name
            </th>
            <th>
            Project Description
            </th>
            <th>
            Number of Jobs
            </th>
            <th>
            Number of Flowcharts
            </th>
        </thead>`
    
    $('#project-cards').html('')
    $('#projects').html(table_header)

    // Build data for table
    let arrayReturn = []
    for (var i = 0, len = data.length; i < len; i++) {
        arrayReturn.push([`<a class="nav-link p-0" href="projects/${data[i].id}/jobs">${data[i].name}</a>`,
            data[i].description,
            data[i].jobs.length,
            data[i].flowcharts.length, 
        ])
        }

        $('#projects').DataTable( {
            "responsive": false,
            "aaData": arrayReturn,
            "autoWidth": false,
            "columnDefs": [
                { "className": "sidebar-nav", 
                "targets": [0]},
            ],
        } );
    }
}

  $(document).ready(function(){

    let listButton = document.querySelector('#toggle-list')
    let cardButton = document.querySelector('#toggle-card')

    cardButton.classList.add('active')

    //- Add click events - should probably move toggling into function sometime
    document.getElementById("toggle-card").addEventListener("click", function() { 
        ajaxProjects("card")
        if (!cardButton.classList.contains('active')) {
            cardButton.classList.add('active')
            cardButton.setAttribute('aria-pressed', true)
        }

        if (listButton.classList.contains('active')) {
            listButton.classList.remove('active')
            listButton.setAttribute('aria-pressed', false)

        }
    
    });
    document.getElementById("toggle-list").addEventListener("click", function() { 
        ajaxProjects("list")
        if (!listButton.classList.contains('active')) {
            listButton.classList.add('active')
            listButton.setAttribute('aria-pressed', true)
        }

        if (cardButton.classList.contains('active')) {
            cardButton.classList.remove('active')
            cardButton.setAttribute('aria-pressed', false)

        }
 
    });
    
    // Load initial data
    ajaxProjects("card")

    document.getElementById("view").classList.toggle("hidden")

    
  })
