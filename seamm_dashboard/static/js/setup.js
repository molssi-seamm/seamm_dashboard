// Set up the main window - load in appropriate menus for login, user, dashboard name.

// Prevent caching on ajax calls.
$.ajaxSetup ({
    cache: false
    });

    // Get username and dashboard name and stuff
    $.ajax({
    url: `${location.origin}/api/status`,
    dataType: 'json',
    async: false,
    success: function (data) {
        let loginString;
        if (data.username == "Anonymous User") {
          
          loginString = `
          <li class="nav-item dropdown mr-5 pr-5">    
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Public User
          </a>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
              <a class="dropdown-item" href="login">Log In</a>
          </div>
      </li>
          `
        }

        else {
          loginString = `
          <li class="nav-item dropdown mr-5 pr-5">    
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Logged in as <strong>${data.username}</strong>
                </a>
                <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">`
          
            if (data.roles.includes("admin")) {
              loginString = loginString.concat(`<h6 class="dropdown-header">Admin Actions</h6>
              <a class="dropdown-item" href="/admin/manage_users">Manage Users</a>
              <a class="dropdown-item" href="/admin/manage_groups">Manage Groups</a>`)
            }

            if (data.roles.includes("group manager")) {
              loginString = loginString.concat(`<h6 class="dropdown-header">Manager Actions</h6>
              <a class="dropdown-item" href="/admin/manage_groups">Manage Groups</a>`)
            }

          loginString = loginString.concat(`
                    <h6 class="dropdown-header">User Actions</h6>
                    <a class="dropdown-item" href="${location.origin}/my-account">My Account</a>
                    <a class="dropdown-item" href="${location.origin}/logout">Logout</a>
          `)
          
          loginString = loginString.concat(`</div>
          </li>`)
        }

        document.getElementById("login-info").innerHTML = loginString
        document.getElementById("dashboard-name").innerHTML = `<h2>${data.dashboard}</h2>`
        },
        // error occurs because of expired access token. Remove cookie and reload page
    error: function () {
      // if this fails, the refresh token is expired and we remove the tokens.
      window.location.href = `${location.origin}/logout`;
        } 
      })

      window.addEventListener('storage', function(event){
        if (event.key == 'seammLogin') { 
          location.reload()
        }
        if (event.key == 'seammLogout') { 
          $.ajax({
            url: `${location.origin}/logout`,
            complete: function() {
              localStorage.removeItem('seammLogout')
              location.reload()
            }
          })
        }

      })
