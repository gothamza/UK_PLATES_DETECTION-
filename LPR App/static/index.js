const imageInput = document.getElementById('image-input');
const imagePreview = document.getElementById('image-preview');
const cropButton = document.getElementById('crop-button');
let cropper;

imageInput.addEventListener('change', function(event) {
  const file = event.target.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = function(event) {
      imagePreview.src = event.target.result;
      initializeCropper();
    };

    reader.readAsDataURL(file);
  }
});

function initializeCropper() {
  if (cropper) {
    cropper.destroy();
  }

  cropper = new Cropper(imagePreview, {
    aspectRatio: -5,
    viewMode: 1,
    movable: false,
    zoomable: false,
    rotatable: false,
    scalable: false
  });
}


cropButton.addEventListener('click', function() {
  const croppedCanvas = cropper.getCroppedCanvas();

  if (croppedCanvas) {
    const croppedImage = croppedCanvas.toDataURL();
    // Faites quelque chose avec l'image recadrée, par exemple l'afficher sur la page ou l'envoyer au serveur.
    document.getElementById('image_preview').src = croppedImage;
    $.ajax({
      url: '/upload',
      type: 'POST',
      data: { image: croppedImage },
      beforeSend: function() {
        // Afficher le chargement
        $('#loading').css('display', 'block');
      },
      success: function(response) {
        // Gérer la réponse du serveur
        var grayImageSrc = 'data:image/jpeg;base64,' + response.gray_image; 
        var edgedImageSrc = 'data:image/jpeg;base64,' + response.edged_image;
        var newImageSrc = 'data:image/jpeg;base64,' + response.new_image;
        var resImageSrc = 'data:image/jpeg;base64,' + response.res;
        var text = response.text;
        var confidence = response.confidence;
    
        // Afficher les images dans votre HTML
        $('#gray-image').attr('src', grayImageSrc).css('display', 'block');
        $('#edged-image').attr('src', edgedImageSrc).css('display', 'block');
        $('#new-image').attr('src', newImageSrc).css('display', 'block');
        $('#res-image').attr('src', resImageSrc).css('display', 'block');
        $('#text').text(text);
        $('#confidence').text(confidence);
    
        // Afficher les balises h2
        $('#gray-heading').show();
        $('#edged-heading').show();
        $('#new-heading').show();
        $('#res-heading').show();
    
        // Masquer le chargement
        $('#loading').css('display', 'none');
        
        // Masquer les éléments image originale et image recadrée
        $('.col-2').hide();
        
        // Masquer les éléments texte et confiance
        $('.col-4').hide();
        
        // Afficher les éléments texte et confiance après le chargement des images
        $('.col-4').show();
      },


      error: function(xhr, status, error) {
        // Gérer les erreurs
      }
    });
  }
  
});


/**

 */