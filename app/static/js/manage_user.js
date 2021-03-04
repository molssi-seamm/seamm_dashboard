function toggleLock(span) {

    let section = span.section

    // delete old tooltips
    let tooltips = section.getElementsByClassName('tooltip')
    for (let k=0; tooltips.length; tooltips++) {
        tooltips[k].remove()
    }

    if (section.isDisabled) {

        // Put in new info and enable 
        span.innerHTML = '<button type="button" class="btn btn-secondary btn-lg" title="Section is unlocked for editing. Click to lock." data-toggle="tooltip" data-placement="top"><i class="fas fa-unlock"></i></button>'
        $(`#${section.id}`).tooltip()

        for (let i=0; i<section.fieldCollection.length; i++) {
            section.fieldCollection[i].disabled = false
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

    span.section = section
}

function getFormFields(section) {
    section.fieldCollection = []
    let inputFields = section.getElementsByTagName('input')

    for (let i=0; i<inputFields.length; i++) {
        section.fieldCollection.push(inputFields[i])
    }

    let selectFields = section.getElementsByTagName('select')
    
    for (let i=0; i<selectFields.length; i++) {
        section.fieldCollection.push(selectFields[i])
    }
}

$(document).ready(function() {

    let submitButton = document.getElementById("submit")
    submitButton.disabled = true

    let spans = document.getElementsByClassName("edit-section")
    $('input').each(function() {
        $(this).attr("disabled", true)
    })

    $('select').each(function() {
        $(this).attr("disabled", true)
    })

    for(var i = 0; i < spans.length; i++){
        spans[i].innerHTML='<button type="button" class="btn btn-secondary btn-lg" title="Click to unlock and edit section." data-toggle="tooltip" data-placement="top"><i class="fas fa-lock"></i></button>';
        let sectionID = spans[i].id.split('-').slice(0,-1).join('-')

        spans[i].section = document.getElementById(sectionID)
        spans[i].section.isDisabled = true;

        getFormFields(spans[i].section)

        // Add tooltip
        $(`#${spans[i].id}`).tooltip()

        // Add button click behavior
        $(`#${spans[i].id}`).click( function() {

            toggleLock(this)
            submitButton.disabled = false

        })
    };

    $("#submit").click( function() {
        $('input').each(function() {
            $(this).removeAttr('disabled');
        })

        $('select').each(function() {
            $(this).removeAttr('disabled');
        })
    });
})

