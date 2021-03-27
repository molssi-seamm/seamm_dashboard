
function getDescription() {
  var description = '';
  var url = location.href.split('/')
    var flowchart_id = url.slice(-1)[0]
        $.ajax({
            url: `api/flowcharts/${flowchart_id}`,
            async: false,
            dataType: 'json',
            success: function (data) {
                description = data.description
            }
        });
    return description
    }

function buildFlowchart(url) {
  var elements = [];
  var url = location.href.split('/')
  var flowchart_id = url.slice(-1)[0]
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

$(document).ready(function(){

  var page_url = location.href.split('/')
  var flowchart_description = getDescription()

  $('#description').html(flowchart_description)

  var cytoscape_elements = buildFlowchart(page_url)

  var cy = window.cy = cytoscape({
      container: document.getElementById('cy'),
    
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
    
      elements: cytoscape_elements,
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
    
    
    cy.on('tap', 'node', function(){
    
      if (this.data('url') != '#') {
    
      try { // your browser may block popups
        window.open(this.data('url'))
      } catch(e){ // fall back on url change
        window.location.href = this.data('url');
      }
    
      }
    
    });  
    
    document.getElementById("view").classList.toggle("hidden")

})



