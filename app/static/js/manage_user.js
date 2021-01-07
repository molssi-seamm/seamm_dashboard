function toggleLock(span) {

    section = span.section

    // delete old tooltips
    tooltips = section.getElementsByClassName('tooltip')
    for (let k=0; tooltips.length; tooltips++) {
        tooltips[k].remove()
    }

    if (section.isDisabled) {

        // Put in new info and enable 
        span.innerHTML = '<button type="button" class="btn btn-secondary btn-lg" title="Section is unlocked for editing. Click to lock." data-toggle="tooltip" data-placement="top"><i class="fas fa-unlock"></i></button>'
        $(`#${section.id}`).tooltip()

        for (let i=0; i<section.fieldCollection.length; i++) {
            section.fieldCollection[i].disabled = false
            console.log('hello')
        }

        section.isDisabled = false;
        
    }

    else {
        span.innerHTML = '<button type="button" class="btn btn-secondary btn-lg" title="Click to unlock and edit section." data-toggle="tooltip" data-placement="top"><i class="fas fa-lock"></i></button>'
        $(`#${section.id}`).tooltip()

        for (let i=0; i<section.fieldCollection.length; i++) {
            section.fieldCollection[i].disabled = true
        }

        section.isDisabled = true;
    }
}

function getFormFields(section, disableSections = true) {
    section.fieldCollection = []
    section.isDisabled = true;
    let inputFields = section.getElementsByTagName('input')
    console.log(section)

    for (let i=0; i<inputFields.length; i++) {
        section.fieldCollection.push(inputFields[i])
        if (disableSections) {
            inputFields[i].disabled = true;
        } 
    }

    let selectFields = section.getElementsByTagName('select')
    
    for (let i=0; i<selectFields.length; i++) {
        section.fieldCollection.push(selectFields[i])
        if (disableSections) {
            selectFields[i].disabled = true;
        } 
    }
}

$(document).ready(function() {

    let submitButton = document.getElementById("submit")
    submitButton.disabled = true

    let spans = document.getElementsByClassName("edit-section")
    let spanIDs = [];
    let sectionFields = [];

    for(var i = 0; i < spans.length; i++){
        spans[i].innerHTML='<button type="button" class="btn btn-secondary btn-lg" title="Click to unlock and edit section." data-toggle="tooltip" data-placement="top"><i class="fas fa-lock"></i></button>';
        let sectionID = spans[i].id.split('-').slice(0,-1).join('-')

        spans[i].section = document.getElementById(sectionID)

        getFormFields(spans[i].section)
        console.log(spans[i].fieldCollection)

        // Add tooltip
        $(`#${spans[i].id}`).tooltip()

        // Add button click behavior
        $(`#${spans[i].id}`).click( function() {

            toggleLock(this)
            submitButton.disabled = false

        })
        
    };

    $("#submit").click( function() {

        for (let i = 0; i < spanIDs.length; i++ ) {
            for (let j=0; j < sectionFields[i].length; j++ ) {
                sectionFields[i][j].disabled = false
            }
            };
        });
    })

