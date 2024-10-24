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
