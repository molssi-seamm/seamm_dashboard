

export function buildFlowchart(url) {
    var elements = [];
    console.log(url)
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