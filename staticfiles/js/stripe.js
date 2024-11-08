/* jshint esversion: 11*/
const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.slice(1, -1);
const clientSecret = document.getElementById('id_client_secret').textContent.slice(1, -1);
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

const style = {
    base: {
        color: '#000',
        fontFamily: '"Noto Sans", sans-serif',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

const card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors
card.addEventListener('change', function (event) {
    const errorDiv = document.getElementById('card-errors');
    if (event.error) {
        errorDiv.textContent = event.error.message;
    } else {
        errorDiv.textContent = '';
    }
});

// Add this after your existing code
const form = document.getElementById('payment-form');
form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true});
    document.getElementById('submit-button').disabled = true;

    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) {
        if (result.error) {
            const errorDiv = document.getElementById('card-errors');
            errorDiv.textContent = result.error.message;
            card.update({ 'disabled': false});
            document.getElementById('submit-button').disabled = false;
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});


