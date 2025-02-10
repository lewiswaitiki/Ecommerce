// Profile update alert
document.querySelector('.profile-form').addEventListener('submit', function(event) {
  alert('Profile updated successfully!');
});

// Login form action
document.querySelector('.login-form').addEventListener('submit', function(event) {
  alert('Login successful');
  event.target.submit();
});


