"use strict";

document.addEventListener("DOMContentLoaded", function(event) { 
  document.getElementById('fileinput').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (!file) {
      return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {      
      var image = document.getElementById('serializedImage');
      image.src = reader.result;
      
      // data.code and data.state will have what i need
      var data = readDataFromImage(image);
      
      document.getElementById('fileinput').style.display = 'none';
      document.getElementById('canvas').style.display = 'block';

      data.code(document.getElementById('canvas'), data.state, function(newState) {
        var newCanvas = document.createElement('canvas');
        newCanvas.width = 320;
        newCanvas.height = 320;
                
        newCanvas.getContext('2d').drawImage(document.getElementById('canvas'), 0, 0);
        serializeCodeAndStateToCanvas(newCanvas, data.code, newState);

        var outputImage = document.getElementById('serializedImage');
        outputImage.src = newCanvas.toDataURL('image/png');
        outputImage.style.display = 'block';
      });
     };
     reader.readAsDataURL(file);
  });

});
