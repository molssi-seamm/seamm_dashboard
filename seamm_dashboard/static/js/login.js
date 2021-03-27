localStorage.removeItem('seammLogout')
localStorage.removeItem('timeOfActivity')
localStorage.clear()
localStorage.setItem('seammLogin', 'login' + Math.random());
idleTimer()
window.location.href = '/'