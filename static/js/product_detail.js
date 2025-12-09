
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dom loaded product detail page')
    add_to_cart_btn = document.querySelector('.add-to-cart')



    // add to cart logic
    add_to_cart_btn.addEventListener('click',function(){
        console.log('add cart button clicked')
        const productId = this.dataset.productId;
        const quantity = document.getElementById('quantity').value;
        console.log('Product ID to add to cart:', productId,'quantity:',quantity);

        fetch('/add_to_cart',{
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({product_id:productId,quantity:quantity})
        })
        .then(response=>response.json())
        .then(data=>{
            if (data.success){
                console.log(data);
                //update cart count instantly
                console.log('cart updated successfully')
            }else{
                alert(data.message || "could not add item to cart");
            }
        })
        .catch(err=>console.error("Error:",err));


    });



});