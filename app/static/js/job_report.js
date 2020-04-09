
var url = location.href.split('/');
var job_id = url.slice(-1)[0];

function inittable(data) {	
$('#job-info').DataTable( {
    "responsive": true,
    "aaData": data,
    "columnDefs": [
        { className: "sidebar-nav", "targets": [0, 1, 2, 3 ]}
    ],
    "autoWidth": false,
} );
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


function load_file(file_url){
    var return_data = []
    console.log(file_url)
    $.ajax({
        url: file_url,
        async: false,
        dataType: 'json',
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
            arrayReturn = [[`<a class="nav-link p-0" href="/jobs/${data.id}" title="View Details">`+data.name+'</a>', 
            data.status, 
            `<a class="nav-link p-0 btn btn-secondary" href="flowcharts/${data.flowchart_id}"><i class="fas fa-project-diagram"></i><span class="d-none d-md-inline">&nbsp;View Flowchart</span></a>`,
            `<a class="nav-link p-0 btn btn-primary" href="/jobs/${data.id}/edit">
        <i class="fa fa-edit"></i><span class="d-none d-md-inline">&nbsp; Edit</span></a>
        <a class="nav-link p-0 btn btn-danger" href="#">
            <i class="fa fa-trash "></i><span class="d-none d-md-inline">&nbsp; Delete</span></a>` ]];
        inittable(arrayReturn);
        job_data = data;
        },
    })
    return job_data
}

$(document).ready(function() {
    // Change div sizes depending on window size

    job_data = get_job_data()

    tree_elements = buildTree();

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
        if (data.node.children.length == 0) {
            var href = data.node.a_attr.href;
            var file_type = href.split(".").slice(-1);
            if (file_type=='flow'){
                var cy = window.cy = cytoscape({
                    container: document.getElementById('file-content'),
                  
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
                  
                    elements: buildFlowchart(`views/flowcharts/${job_data.flowchart_id}`),
                });

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
                plotly_data = load_file(href)
                content_div = document.getElementById('file-content');
                content_div.innerHTML = "";
                Plotly.newPlot(content_div, plotly_data.data, plotly_data.layout, {'editable': true, 
                    'toImageButtonOptions': {
                    format: 'png', // one of png, svg, jpeg, webp
                    filename: data.node.text,
                    scale: 10 // Multiply title/legend/axis/canvas sizes by this factor
                  }});
                
            }
            else { $("#file-content").load(href); }
        }
    });

})

    