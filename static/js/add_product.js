document.addEventListener('DOMContentLoaded', function() {
    console.log('Add Product JS Loaded');
    // 
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('product-image');
    const previewImg = document.getElementById('preview-img');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#007bff';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#ddd';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ddd';
        const file = e.dataTransfer.files[0];
        if (file) {
        previewImage(file);
        }
    });

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
        previewImage(file);
        }
    });

    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = () => {
        previewImg.src = reader.result;
        };
        reader.readAsDataURL(file);
    }
    // 

});