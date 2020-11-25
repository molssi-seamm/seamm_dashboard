// Prevent caching on ajax calls.
$.ajaxSetup ({
    cache: false
    });

    // Get username and stuff
    $.ajax({
    url: `api/status`,
    dataType: 'json',
    async: false,
    success: function (data) {
        //console.log(data)
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
                <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                    <a class="dropdown-item" href="#">Manage Account</a>
                    <a class="dropdown-item" href="logout">Logout</a>
          `
          if (data.roles.includes("admin")) {
              console.log("admin")
            loginString = loginString.concat(`<h6 class="dropdown-header">Admin Actions</h6>
            <a class="dropdown-item" href="#">Manage Users</a>`)
            console.log(loginString)
          }
          
          loginString = loginString.concat(`</div>
          </li>`)
        }

        document.getElementById("login-info").innerHTML = loginString

        if (data.username != "Anonymous User") {
          idleTimer()
        }
       
        },
        // error occurs because of expired access token. Remove cookie and reload page
        error: function () {
          $.ajax({
            url: `logout`,
            complete: location.reload()
          })
          
        },
      })

      window.addEventListener('storage', function(event){
        if (event.key == 'login-event') { 
          location.reload()
        }
        if (event.key == 'logout-event') { 
          $.ajax({
            url: `auth/logout`,
            complete: function() {
              location.reload()
            }
          })
        }

      })
