from . import projects


@projects.route("/views/projects")
def project_list():
    return render_template("flowcharts/flowchart_list.html")
