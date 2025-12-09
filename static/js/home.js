function clearFilters(){
    console.log("calling function clear filters")
    window.location.href = '/home';
}



document.addEventListener('DOMContentLoaded', function() {
    console.log('Dom loaded products page')
    add_to_cart_btn = document.querySelector('.add-to-cart')
    // Auto-submit search when user stops typing
    let searchTimeout;
    document.getElementById('search-input').addEventListener('input',function(){
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(()=>{
            document.getElementById('filter-form').submit();
        },500);
    });

    // Auto-submit filters when checkboxes/radios change
    document.querySelectorAll('input[type="checkbox"],input[type="radio"]').forEach(input=>{
        input.addEventListener('change',function(){
            document.getElementById('filter-form').submit();
        });
    });

    // Price range auto-submit
    document.getElementById('max-price').addEventListener('change',function(){
        document.getElementById('filter-form').submit();
    });

    document.getElementById('clear-filters').addEventListener('click',function(){
        console.log("clearing filters")
        clearFilters();
    })

    document.getElementById('apply-filters-btn').addEventListener('click',function(){
        console.log("applying filters")
        document.getElementById('filter-form').submit();
    });


    // add to cart logic
    add_to_cart_btn.addEventListener('click',function(){
        console.log('add cart button clicked')
    })

});