document.addEventListener('DOMContentLoaded', function() {
    console.log('Dom loaded product detail page');

    const add_to_cart_btn = document.querySelector('.add-to-cart');
    const quantityInput = document.getElementById('quantity');
    const plusBtn = document.getElementById('increase-qty');
    const minusBtn = document.getElementById('decrease-qty');

    // Plus button increases quantity
    plusBtn.addEventListener('click', function() {
        let currentQty = parseInt(quantityInput.value);
        let maxQty = parseInt(quantityInput.max);
        if (currentQty < maxQty) {
            quantityInput.value = currentQty + 1;
        }
    });

    // Minus button decreases quantity
    minusBtn.addEventListener('click', function() {
        let currentQty = parseInt(quantityInput.value);
        if (currentQty > 1) {
            quantityInput.value = currentQty - 1;
        }
    });

    // Add to cart logic
    add_to_cart_btn.addEventListener('click', function() {
        console.log('add cart button clicked');
        const productId = this.dataset.productId;
        const quantity = quantityInput.value;

        fetch('/add_to_cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('cart updated successfully', data);
                // ✅ Fetch updated cart count
                fetch('/get_cart_item_count')
                    .then(res => res.json())
                    .then(countData => {
                        document.querySelector('.cart-count').textContent = countData.cart_count;
                    });
            } else {
                alert(data.message || "Could not add item to cart");
            }
        })
        .catch(err => console.error("Error:", err));
    });
});
