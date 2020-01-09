
  window.addEventListener('DOMContentLoaded', function(){

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

        elements:
        [
          {% for element in data %}

            {
            {% for key, value in element.items() %}
                {%- if value is mapping -%}
                  '{{ key|safe }}' : {{ value|safe }},
                {%- else -%}
                  '{{ key|safe }}' : '{{ value|safe }}',
                {% endif %}
            {% endfor %}
            },
          {%- endfor -%}
        ]
      });

      cy.nodes('[name = "Join"]').style( {
              'shape': 'ellipse',
              'background-color': '#000000',
              'label': 'data(name)',
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


      });