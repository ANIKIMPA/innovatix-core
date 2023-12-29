// Set your publishable key: remember to change this to your live publishable key in production
// See your keys here: https://dashboard.stripe.com/apikeys
const stripe = Stripe(stripePublicKey);
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const options = {
    mode: 'subscription',
    amount: subtotal,
    currency: 'usd',
    paymentMethodCreation: 'manual',
    // Fully customizable with appearance API.
    appearance: {
        theme: 'stripe',
        labels: 'floating',

        variables: {
            colorPrimary: '#0570de',
            colorBackground: '#ffffff',
            colorText: '#30313d',
            colorDanger: '#df1b41',
            fontFamily: 'Ideal Sans, system-ui, sans-serif',
            spacingUnit: '2px',
            borderRadius: '4px',
            spacingGridRow: '1rem',
            // See all possible variables below
        }
    },
};

// Set up Stripe.js and Elements to use in checkout form
const elements = stripe.elements(options);

// Create and mount the Payment Element
const paymentElement = elements.create('payment', {
    layout: {
        type: 'tabs',
        defaultCollapsed: false,
    }
});
paymentElement.mount('#payment-element');

const form = document.getElementById('id_payment_form');
const cardNameInput = document.getElementById("id_card_name")
const submitBtn = document.getElementById('id_btn_submit');
const messageContainer = document.querySelector('#error-message');

paymentElement.on('change', function(event) {
    if (event.complete) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
});

const handleError = (error) => {
    messageContainer.textContent = error.message;
    submitBtn.disabled = false;
}

// Check for the client_secret in the URL
const urlParams = new URLSearchParams(window.location.search);
const clientSecret = urlParams.get('client_secret');

if (clientSecret) {
    // Handle next action with client_secret
    stripe.handleNextAction({clientSecret})
    .then(function(result) {
        if (result.error) {
            handleError(result.error);
        } else {
            // Redirect to success page or handle additional success logic
            window.location.href = '/pago-completado/';
        }
    });

    // Remove the client_secret parameter from the URL
    urlParams.delete('client_secret');
    const newUrl = `${window.location.protocol}//${window.location.host}${window.location.pathname}?${urlParams.toString()}`;
    window.history.replaceState({}, '', newUrl);
}

form.addEventListener('submit', async (event) => {
    // We don't want to let default form submission happen here,
    // which would refresh the page.
    event.preventDefault();

    // Prevent multiple form submissions
    if (submitBtn.disabled) {
        return;
    }

    // Disable form submission while loading
    submitBtn.disabled = true;

    // Trigger form validation and wallet collection
    const {error: submitError} = await elements.submit();
    if (submitError) {
        handleError(submitError);
        return;
    }

    // Create the PaymentMethod using the details collected by the Payment Element
    const {error, paymentMethod} = await stripe.createPaymentMethod({
        elements,
        params: {
            billing_details: {
                name: cardNameInput.value,
            }
        }
    });

    if (error) {
        // This point is only reached if there's an immediate error when
        // creating the PaymentMethod. Show the error to your customer (for example, payment details incomplete)
        handleError(error);
        return;
    }

    const paymentMethodIdInput = document.getElementById("id_payment_method_id")
    paymentMethodIdInput.value = paymentMethod.id;

    form.submit();
});