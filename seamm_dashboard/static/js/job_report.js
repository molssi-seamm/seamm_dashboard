// You must include util.js on any page that uses this javascript file

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
    let location = document.getElementById("file-name").getBoundingClientRect();
    let headerLocation = document.querySelector(".app-header").getBoundingClientRect()
    let viewCardHeight = $(window).innerHeight() - location.bottom - headerLocation.bottom

    let divs = Array.from(document.querySelectorAll(".load-content"))

    for (var i=0; i<divs.length; i++) {
        if (divs[i].tagName != "TABLE") {
            divs[i].style.height = `${viewCardHeight}px`;
        }
    }

    let jsTree= document.getElementById("js-tree");
    let searchLocation = document.getElementById('search').getBoundingClientRect()
    let jsHeight = viewCardHeight - (searchLocation.bottom - location.bottom)
    jsTree.style.height = `${jsHeight}px`;

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
}

function loadGraph(nodeData) {
    let content_div = document.getElementById('file-content');
    var plotlyData = load_file(nodeData.a_attr.href, 'json')
    Plotly.newPlot(content_div, plotlyData.data, plotlyData.layout, 
        {'editable': true, 
        'toImageButtonOptions': {
        format: 'png', // one of png, svg, jpeg, webp
        filename: nodeData.text,
        scale: 10 // Multiply title/legend/axis/canvas sizes by this factor
        }});

}

function loadTable(href) {
    try {
        table.destroy();
        $('#csv-data tr').remove();
        $('#csv-data thead').remove();
        $('#csv-data tbody').remove();
    } catch {
        // Do nothing.
    }

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

}

function loadOther(file) {
    var fileType = file.split(".").slice(-1);
    $("#file-content").html(`<pre style="white-space:pre-wrap;" id="pre-code"><code id="codeBlock" class="language-${fileType} animated fadeIn"></code>`)
    $("#codeBlock").load(file, function(data){ 
        if (data.length < 75000) {
            $("#pre-code").addClass('line-numbers')
            }
        Prism.highlightAll() });
}

function loadDescription(description) {
    $("#file-content").html(`<pre style="white-space:pre-wrap;" id="pre-code"><code id="codeBlock" class="language-text animated fadeIn"></code>`)
    
    if (description.length < 75000) {
        $("#pre-code").addClass('line-numbers')
    }

    description = "Job Description:\n" + description

    $("#codeBlock").text(description)
        
    Prism.highlightAll();
}

