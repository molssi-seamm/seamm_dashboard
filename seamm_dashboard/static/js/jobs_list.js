// You must include table_api.js on the html for this page.

$(document).ready(function () {
    let api_url = location.href.split('#')[1];
    let my_table = inittable(api_url);

    // Add action to refresh button
    $("#refresh").click(my_table.ajax.reload)


    let tableButtons = document.getElementsByClassName("dt-buttons")
    tableButtons[0].className = "row justify-content-end"

    let titleObject = document.getElementById('page-title')
    let titleSplit = api_url.toLowerCase().split('/')

    let myTitle = titleSplit.map(function(word) {
        return (word.charAt(0).toUpperCase() + word.slice(1));
      }).join(' ');

      myTitle = myTitle.replace('Projects', 'Project')

      titleObject.textContent = myTitle;

      if (titleSplit.includes('projects')){
        titleSplit.pop()
        let my_url = titleSplit.join('/')
        ajaxProjectDescription(my_url)
      }

      document.getElementById("view").classList.toggle("hidden")

    
})

