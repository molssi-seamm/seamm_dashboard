// Set time of last activity in local storage
// Each window has a time out. At time out, see time of last activity across all tabs stored in local storage.
// If time of last activity is longer ago than the time out time, log out.


function idleTimer() {
    let timeOutTime = 36000000 // timeout in milliseconds - 10 hours
    let activityTimer;

    if (localStorage.getItem('timeOfActivity') != null) {
        checkTimer()
    }


    window.onload = refresh_token;
    window.onmousemove = resetTimer; // catches mouse movements
    window.onmousedown = resetTimer; // catches mouse movements
    window.onclick = resetTimer;     // catches mouse clicks
    window.onscroll = resetTimer;    // catches scrolling
    window.onkeypress = resetTimer;  //catches keyboard actions

    resetTimer();

    function checkTimer() {
        let nowTime = new Date()
        let currentTime = nowTime.getTime()
        let elapsedTime = currentTime - localStorage.getItem('timeOfActivity')
        if (( elapsedTime >= timeOutTime)) {
            window.location.href = `${location.origin}/logout`;  // Logout user
        }
    }

   function refresh_token() {
    let d = new Date();
    localStorage.setItem('timeOfActivity', d.getTime())
    
    // Placeholder for token.
    let csrf_refresh;

    // Get the csrf refresh token
    document.cookie.split(";").forEach(function(value) { if (value.trim().split("=")[0] == 'csrf_refresh_token') { csrf_refresh = value.trim().split('=')[1] } })
   
    $.ajaxSetup({
        headers: { 'X-CSRF-TOKEN': csrf_refresh }
    })

    $.ajax({
        url: `${location.origin}/api/auth/token/refresh`,
        type: "POST",
        success: setTimeout(refresh_token, 3300000), // refresh the token every 55 minutes
        error: function () {
            // if this fails, the refresh token is expired and we remove the tokens.
            window.location.href =`${location.origin}/logout`;
         }
        })
  }

   function resetTimer() {
        let d = new Date();
        localStorage.setItem('timeOfActivity', d.getTime())
        clearTimeout(activityTimer);
        activityTimer = setTimeout(checkTimer, timeOutTime);  
    }
}
