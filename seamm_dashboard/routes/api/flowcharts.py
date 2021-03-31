"""
API calls for flowcharts
"""

from seamm_dashboard.models import Flowchart, FlowchartSchema
from flask import Response
from flask_jwt_extended import jwt_required

from seamm_dashboard import authorize

__all__ = ["get_flowcharts", "get_flowchart", "get_cytoscape"]


@jwt_required(optional=True)
def get_flowcharts(description=None, limit=None):

    # If limit is not set, set limit to all jobs in DB.
    if limit is None:
        limit = Flowchart.query.count()

    if description is not None:
        flowcharts = Flowchart.query.filter(
            Flowchart.description.contains(description), Flowchart.authorized("read")
        ).limit(limit)
    else:
        flowcharts = Flowchart.query.filter(Flowchart.authorized("read")).limit(limit)

    flowcharts_schema = FlowchartSchema(many=True)

    return flowcharts_schema.dump(flowcharts), 200


@jwt_required(optional=True)
def get_flowchart(id):
    """
    Function for api endpoint api/flowcharts/{id}

    Parameters
    ----------
    id : the ID of the flowchart to return
    """
    flowchart = Flowchart.query.get(id)

    if flowchart is None:
        return Response(status=404)

    if not authorize.read(flowchart):
        return Response(status=401)

    flowchart_schema = FlowchartSchema(many=False)
    return flowchart_schema.dump(flowchart), 200


@jwt_required(optional=True)
def get_cytoscape(id, flowchartKeys=None):
    """
    Function for getting cytoscape elements for a flowchart.
    """

    flowchart = Flowchart.query.get(id)

    if flowchart is None:
        return Response(status=404)

    if not authorize.read(flowchart):
        return Response(status=401)

    important_stuff = {}
    important_stuff = flowchart.json
    # description = important_stuff['nodes'][0]['attributes']['_description']

    elements = []

    for node_number, node in enumerate(important_stuff["nodes"]):
        url = "#"
        # Build elements for cytoscape
        elements.append(
            {
                "data": {
                    "id": node["attributes"]["_uuid"],
                    "name": node["attributes"]["_title"],
                    "url": url,
                },
                "position": {
                    "x": node["attributes"]["x"],
                    "y": node["attributes"]["y"],
                },
                "description": "",
            }
        )

    for edge in important_stuff["edges"]:
        node1_id = edge["node1"]
        node2_id = edge["node2"]
        edge_data = {
            "data": {
                "id": str(node1_id) + "_" + str(node2_id),
                "source": node1_id,
                "target": node2_id,
            },
        }

        elements.append(edge_data)
    return elements, 201
