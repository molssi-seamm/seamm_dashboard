
var url = location.href.split('/');
var job_id = url.slice(-1)[0];

function inittable(data, div_id) {	
    var my_table = $(`#${div_id}`).DataTable( {
        "responsive": false,
        "info": false,
        "searching": false,
        "lengthChange": false,
        "orderable": false,
        "paginate": false,
        "aaData": data,
        "columnDefs": [
            { className: "sidebar-nav", "targets": [0, 1, 2, 3 ]}
        ],
        "autoWidth": false,
    } );

    return my_table
}

function buildTree() {
    var elements = [];
        $.ajax({
            url: `api/jobs/${job_id}/files`,
            async: false,
            dataType: 'json',
            success: function (data) {
                elements = data
            }
        });
    return elements
}

function load_file(file_url, data_type){
    var return_data = []
    console.log(file_url)
    $.ajax({
        url: file_url,
        async: false,
        dataType: data_type,
        success: function (data) {
            return_data = data
        }
    });
    return return_data
    }

function buildFlowchart(flowchart_url) {
    var elements = [];
    var flowchart_id = flowchart_url.split('/').slice(-1)[0]
        $.ajax({
            url: `api/flowcharts/${flowchart_id}/cytoscape`,
            async: false,
            dataType: 'json',
            success: function (data) {
                elements = data
            }
        });
    return elements
    }

function get_job_data() {
    var arrayReturn = [];
    var job_data = {};
    $.ajax({
    url: `api/jobs/${job_id}`,
    dataType: 'json',
    async: false,
    success: function (data) {
        job_data = data;
        },
    })
    return job_data
}

function build_job_table(data) {
    arrayReturn = [[`<a class="nav-link p-0" href="/jobs/${data.id}" title="View Details">`+data.name+'</a>', 
            data.status, 
            `<a class="nav-link p-0 btn btn-secondary" href="flowcharts/${data.flowchart_id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`,
            `<a class="nav-link p-0 btn btn-primary" href="/jobs/${data.id}/edit">
        <i class="fa fa-edit"></i><span class="d-none d-md-inline">&nbsp; Edit</span></a>
        <a class="nav-link p-0 btn btn-danger" href="#">
            <i class="fa fa-trash "></i><span class="d-none d-md-inline">&nbsp; Delete</span></a>` ]];
        inittable(arrayReturn, "job-info");
}

function build_cyto_graph(elements, container_id) {
    var graph = cytoscape({
        container: document.getElementById(container_id),
      
        boxSelectionEnabled: false,
        autounselectify: true,
      
        layout: {
          name: 'preset'
        },
      
        style: [
          {
            selector: 'node',
            style: {
              'shape': 'rectangle',
              'background-color': '#DCDCDC',
              'label': 'data(name)',
              'text-halign': 'center',
              'text-valign': 'center',
              'width': 200,
            }
          },
      
          {
            selector: 'edge',
            style: {
              'width': 4,
              'target-arrow-shape': 'triangle',
              'line-color': '#696969',
              'target-arrow-color': '#696969',
              'curve-style': 'bezier',
            }
          }
        ],
      
        elements: elements,
    });
    
    return graph
}

$(document).ready(function() {
    $('#view-card').height($(window).height()-$('#js-tree').offset().top+50)

    job_data = get_job_data();
    build_job_table(job_data);
    tree_elements = buildTree();
    
    // JS Tree stuff
    $('#js-tree').jstree({ 'core' : {
        'data' : tree_elements,
        },

    "plugins" : ["search", "wholerow"],

    "search": {
            "case_insensitive": true,
            "show_only_matches" : true
        },
    })

    $('#search').keyup(function(){
        $('#js-tree').jstree('search', $(this).val());
    });

    $('#job_title').text(tree_elements[0].text)

    $('#js-tree').bind("select_node.jstree", function (e, data) {
        if (data.node.a_attr.href != '#') {
            
            $('#view-card').height($(window).height()-$('#js-tree').offset().top+50)

            // Clear div content before new content loading 
            content_div = document.getElementById('file-content');
            content_div.innerHTML = "";

            content_div = document.getElementById('cytoscape');
            content_div.innerHTML = "";
            
            try {
                table.destroy();
                $('#csv-data tr').remove();
                $('#csv-data thead').remove();
                $('#csv-data tbody').remove();
            } catch {
                // Do nothing.
            }

            $('#file-name').html(data.node.text)

            // Figure out the file type.
            var href = data.node.a_attr.href;
            var file_type = href.split(".").slice(-1);
            var cyto_elements = buildFlowchart(`views/flowcharts/${job_data.flowchart_id}`)


            // Handle the file.
            if (file_type=='flow'){
                $('#file-content').height("0px")
                $('#cytoscape').height($(window).height()-$('#js-tree').offset().top+50);

                var cy = window.cy = build_cyto_graph(cyto_elements, 'cytoscape')
                cy.nodes('[name = "Join"]').style( {
                    'shape': 'ellipse',
                    'background-color': '#000000',
                    'text-halign': 'right',
                    'text-valign': 'center',
                    'width': 30,
                  });
            
                cy.nodes('[name = "Start"]').style( {
                        'shape': 'ellipse',
                    });
            }

            else if (file_type=='graph'){
                $('#cytoscape').height("0px")
                $('#file-content').height("0px")

                plotly_data = load_file(href, 'json')
                Plotly.newPlot(content_div, plotly_data.data, plotly_data.layout, 
                    {'editable': true, 
                    'toImageButtonOptions': {
                    format: 'png', // one of png, svg, jpeg, webp
                    filename: data.node.text,
                    scale: 10 // Multiply title/legend/axis/canvas sizes by this factor
                  }});

                  $('#view-card').height($('.plotly').height()+150);
                
            }

            else if (file_type=='csv'){
                $('#cytoscape').height("0px")
                $('#file-content').height("0px")
                var csv_data = load_file(href, 'text')
                var separated = $.csv.toArrays(csv_data)

                var headers = [];
                for (var j=0; j<separated[0].length; j++) {
                    headers.push( {'title': separated[0][j]} )
                }

                var data = separated.slice(1,)
                
                table = $('#csv-data').DataTable({
                    "responsive": true,
                    "aaData": data,
                    "columns": headers,
                    "initComplete": function (settings, json) {  
                        $("#csv-data").wrap("<div style='overflow:auto; width:100%;position:relative;'></div>");
                    },
                });

                $('#view-card').height($('#csv-data_wrapper').height()+150)


            }
            // Try to load as text file.
            else { 
                $('#cytoscape').height("0px")
                $('#file-content').height($('#ui-view').height());
                $("#file-content").load(href); 
            }
        }
    });

})

    