/* jshint esversion: 11*/
document.addEventListener('DOMContentLoaded', function () {
    // Safely initialize carousel
    const heroCarouselElement = document.getElementById('heroCarousel');
    if (heroCarouselElement && typeof bootstrap !== 'undefined') {
        new bootstrap.Carousel(heroCarouselElement, {
            interval: 5000,
            direction: 'left'
        });
    }

    // Message handling
    const messages = document.querySelectorAll('.messages-container');
    messages.forEach(message => {
        if (message) {
            // Set initial state
            message.style.opacity = '1';
            message.style.transition = 'opacity 1s ease-out';
            
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 1000);
            }, 5000);
        }
    });

    var usernameField = document.getElementById('id_username');
    if (usernameField) {
        usernameField.placeholder = 'Username';
    }

    var emailField = document.getElementById('id_email');
    if (emailField) {
        emailField.classList.add('form-control');
        emailField.placeholder = 'Enter your email';
    }

    const descriptionLabel = document.querySelector('label[for="id_description"]');
    if (descriptionLabel) {
        const lineBreak = document.createElement('br');
        descriptionLabel.parentNode.insertBefore(lineBreak, descriptionLabel.nextSibling);
    }

    const filterByPriceButton = document.getElementById('filterByPrice');
    const filterByRecentButton = document.getElementById('filterByRecent');
    const filterByRatingButton = document.getElementById('filterByRating');
    const filterByPopularButton = document.getElementById('filterByPopular');

    if (filterByPriceButton) {
        filterByPriceButton.addEventListener('click', function() {
            fetchAndUpdateGames('price');
        });
    }

    if (filterByRecentButton) {
        filterByRecentButton.addEventListener('click', function() {
            fetchAndUpdateGames('recent');
        });
    }

    if (filterByRatingButton) {
        filterByRatingButton.addEventListener('click', function() {
            fetchAndUpdateGames('highest_rated');
        });
    }

    if (filterByPopularButton) {
        filterByPopularButton.addEventListener('click', function() {
            fetchAndUpdateGames('popular');
        });
    }

    function fetchAndUpdateGames(filterType) {
        fetch(`/filter-games/?filter=${filterType}`)
            .then(response => response.json())
            .then(games => {
                updateGameCards(games);
            });
    }

    function updateGameCards(games) {
        const container = document.getElementById('gameCardContainer');
        container.innerHTML = '';
        games.forEach(game => {
            const ratingHtml = game.avg_rating > 0 
                ? `<span>★ ${game.avg_rating.toFixed(1)} (${game.review_count} reviews)</span>`
                : `<span class="text-muted">No ratings yet</span>`;

            container.innerHTML += `
                <div class="col mb-4">
                    <div class="card">
                        <a href="/game/${game.game_id}" class="text-decoration-none">
                            <div class="card-img-container">
                                <img src="${game.thumbnail}" class="card-img-top" alt="${game.title}">
                            </div>
                        </a>
                        <div class="card-body font-main">
                            <h5 class="card-title font-banner">
                                <a href="/game/${game.game_id}" class="text-decoration-none game-title-link">${game.title}</a>
                            </h5>
                            <div class="text-warning mb-2">
                                ${ratingHtml}
                            </div>
                            <p class="game-price font-cta mb-2">${game.price.toFixed(2)} €</p>
                            <div class="card-text">
                                <small class="text-muted d-block mb-2">${game.genre}</small>
                                <p class="mb-0">${game.description.substring(0, 100)}...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
    }

    const toastElement = document.getElementById('deleteToast');
    if (toastElement && typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const toast = new bootstrap.Toast(toastElement);
        let formToSubmit;

        document.querySelectorAll('.delete-button').forEach(button => {
            button.addEventListener('click', function () {
                formToSubmit = this.closest('form');
                toast.show();
            });
        });

        document.getElementById('confirmDelete')?.addEventListener('click', function () {
            if (formToSubmit) {
                formToSubmit.submit();
            }
        });
    }
});