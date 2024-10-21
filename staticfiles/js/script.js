document.addEventListener('DOMContentLoaded', function() {
    var heroCarousel = new bootstrap.Carousel(document.getElementById('heroCarousel'), {
        interval: 5000,  // Change slide every 5 seconds
        direction: 'left'  // Animate from right to left
    });
});