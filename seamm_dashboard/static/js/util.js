var previous;

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

function getJobData(jobID) {
    var jobData = {};
    $.ajax({
    url: `api/jobs/${jobID}`,
    dataType: 'json',
    async: false,
    success: function (data) {
        jobData = data;
        },
    })
    return jobData
}

function buildCytoGraph(elements, container_id) {
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
