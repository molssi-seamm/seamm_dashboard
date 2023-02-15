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
        // Add this back in when we're ready to add deleting the project as an option.
        //<a class="dropdown-item nav-link delete-button" href="/projects" id="${data[i].id}">Delete Project</a>
        card_string += `<div class="${column_string}">
        <div class="card text-white bg-projects" style="min-height:200px;">
        <div class="card-body pb-0 sidebar-nav">
          <div class="btn-group float-right">
            <button type="button" class="btn btn-transparent dropdown-toggle p-0" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <i class="icon-settings"></i>
            </button>
            <div class="dropdown-menu dropdown-menu-right">
              <a class="dropdown-item" href="projects/${data[i].id}/edit">Edit Title and Description</a>
            </div>
          </div>
          <div class="text-value-lg"><a class='nav-link' href="projects/${data[i].id}/jobs" style="color:white">${data[i].name}</a></div>
        </div>
        <div class="card-description fade-text pl-3" style="height:100px; overflow:hidden">Project ID: ${data[i].id} <br><br>Description : ${data[i].description}</div>
        <div class="chart-wrapper mt-3 px-3" style="height:100px;">
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

    let csrf_access;

    // Set up ajax headers
    document.cookie.split(";").forEach(function(value) { if (value.trim().split("=")[0] == 'csrf_access_token') { csrf_access = value.trim().split('=')[1] } })

    $.ajaxSetup({
        headers: { 'X-CSRF-TOKEN': csrf_access }
    })

    // Activate delete buttons
    $(".delete-button").on("click", function(event){
        event.preventDefault()
        if (this.id == 1) {
            alert("You cannot delete the default project")
        }
        else {
            if (confirm(`You have chosen to delete Project ${this.id}. 
        
            This action will result in the deletion of all jobs and files associated with the jobs and project.
    
            This action cannot be undone.
    
            Do you wish to proceed?
            `) ) {

                $.ajax({
                    url: `api/projects/${this.id}`,
                    type: 'DELETE',
                    success: function(data) { location.reload() },
                    complete: function(xhr, textStatus) { 
                        if (xhr.status == 401) {
                            alert(`You do not have the necessary permission to delete this project.`) 
                        }
                        else if (xhr.status == 200) {
                            alert(`Project ${this.id} deleted.`)
                        }
    
                    }
                })
            }
        }
    })   
            

    document.getElementById("view").classList.toggle("hidden")
    
  })
