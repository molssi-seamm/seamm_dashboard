from flask import render_template
from . import flowcharts


@flowcharts.route("/views/flowcharts")
def flowchart_list():
    return render_template("flowcharts/flowchart_list.html")


@flowcharts.route("/views/flowcharts/<id>")
@flowcharts.route("/views/flowcharts/<id>/<flowchart_keys>")
def flowchart_details(id):
    return render_template("flowcharts/render_flowchart.html")
