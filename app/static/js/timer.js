function idleTimer() {
    var activityTimer;
    window.onload = refresh_token;
    window.onmousemove = resetTimer; // catches mouse movements
    window.onmousedown = resetTimer; // catches mouse movements
    window.onclick = resetTimer;     // catches mouse clicks
    window.onscroll = resetTimer;    // catches scrolling
    window.onkeypress = resetTimer;  //catches keyboard actions

    function logout() {
        window.location.href = '/auth/logout';  //Adapt to actual logout script
    }

   function refresh_token() {
    $.ajax({
        url: `/api/auth/token/refresh`,
        type: "POST",
        success: setTimeout(refresh_token, 3300000), // refresh the token every 55 minutes
        error: function () {
            // if this fails, the refresh token is expired and we remove the tokens.
            $.ajax({
                url: `auth/logout`,
                complete: location.relaod(),
                })
         }
        })
  }

   function resetTimer() {
        clearTimeout(activityTimer);
        activityTimer = setTimeout(logout, 1200000);  // logout after 20 minutes of inactivity
    }
}