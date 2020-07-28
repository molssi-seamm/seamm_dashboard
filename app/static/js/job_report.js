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
    viewCardHeight = $(window).outerHeight()*0.85
    $("#js-tree").height(viewCardHeight)
    $(".active-div").height(viewCardHeight)
}

function flowResize(viewCardHeight) {
    viewCardHeight = $(window).outerHeight()*0.90
    $('#file-content').height("0px")
    $('#structure').height("0px")
    $('#cytoscape').height(viewCardHeight*0.9);
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
    $('#structure').height("0px")
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
    var fileType = file.split(".").slice(-1);
    $("#file-content").html(`<pre style="white-space:pre-wrap;" id="pre-code"><code id="codeBlock" class="language-${fileType}"></code>`)
    $("#codeBlock").load(file, function(data){ 
        if (data.length < 75000) {
            $("#pre-code").addClass('line-numbers')
            }
        Prism.highlightAll() });
    $(".active-div").removeClass("active-div")
    $("#codeBlock").addClass("active-div") 
    $("#file-content").addClass("active-div") 
}

function resizeOther(viewCardHeight) {
    $('#cytoscape').height("0px")
    $('#structure').height("0px")
    $('#file-content').height(viewCardHeight);
}

function resizeStructure(viewCardHeight) {
    $('#cytoscape').height("0px")
    $('#structure').height(viewCardHeight)
    $('#file-content').height("0px");
}

function loadStructure(URL) {
    
    // Inner function for NGL stage - only used in this function
    function loadStage(URL, representation="default") {
        
        // Clear stage if one exists
        let canvas = document.querySelector("#structure canvas")
        if (canvas) {
            canvas.remove()}

        // Figure out the file extension and load the file
        var fileExtension = URL.split(".");
        fileExtension = fileExtension[fileExtension.length - 1]
        var stage = new NGL.Stage("structure", {backgroundColor: "white"} );
        
        if (representation == "default") {
            stage.loadFile(URL, {defaultRepresentation: true, ext: fileExtension });
        }

        else {
            stage.loadFile(URL, {ext: fileExtension }).then(function (component) {
            // add specified representation to the structure component
            component.addRepresentation(representation);
            // provide a "good" view of the structure
            component.autoView();
            });
        }

        return stage
    }

    // Put some buttons above the stage
    $("#structure").html(`
        <div>
            <span>
                <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Representation Style
                </button>
                <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                    <a class="dropdown-item" href="#" id='default-rep'>Default</a>
                    <a class="dropdown-item" href="#" id="ball-stick-rep">Ball and Stick</a>
                    <a class="dropdown-item" href="#" id="licorice-rep">Licorice</a>
                    <a class="dropdown-item" href="#" id="cartoon-rep">Cartoon</a>
                    <a class="dropdown-item" href="#" id="surface-rep">Surface</a>
                    <a class="dropdown-item" href="#" id="spacefill-rep">Space Fill</a>
                </div>
            </span>

            <span>
                <button class="btn btn-primary dropdown-toggle" type="button" id="image-export" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Export Image
                </button>
                <div class="dropdown-menu" aria-labelledby="image-export">
                    <a class="dropdown-item" href="#" id='normal'>Normal Quality</a>
                    <a class="dropdown-item" href="#" id="high">High Quality</a>
                    <a class="dropdown-item" href="#" id="ultra-high">Ultra High Quality</a>
                </div>
            </span>
        </div>
    `)

    // Initial stage load
    var myStage;
    myStage = loadStage(URL);

    // Change active div
    $(".active-div").removeClass("active-div")
    $("#structure").addClass("active-div")

    // All the button behavior
    $(document).on("click", "#default-rep", {'URL': URL, 'rep': 'default'},
        function(event){ 
        event.preventDefault();
        myStage = loadStage(event.data.URL, event.data.rep);
        });
    
    $(document).on("click", "#licorice-rep", {'URL': URL, 'rep': 'licorice'},
        function(event){ 
        event.preventDefault();
        myStage = loadStage(event.data.URL, event.data.rep);
        });

    $(document).on("click", "#cartoon-rep", {'URL': URL, 'rep': 'cartoon'},
        function(event){ 
        event.preventDefault();
        myStage = loadStage(event.data.URL, event.data.rep);
        });

    $(document).on("click", "#ball-stick-rep", {'URL': URL, 'rep': 'ball+stick'}, 
        function(event){ 
            event.preventDefault();
            myStage = loadStage(event.data.URL, event.data.rep)
            });
    
    $(document).on("click", "#surface-rep", {'URL': URL, 'rep': 'surface'}, 
        function(event){ 
            event.preventDefault();
            myStage = loadStage(event.data.URL, event.data.rep)
        } );

    $(document).on("click", "#spacefill-rep", {'URL': URL, 'rep': 'spacefill'}, 
        function(event){ 
            event.preventDefault();
            myStage = loadStage(event.data.URL, event.data.rep)
        } );

    // Export image buttons
    $(document).on("click", "#normal", {'stage': myStage}, 
    function(event){ 
        event.preventDefault();
        myStage.makeImage( {
            factor: 1,
            antialias: true,
            trim: false,
            transparent: true,
        } ).then( function( blob ){
            NGL.download( blob, "molecule-view.png" );
        } );
    } );

    $(document).on("click", "#high", {'stage': myStage}, 
    function(event){ 
        event.preventDefault();
        myStage.makeImage( {
            factor: 5,
            antialias: true,
            trim: false,
            transparent: true,
        } ).then( function( blob ){
            NGL.download( blob, "molecule-view-high.png" );
        } );
    } );

    $(document).on("click", "#ultra-high", {'stage': myStage}, 
    function(event){ 
        event.preventDefault();
        myStage.makeImage( {
            factor: 10,
            antialias: true,
            trim: false,
            transparent: true,
        } ).then( function( blob ){
            NGL.download( blob, "molecule-view-ultra-high.png" );
        } );
    } );
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
        "resize": [resizeStructure, "viewCardHeight"],
    },
    "pdb": {
        "load" : [loadStructure, "href"],
        "resize": [resizeStructure, "viewCardHeight"],
    },
    "other": {
        "load": [loadOther, "href"],
        "resize": [resizeOther, "viewCardHeight"]
    },
}

$(document).ready(function() {
    let url = location.href.split('/');
    const jobID = url.slice(-1)[0];

    let content_div = document.getElementById('file-content');
    let cytoscape_div = document.getElementById('cytoscape');
    let ngl_div = document.getElementById('structure')
    $("#file-content").addClass("active-div")
    
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
            // Clear div content before new content loading 
            content_div.innerHTML = "";
            ngl_div.innerHTML = "";
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

    viewCardHeight = $(window).outerHeight()*0.85
    $("#outer-card").height(viewCardHeight*1)
    $("#js-tree").height(viewCardHeight*1)
    $("#file-content").height(viewCardHeight*0.90)

})

    