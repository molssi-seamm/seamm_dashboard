localStorage.removeItem('seammLogout')
localStorage.clear()
localStorage.setItem('seammLogin', 'login' + Math.random());
idleTimer()
window.location.href = '/'