function loadStructure(URL) {
    
    // Inner function for NGL stage - only used in this function
    function loadStage(URL, representation="default") {
        
        // Clear stage if one exists
        let canvas = document.querySelector("#structure canvas")
        if (canvas) {
            canvas.remove()}

        // Figure out the file extension and load the file
        let fileExtension = URL.split(".");
        fileExtension = fileExtension[fileExtension.length - 1]
        let stage = new NGL.Stage("structure", {backgroundColor: "white"} );

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
    let myStage;
    myStage = loadStage(URL);

    // Add behavior for representation buttons.
    let representations = {
                    "#default-rep": "default",
                    "#licorice-rep": "licorice", 
                    "#cartoon-rep": "cartoon", 
                    "#ball-stick-rep": "ball+stick", 
                    "#surface-rep": "surace", 
                    "#spacefill-rep":"spacefill"
                }
    
    for (let key in representations){

        let rep = representations[key]
        $(document).on("click", `${key}`, {'URL': URL, 'rep': rep},
        function(event){ 
        event.preventDefault();
        myStage = loadStage(event.data.URL, event.data.rep);
        });
    }

    // Export image buttons
    let qualities = {
        "normal": 1,
        "high": 5,
        "ultra-high": 10,
    }

    for (let key in qualities){
        // Remove previous behavior
        $(document).off("click", `#${key}`)

        $(document).on("click", `#${key}`, {'stage': myStage}, 
            function(event){ 
                event.preventDefault();
                myStage.makeImage( {
                    factor: qualities[key],
                    antialias: true,
                    trim: false,
                    transparent: true,
                } ).then( function( blob ){
                    NGL.download( blob, `molecule-view-${key}.png` );
                } );
            } );
    }
}

function toggleDivs(divList, divToShow = null) {
    for (var i = 0; i < divList.length; i++) {
        if (divList[i] == divToShow) {
            document.getElementById(divList[i]).classList.remove("hidden")
        }
        else {
            document.getElementById(divList[i]).classList.add("hidden")
        }
    }
};

var contentFunctions = {
    "flow" : {
        "load": [loadFlow, "jobData.flowchart_id"],
        "resize": "cytoscape",
    },
    "graph": {
        "load": [loadGraph, "data.node"],
        "resize": "file-content",
    },
    "csv": {
        "load" : [loadTable, "href"],
        "resize": "csv-data",
    },
    "mmcif": {
        "load" : [loadStructure, "href"],
        "resize": "structure",
    },
    "cif": {
        "load" : [loadStructure, "href"],
        "resize": "structure",
    },
    "pdb": {
        "load" : [loadStructure, "href"],
        "resize": "structure",
    },
    "other": {
        "load": [loadOther, "href"],
        "resize": "file-content",
    },
}

var contentDivs = ["file-content", "structure","cytoscape", "csv-data"]

$(document).ready(function() {
    let url = location.href.split('/');
    const jobID = url.slice(-1)[0];

    // Get info we need for page
    let jobData = getJobData(jobID);
    let treeElements = buildTree(jobID);

    // add listener for resize event
    window.addEventListener('resize', setFileDivSize)

    // Load in the job status
    $("#job-status").html(jobData.status)
    $('#root-folder').text(treeElements[0].text)
    
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
             let divs = document.getElementsByClassName('load-content')
             
             for (var i=0; i<divs.length; i++) {
                 divs[i].innerHTML = "";
             }

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

            var http = new XMLHttpRequest();

            http.open('HEAD', href, false);
            http.send();

            // If logout is find, the index will be greater than -1
            if (http.responseURL.indexOf("logout") > -1) { 
                window.location.assign("/logout") 
            }

            // Figure out functions to call. If not recognized extension, other
            if (!(fileType in contentFunctions)) {
                fileType = "other"
            }

            //Resize divs appropriately.
            let resizeDiv = contentFunctions[fileType]["resize"]
            toggleDivs(contentDivs, resizeDiv)

            // Load function
            let func = contentFunctions[fileType]["load"][0]
            let arg = eval(contentFunctions[fileType]["load"][1])
            func(arg)
            
            // Make file refresh button work.
            $("#refresh").click(
                function() {
                func(arg)
            })
        }
    });

    // Make file list refresh button work.
    $("#refresh-file-list").click(
        function() {
            document.getElementById("js-tree").classList.toggle("hidden")
            newData = buildTree(jobID)
            $('#js-tree').jstree(true).settings.core.data = newData;
            $('#js-tree').jstree("refresh")
            document.getElementById("js-tree").classList.toggle("hidden")

            // Update the job data and status.
            jobData = getJobData(jobID);
            $("#job-status").html(jobData.status);
            $("#job-title").html(jobData.title);
        }
    )


    toggleDivs(contentDivs, "file-content")
    
    // Show content
    document.getElementById("view").classList.toggle("hidden")
    setFileDivSize()

    if ( jobData["description"] ) { 
        loadDescription(jobData["description"])
    }

    $("#load-description").click(function() {
        try {
            table.destroy();
            $('#csv-data tr').remove();
            $('#csv-data thead').remove();
            $('#csv-data tbody').remove();
        } catch {
            // Do nothing.
        }
        toggleDivs(contentDivs, "file-content")
        loadDescription(jobData["description"]);

    })
    

})

    
