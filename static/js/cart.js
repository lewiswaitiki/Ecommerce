function updateQuantity(productId, delta) {
    const input = document.querySelector(`.quantity-input[data-product="${productId}"]`);
    let newQty = parseInt(input.value) + delta;
    if (newQty < 1) newQty = 1;
    input.value = newQty;

    fetch('/update_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity: newQty })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.querySelector('.cart-count').textContent = data.cart_count;
            document.querySelector(`.item-total[data-product="${productId}"]`).textContent = "Ksh " + data.product_total.toFixed(2);
            document.querySelector('.cart-total').textContent = "Total: Ksh " + data.total.toFixed(2);
            console.log('cart quantity updated successfully');
        }
    });
}



// remove item from cart function
function removeItem(productId) {
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({product_id: productId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload(); // simplest way: reload cart page
            console.log('item deleted successfully')
        }
    })
    .catch(err => {
        console.error("Error removing item:", err);
        alert("Could not remove item from cart");

    });
}



document.addEventListener('DOMContentLoaded', function() {
    console.log('Dom loaded cart  page')
    const checkoutBtn = document.getElementById('checkout-btn');
    document.querySelectorAll('.qty-btn.plus').forEach(btn => {
        btn.addEventListener('click', () => updateQuantity(btn.dataset.product, 1));
    });
    document.querySelectorAll('.qty-btn.minus').forEach(btn => {
        btn.addEventListener('click', () => updateQuantity(btn.dataset.product, -1));
    });

    document.querySelectorAll('.fa-trash-can').forEach(icon => {
        icon.addEventListener('click', () => removeItem(icon.dataset.product));
    });


    // checkout button click
    if (checkoutBtn){
        checkoutBtn.addEventListener('click', () => {
            window.location.href = '/checkout';
        }
    );
    }
});