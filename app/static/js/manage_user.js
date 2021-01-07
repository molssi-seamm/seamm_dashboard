$(document).ready(function() {

    let submitButton = document.getElementById("submit")
    submitButton.disabled = true

    let spans = document.getElementsByClassName("edit-section")
    let spanIDs = [];
    let sectionFields = [];

    for(var i = 0; i < spans.length; i++){

        spans[i].innerHTML='<button type="button" class="btn btn-secondary" title="Click to unlock and edit section." data-toggle="tooltip" data-placement="top"><i class="fas fa-lock"></i></button>';
        
        spanIDs.push(spans[i].id)
        let sectionID = spans[i].id.split('-').slice(0,-1).join('-')

        let fieldCollection = []
        
        let inputFields = document.getElementById(sectionID).getElementsByTagName('input')

        for (let j = 0; j < inputFields.length; j++) {
            inputFields[j].disabled = true;
            fieldCollection.push(inputFields[j])
        }

        let selectFields = document.getElementById(sectionID).getElementsByTagName('select')

        for (let j = 0; j < selectFields.length; j++) {
            selectFields[j].disabled = true;
            fieldCollection.push(selectFields[j])
        }

        sectionFields.push(fieldCollection)
        
    };

    $('[data-toggle="tooltip"]').tooltip()

    // Add button press actions
    for (let i = 0; i < spanIDs.length; i++ ) {
        $(`#${spanIDs[i]}`).click( function() {
            let button = document.getElementById(spanIDs[i])
            button.innerHTML='<button type="button" class="btn btn-secondary" title="Section is unlocked for editing." data-toggle="tooltip" data-placement="top"><i class="fas fa-unlock"></i></button>'
            
            for (let j=0; j < sectionFields[i].length; j++ ) {
                sectionFields[i][j].disabled = false
            }
            // enable the submit button
            submitButton.disabled = false;
            
            // Remove tooltip
            tooltips = document.getElementsByClassName('tooltip')
            for (let k=0; tooltips.length; tooltips++) {
                tooltips[k].remove()
            }

        });
    }

    $("#submit").click( function() {

        for (let i = 0; i < spanIDs.length; i++ ) {
            for (let j=0; j < sectionFields[i].length; j++ ) {
                sectionFields[i][j].disabled = false
            }
    
            };
        });
    })

