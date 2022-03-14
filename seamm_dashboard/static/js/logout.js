// Make sure local storage is clear
localStorage.removeItem('timeOfActivity')
localStorage.removeItem('seammLogin')

localStorage.setItem('seammLogout', 'logout' + Math.random());
window.location.assign(window.location.origin)