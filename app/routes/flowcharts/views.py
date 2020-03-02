from flask import request, render_template, flash, g, \
                render_template_string, session, \
                redirect, url_for, abort, jsonify, send_from_directory,\
                current_app
import os
import json
from . import flowcharts
import logging
import random

#import seamm
#import subprocess

from app.routes.jobs.forms import EditJob
from app.models import Job, Flowchart

@flowcharts.route("/views/flowcharts")
def flowchart_list():
    return render_template("flowcharts/flowchart_list.html")

@flowcharts.route('/views/flowcharts/<id>')
@flowcharts.route('/views/flowcharts/<id>/<flowchart_keys>')
def flowchart_details(id, flowchart_keys=None):
    
    this_url = 'flowchart_details_{}_{}'.format(id,flowchart_keys)

    flowchart = Flowchart.query.get(id)

    if flowchart_keys is None:
        flowchart_keys = 'flowchart_json'

    important_stuff = {}
    important_stuff['flowchart_json'] = flowchart.flowchart_json

   
    for key in flowchart_keys.split(','):
        if isinstance(important_stuff, list):
            key = int(key)
        important_stuff = important_stuff[key]

    
    description = important_stuff['nodes'][0]['attributes']['_description']

    elements = []

    for node_number, node in enumerate(important_stuff['nodes']):
        
        ## Build URLs for nodes with subflowcharts
        node_keys = flowchart_keys
        node_keys += ',nodes'

        original_length = len(node_keys)
        
        for key in node.keys():
            if 'flowchart' in key.lower():
                node_keys += ",{}".format(node_number)
                node_keys += ",{}".format(key)
        
        url = "#"

        if len(node_keys) > original_length:
            url=url_for('flowcharts.flowchart_details', id=id, flowchart_keys=node_keys)

        
        ## Build elements for cytoscape
        elements.append({'data': {
            'id': node['attributes']['_uuid'],
            'name': node['attributes']['_title'],
            'url': url,
            
        },
        'position': {
                "x": node['attributes']['x'],
                "y": node['attributes']['y']
            },

        'description': "",                
        })
        

    for edge in important_stuff['edges']:
        node1_id = edge['node1']
        node2_id = edge['node2']
        edge_data = {'data':
            {
                'id': str(node1_id) + '_' + str(node2_id),
                'source': node1_id, 
                'target': node2_id
            },
            
        }

        elements.append(edge_data)

    flowchart_text = render_template('js/flowchart.js', data=elements)

    tmp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'static', 'tmp', this_url +'.js.tmp')

    with open(tmp_file, 'w+') as f:
        f.write(flowchart_text)
    
    tmp_file_name = url_for('static', filename='tmp/'+os.path.basename(tmp_file))

    return render_template('flowcharts/render_flowchart.html', description=description, js_file=tmp_file_name)