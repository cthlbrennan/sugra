document.addEventListener('DOMContentLoaded', function () {
    var heroCarousel = new bootstrap.Carousel(document.getElementById('heroCarousel'), {
        interval: 5000,  // Change slide every 5 seconds
        direction: 'left'  // Animate from right to left
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        setTimeout(function () {
            messagesContainer.style.opacity = '0';
            setTimeout(function () {
                messagesContainer.style.display = 'none';
            }, 1000);
        }, 5000);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var usernameField = document.getElementById('id_username');
    if (usernameField) {
        usernameField.placeholder = 'Username';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var emailField = document.getElementById('{{ form.email.id_for_label }}');
    if (emailField) {
        emailField.classList.add('form-control');
        emailField.placeholder = 'Enter your email';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const descriptionLabel = document.querySelector('label[for="id_description"]');
    if (descriptionLabel) {
        const lineBreak = document.createElement('br');
        descriptionLabel.parentNode.insertBefore(lineBreak, descriptionLabel.nextSibling);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const filterByPriceButton = document.getElementById('filterByPrice');
    if (filterByPriceButton) {
        filterByPriceButton.addEventListener('click', function() {
            fetch('/filter-games/?filter=price')
                .then(response => response.json())
                .then(games => {
                    const container = document.getElementById('gameCardContainer');
                    container.innerHTML = '';
                    games.forEach(game => {
                        container.innerHTML += `
                            <div class="col">
                                <div class="card h-100">
                                    <div class="card-img-container">
                                        <img src="${game.thumbnail}" class="card-img-top" alt="${game.title}">
                                    </div>
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
                });
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const toastElement = document.getElementById('deleteToast');
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
});