document.addEventListener('DOMContentLoaded', function () {
    var heroCarousel = new bootstrap.Carousel(document.getElementById('heroCarousel'), {
        interval: 5000,  // Change slide every 5 seconds
        direction: 'left'  // Animate from right to left
    });

    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        setTimeout(function () {
            messagesContainer.style.opacity = '0';
            setTimeout(function () {
                messagesContainer.style.display = 'none';
            }, 1000);
        }, 5000);
    }

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
            container.innerHTML += `
                <div class="col">
                    <div class="card h-100">
                        <a href="/game/${game.game_id}" class="text-decoration-none">
                            <div class="card-img-container">
                                <img src="${game.thumbnail}" class="card-img-top" alt="${game.title}">
                            </div>
                        </a>
                        <div class="card-body font-main">
                            <h5 class="card-title font-banner">
                                <a href="/game/${game.game_id}" class="text-decoration-none game-title-link">${game.title}</a>
                            </h5>
                            <p class="game-price font-cta">${game.price.toFixed(2)} €</p>
                            <div class="card-text">
                                <small class="text-muted">${game.genre}</small>
                                <p class="mt-2 mb-0">${game.description.substring(0, 100)}...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
    }

    const toastElement = document.getElementById('deleteToast');
    if (toastElement) {
        const toast = new bootstrap.Toast(toastElement);
        let formToSubmit;

        document.querySelectorAll('.delete-button').forEach(button => {
            button.addEventListener('click', function () {
                formToSubmit = this.closest('form');
                toast.show();
            });
        });

        document.getElementById('confirmDelete').addEventListener('click', function () {
            formToSubmit.submit();
        });
    }
});