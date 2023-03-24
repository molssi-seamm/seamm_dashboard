// You must include table_api.js on the html for this page.

// Wait for the document to be fully loaded before executing the code
$(document).ready(function () {
  // Get the URL fragment identifier (everything after the #)
  let api_url = location.href.split('#')[1];

  // Initialize the DataTables table using the URL fragment identifier
  let my_table = inittable(api_url);

  // Add an event listener to the "refresh" button to reload the table data
  $("#refresh").click(my_table.ajax.reload);

  // Set the position of the DataTables table buttons to the right of the page
  let tableButtons = document.getElementsByClassName("dt-buttons");
  tableButtons[0].className = "row justify-content-end";

  // Get the page title element and split the URL fragment identifier into parts
  let titleObject = document.getElementById('page-title');
  let titleSplit = api_url.toLowerCase().split('/');

  // Format the title based on the parts of the URL fragment identifier
  let myTitle = titleSplit.map(function(word) {
      return (word.charAt(0).toUpperCase() + word.slice(1));
    }).join(' ');

  myTitle = myTitle.replace('Projects', 'Project');

  // Set the text content of the page title element to the formatted title
  titleObject.textContent = myTitle;

  // Check if the URL fragment identifier includes the string 'projects'
  if (titleSplit.includes('projects')) {
      // Get the project ID from the URL fragment identifier
      let projectId = titleSplit[1];

      // Call the API with the project ID to get the project details
      fetch('/api/projects/' + projectId)
          .then(response => response.json())
          .then(data => {
              // Set the title to the project name
              let projectName = data.name;
              titleObject.textContent = projectName;
              
              // Set the description to the project description
              let projectDescription = data.description;
              ajaxProjectDescription(projectDescription);
          })
          .catch(error => console.error(error));
  }

  // Toggle the visibility of the "view" element and set the value of "previous"
  document.getElementById("view").classList.toggle("hidden");
  previous = window.location.href;
});

// Update the project description element with the given description text
function ajaxProjectDescription(description) {
  let descriptionObject = document.getElementById('description');
  if (description) {
      descriptionObject.textContent = description;
  }
}


