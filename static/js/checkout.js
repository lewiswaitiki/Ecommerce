// Global modal + message elements
const modal = document.getElementById("payment-modal");
const messageBox = document.getElementById('payment-message');
const message = document.getElementById("payment-message-modal");

// Utility functions
function openModal(text, type = "") {
    message.textContent = text;
    modal.hidden = false;

    // Reset classes
    messageBox.classList.remove("success", "error");
    message.classList.remove("success", "error");

    if (type === "success") {
        messageBox.classList.add("success");
        message.classList.add("success");
    } else if (type === "error") {
        messageBox.classList.add("error");
        message.classList.add("error");
    }
}
function closeModal() {
    modal.hidden = true;
}
modal.addEventListener("click", (e) => {
    if (e.target.hasAttribute("data-close-modal")) {
        closeModal();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dom loaded checkout page');

    const options = document.querySelectorAll('.pay-option');
    const mpesaForm = document.getElementById('mpesa-form');
    const stripeForm = document.getElementById('stripe-form');

    // Calculate total once
    const totalText = document.querySelector('.order-total').textContent;
    const totalAmount = parseFloat(totalText.replace(/[^0-9.]/g, ''));

    // Step 1: toggle forms
    options.forEach(btn => {
        btn.addEventListener('click', () => {
            mpesaForm.classList.add('hidden');
            stripeForm.classList.add('hidden');
            if (btn.dataset.method === 'mpesa') {
                mpesaForm.classList.remove('hidden');
            } else if (btn.dataset.method === 'stripe') {
                stripeForm.classList.remove('hidden');
            }
        });
    });

    // Step 2: handle M‑Pesa form
    mpesaForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const phone = document.getElementById('phone').value;
        openModal("Processing M‑Pesa payment...");

        fetch('/pay/mpesa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone, amount: totalAmount })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log(data);
                openModal("STK Push initiated. Please complete payment on your phone...", "success");

                const checkoutId = data.stk_response.CheckoutRequestID;
                checkPaymentStatus(checkoutId);
            } else {
                openModal("Payment failed: " + data.message, "error");
            }
        })
        .catch(err => {
            console.error("Error initiating payment:", err);
            openModal("Error initiating payment.", "error");
        });
    });

    // Step 2: handle Stripe form
    stripeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const card = document.getElementById('card').value;

        fetch('/pay/stripe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ card_number: card, amount: totalAmount })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = `/order/${data.order_id}`;
            } else {
                openModal("Payment failed: " + data.message, "error");
            }
        })
        .catch(err => {
            console.error("Error initiating Stripe payment:", err);
            openModal("Error initiating payment.", "error");
        });
    });
});

// Polling for payment status
function checkPaymentStatus(checkoutId) {
    const interval = setInterval(() => {
        fetch(`/payment_status/${checkoutId}`)
            .then(res => res.json())
            .then(data => {
                if (data.status !== "pending") {
                    clearInterval(interval);
                    if (data.success) {
                        console.log(`Payment successful for checkout ID: ${checkoutId}`);
                        openModal("✅ Payment successful!", "success");
                    } else {
                        openModal("❌ " + data.message, "error");
                        console.log(`Payment failed for checkout ID: ${checkoutId}`);
                    }
                }
            })
            .catch(err => {
                console.error("Error checking payment status:", err);
                openModal("Error checking payment status.", "error");
            });
    }, 5000); // poll every 5 seconds
}
