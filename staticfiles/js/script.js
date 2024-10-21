document.addEventListener('DOMContentLoaded', function() {
    var heroCarousel = new bootstrap.Carousel(document.getElementById('heroCarousel'), {
        interval: 5000,  // Change slide every 5 seconds
        direction: 'left'  // Animate from right to left
    });
});

// Add this to the end of your existing script.js file

document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        setTimeout(function() {
            messagesContainer.style.opacity = '0';
            setTimeout(function() {
                messagesContainer.style.display = 'none';
            }, 1000);
        }, 5000);
    }
});