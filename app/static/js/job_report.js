// You must include util.js on any page that uses this javascript file
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

function buildTree(jobID) {
    var elements = [];
        $.ajax({
            url: `api/jobs/${jobID}/files`,
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


function setFileDivSize() {
    viewCardHeight = $(window).outerHeight()*0.90
    $("#js-tree").height(viewCardHeight)
    $(".active-div").height(viewCardHeight)
}

function flowResize(viewCardHeight) {
    viewCardHeight = $(window).outerHeight()*0.90
    $('#file-content').height("0px")
    $('#cytoscape').height(viewCardHeight);
}

function loadFlow(flowchartID) {
    let cytoElements = buildFlowchart(`views/flowcharts/${flowchartID}`)
    var cy = window.cy = buildCytoGraph(cytoElements, 'cytoscape')
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

    $(".active-div").removeClass("active-div")
    $("#cytoscape").addClass("active-div")
}

function loadGraph(nodeData) {
    let content_div = document.getElementById('file-content');
    $('#cytoscape').height("0px")
    $("#file-content").html("")

    var plotlyData = load_file(nodeData.a_attr.href, 'json')
    Plotly.newPlot(content_div, plotlyData.data, plotlyData.layout, 
        {'editable': true, 
        'toImageButtonOptions': {
        format: 'png', // one of png, svg, jpeg, webp
        filename: nodeData.text,
        scale: 10 // Multiply title/legend/axis/canvas sizes by this factor
        }});
        
        $('#view-card').height($('.plotly').height()+150);
        $('#file-content').height($('.plotly').height()+150)
    
        $(".active-div").removeClass("active-div")
        $("#file-content").addClass("active-div")

}

function loadTable(href) {
    $('#cytoscape').height("0px")
    $('#file-content').height("0px")
    var csvData = load_file(href, 'text')
    var separated = $.csv.toArrays(csvData)

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

    $('#outer-card').height($("#csv-data_wrapper").height()*1.1)

    $(".active-div").removeClass("active-div")
    $("#csv-data").addClass("active-div")

}

function loadOther(file) {
    $("#file-content").load(file);
    $(".active-div").removeClass("active-div")
    $("#file-content").addClass("active-div") 
}

function resizeOther(viewCardHeight) {
    $('#cytoscape').height("0px")
    $('#file-content').height(viewCardHeight);
}

function loadStructure(URL) {
    var fileExtension = URL.split(".");
    fileExtension = fileExtension[fileExtension.length - 1]
    var stage = new NGL.Stage("file-content", {backgroundColor: "white"} );
    stage.loadFile(URL, {defaultRepresentation: true, ext: fileExtension },);
}

var contentFunctions = {
    "flow" : {
        "load": [loadFlow, "jobData.flowchart_id"],
        "resize": [flowResize, "viewCardHeight"],
    },
    "graph": {
        "load": [loadGraph, "data.node"],
        "resize": null,
    },
    "csv": {
        "load" : [loadTable, "href"],
        "resize": null,
    },
    "mmcif": {
        "load" : [loadStructure, "href"],
        "resize": [resizeOther, "viewCardHeight"],
    },
    "pdb": {
        "load" : [loadStructure, "href"],
        "resize": [resizeOther, "viewCardHeight"],
    },
    "other": {
        "load": [loadOther, "href"],
        "resize": [resizeOther, "viewCardHeight"]
    },
}

$(document).ready(function() {
    let url = location.href.split('/');
    let content_div = document.getElementById('file-content');
    $("#file-content").addClass("active-div")
    const jobID = url.slice(-1)[0];
    let viewCardHeight;

    // Get info we need for page
    let jobData = getJobData(jobID);
    let treeElements = buildTree(jobID);

    // add listener for resize event
    window.addEventListener('resize', setFileDivSize)

    // Load in the job status
    $("#job-status").html(jobData.status)
    $('#job-title').text(treeElements[0].text)
    
    // JS Tree stuff
    $('#js-tree').jstree({ 'core' : {
        'data' : treeElements,
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

    // Code to control loading content into div on button clicks
    $('#js-tree').bind("select_node.jstree", function (e, data) {
        if (data.node.a_attr.href != '#') {

            cytoscape_div = document.getElementById('cytoscape');
            
            
            // Clear div content before new content loading 
            content_div.innerHTML = "";

            
            cytoscape_div.innerHTML = "";
            
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
            var fileType = href.split(".").slice(-1);

            // Figure out functions to call. If not recognized extension, other
            if (!(fileType in contentFunctions)) {
                fileType = "other"
            }

            //Resize function
            if (contentFunctions[fileType]["resize"]) {
                let resizeFunc = contentFunctions[fileType]["resize"][0]
                let resizeArg = eval(contentFunctions[fileType]["resize"][1])
                resizeFunc(resizeArg)
            }

            // Load function
            let func = contentFunctions[fileType]["load"][0]
            let arg = eval(contentFunctions[fileType]["load"][1])
            func(arg)
        }
    });

    viewCardHeight = $(window).outerHeight()*0.90
    $("#outer-card").height(viewCardHeight*1.10)
    $("#js-tree").height(viewCardHeight*1.10)
    $("#file-content").height(viewCardHeight)

})

    