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

// Close modal on backdrop click
modal.addEventListener("click", (e) => {
    if (e.target.hasAttribute("data-close-modal")) {
        closeModal();
    }
});

// Main DOM ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - checkout page');

    // Get all elements
    const options = document.querySelectorAll('.pay-option');
    const mpesaForm = document.getElementById('mpesa-form');
    const stripeForm = document.getElementById('stripe-form');
    const pesapalForm = document.getElementById('pesapal-form');
    const pesapalPayBtn = document.getElementById('pesapal-pay-btn');
    const totalInput = document.getElementById('total-amount');
    
    // Calculate total
    const totalAmount = totalInput ? parseFloat(totalInput.value) : 0;
    console.log('Total amount:', totalAmount);

    // ============================================
    // STEP 1: Toggle payment forms
    // ============================================
    options.forEach(btn => {
        btn.addEventListener('click', () => {
            // Hide all forms
            mpesaForm.classList.add('hidden');
            stripeForm.classList.add('hidden');
            if (pesapalForm) pesapalForm.classList.add('hidden');
            
            // Show selected form
            const method = btn.dataset.method;
            if (method === 'mpesa') {
                mpesaForm.classList.remove('hidden');
            } else if (method === 'stripe') {
                stripeForm.classList.remove('hidden');
            } else if (method === 'pesapal' && pesapalForm) {
                pesapalForm.classList.remove('hidden');
            }
        });
    });

    // ============================================
    // STEP 2: M-Pesa Payment
    // ============================================
    mpesaForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const phone = document.getElementById('phone').value;
        
        if (!phone || phone.length < 10) {
            openModal("Please enter a valid phone number", "error");
            return;
        }
        
        openModal("Processing M‑Pesa payment...");

        fetch('/pay/mpesa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                phone_number: phone, 
                amount: totalAmount 
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('M-Pesa response:', data);
                openModal("STK Push initiated. Please complete payment on your phone...", "success");
                
                const checkoutId = data.stk_response?.CheckoutRequestID;
                if (checkoutId) {
                    checkPaymentStatus(checkoutId);
                }
            } else {
                openModal("Payment failed: " + (data.message || "Unknown error"), "error");
            }
        })
        .catch(err => {
            console.error("Error initiating M-Pesa payment:", err);
            openModal("Error initiating payment. Please try again.", "error");
        });
    });

    // ============================================
    // STEP 3: Stripe Payment
    // ============================================
    stripeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const card = document.getElementById('card').value;
        
        if (!card || card.length < 10) {
            openModal("Please enter a valid card number", "error");
            return;
        }

        openModal("Processing Stripe payment...");

        fetch('/pay/stripe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                card_number: card, 
                amount: totalAmount 
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                openModal("✅ Payment successful!", "success");
                setTimeout(() => {
                    window.location.href = `/order/${data.order_id}`;
                }, 1500);
            } else {
                openModal("Payment failed: " + (data.message || "Unknown error"), "error");
            }
        })
        .catch(err => {
            console.error("Error initiating Stripe payment:", err);
            openModal("Error initiating payment. Please try again.", "error");
        });
    });

    // ============================================
    // STEP 4: Pesapal Payment
    // ============================================
    if (pesapalPayBtn) {
        pesapalPayBtn.addEventListener('click', function() {
            if (totalAmount === 0) {
                openModal("Error: No items in cart", "error");
                return;
            }

            // Show processing message
            openModal("Processing Pesapal payment...");

            // Prepare the payload for Pesapal terminal service
            const payload = {
                txntype: "sale",
                timestamp: new Date().toISOString(),
                reference: `Order_${Date.now()}`,
                paymentdetails: {
                    currency: "USD",
                    amount: totalAmount,
                    taxamount: 0
                },
                posdetails: {
                    name: "Unity Store",
                    details: {
                        cardpresent: "1",
                        industrycode: "1",
                        operator: "1",
                        lodgingcode: "1",
                        siteid: "1",
                        sequenceno: String(Math.floor(Math.random() * 1000000)).padStart(6, '0')
                    }
                }
            };

            console.log("Sending payload to Pesapal:", payload);

            // Send to Flask server (which forwards to terminal service)
            fetch('/pay/pesapal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: totalAmount,
                    payload: payload
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Pesapal response:", data);
                
                if (data.success) {
                    openModal("✅ Payment successful! Order #" + data.order_id, "success");
                    
                    // Redirect to order confirmation after delay
                    setTimeout(() => {
                        window.location.href = `/order/${data.order_id}`;
                    }, 2000);
                } else {
                    openModal("❌ Payment failed: " + (data.message || "Unknown error"), "error");
                }
            })
            .catch(error => {
                console.error("Error processing Pesapal payment:", error);
                openModal("❌ Error: " + (error.message || "Network error"), "error");
            });
        });
    }
});

// ============================================
// Polling for M-Pesa payment status
// ============================================
function checkPaymentStatus(checkoutId) {
    if (!checkoutId) return;
    
    let attempts = 0;
    const maxAttempts = 12; // 12 * 5 seconds = 60 seconds max
    
    const interval = setInterval(() => {
        attempts++;
        
        fetch(`/payment_status/${checkoutId}`)
            .then(res => res.json())
            .then(data => {
                console.log(`Payment status check #${attempts}:`, data);
                
                if (data.status !== "pending") {
                    clearInterval(interval);
                    if (data.success) {
                        openModal("✅ Payment successful!", "success");
                        // Redirect to orders page after success
                        setTimeout(() => {
                            window.location.href = '/orders';
                        }, 2000);
                    } else {
                        openModal("❌ " + (data.message || "Payment failed"), "error");
                    }
                } else if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    openModal("⏱️ Payment timeout. Please check your orders for status.", "error");
                }
            })
            .catch(err => {
                console.error("Error checking payment status:", err);
                if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    openModal("Error checking payment status. Please check your orders.", "error");
                }
            });
    }, 5000); // poll every 5 seconds
}