const imageInput = document.getElementById('id_image');
const preview =  document.getElementById('preview-image')

imageInput.addEventListener('change',()=>{
    const file = imageInput.files[0];
    if(file){
        const reader = new FileReader();
        reader.onload = e => {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});