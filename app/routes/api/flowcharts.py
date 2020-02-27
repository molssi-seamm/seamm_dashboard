"""
API calls for flowcharts
"""

from app.models import Flowchart, FlowchartSchema
from flask import Response

__all__ = ['get_flowcharts', 'get_flowchart']

def get_flowcharts(description=None, limit=None):
    
    # If limit is not set, set limit to all jobs in DB.
    if limit is None:
        limit = Flowchart.query.count()
    
    if description is not None:
        flowcharts = Flowchart.query.filter(Flowchart.description.contains(description)).limit(limit)
    else:
        flowcharts = Flowchart.query.limit(limit)

    flowcharts_schema = FlowchartSchema(many=True)
    
    return flowcharts_schema.dump(flowcharts), 200

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

    flowchart_schema = FlowchartSchema(many=False)
    return flowchart_schema.dump(flowchart), 200