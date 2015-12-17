"use strict";

var outputString = "ha ha ha";

var HEADER = "FRWH";

var WIDTH = 320;
var HEIGHT = 320;

/**
 * FRWH
 * [version], a number in ascii left-padded w zeroes to be 4 chracters wide
 * len(code), a number in ascii left-padded w zeroes to be 10 chracters wide
 * [code]
 * len(state), a number in ascii left-padded w zeroes to be 10 chracters wide
 * [state] in json
 */

// Writes a header and CRC check
function writeDataToCanvas(data, canvas, x, y, maxWidth, maxHeight) {
  var ctx = canvas.getContext('2d');
  for (var i = 0; i < data.length; i++) {
    var charCode = data.charCodeAt(i);
    ctx.fillStyle = `rgb(${charCode},${charCode},${charCode})`;
    var pixelX = i % maxWidth;
    var pixelY = Math.floor(i / maxHeight);
    ctx.fillRect(pixelX, pixelY, 1, 1);
  }
}

function leftPadNumber(number) {
  var str = "" + number;
  var pad = "0000000000";
  return pad.substring(0, pad.length - str.length) + str;
}

// draws to canvas, is given existing state. call completion(newState) when done to generate a new png.
var chessApp = function (canvas, state, completion) {
  var ctx = canvas.getContext('2d');
  
  var padding = 40;
  var boardWidth = WIDTH - 2 * padding;
  var boardHeight = HEIGHT - 2 * padding;
  var squareDimension = boardWidth / 8;
  
  var boardState = state;
  
  for (var i = 0; i < 8; i++) {
    for (var j = 0; j < 8; j++) {
      if ((i + j) % 2 == 0) {
        ctx.fillStyle = 'red';
      } else {
        ctx.fillStyle = 'black';
      }
      ctx.fillRect(padding + j * squareDimension, padding + i * squareDimension, squareDimension, squareDimension);
      
      if (boardState[i * 8 + j] == 'R') {
        ctx.fillStyle = 'red';
        ctx.beginPath();
        ctx.arc(padding + j * squareDimension + squareDimension / 2, padding + i * squareDimension + squareDimension / 2, squareDimension / 2 - 4, 0, Math.PI * 2, true);
        ctx.fill();
      }
      if (boardState[i * 8 + j] == 'B') {
        ctx.fillStyle = 'black';
        ctx.beginPath();
        ctx.arc(padding + j * squareDimension + squareDimension / 2, padding + i * squareDimension + squareDimension / 2, squareDimension / 2 - 4, 0, Math.PI * 2, true);
        ctx.fill();
      }
      
    }
  }
}

var chessInitialState = 
  " R R R R" +
  "R R R R " +
  " R R R R" +
  "        " +
  "        " +
  " B B B B" +
  "B B B B " +
  " B B B B";

function serializeCanvasAndState(canvas, state) {
  var output = HEADER;
  output += "0001"; // version
  var code = chessApp.toString();
  output += leftPadNumber(code.length);
  output += code;
  var serializedState = JSON.stringify(state);
  output += leftPadNumber(serializedState.length);
  output += serializedState;
  
  // console.log(output);

  writeDataToCanvas(output, canvas, 0, 0, 320, 320);
}

function readStringAtLinearOffset(canvas, offset, length) {
  var buffer = "";

  for (var i = 0; i < length; i++) {
    var pixelX = (i + offset) % WIDTH;
    var pixelY = (i + offset) / HEIGHT;
    var pixelData = canvas.getContext('2d').getImageData(pixelX, pixelY, 1, 1).data;
    buffer += String.fromCharCode(pixelData[0]);
  }

  return buffer;
}

function readDataFromImage(image) {
  var canvas = document.createElement('canvas');
  canvas.width = image.width;
  canvas.height = image.height;
  
  var ctx = canvas.getContext('2d');
  ctx.drawImage(image, 0, 0, image.width, image.height);
  
  var header = readStringAtLinearOffset(canvas, 0, 4);
  if (header != HEADER) {
    throw new die;
  }
  
  var version = readStringAtLinearOffset(canvas, 4, 4);
  if (parseInt(version) != 1) {
    throw new die;
  }
  
  var codeLength = parseInt(readStringAtLinearOffset(canvas, 8, 10));
  var code = readStringAtLinearOffset(canvas, 18, codeLength);
  
  var stateLength = parseInt(readStringAtLinearOffset(canvas, 18 + codeLength, 10));
  var state = JSON.parse(readStringAtLinearOffset(canvas, 28 + codeLength, stateLength));
  
  return {
    code: eval('(' + code + ')'),
    state: state
  };
}

document.addEventListener("DOMContentLoaded", function(event) { 
  chessApp(canvas, chessInitialState, function() {
  });
  
  serializeCanvasAndState(canvas, chessInitialState);

  var outputImage = document.getElementById('serializedImage');
  outputImage.src = canvas.toDataURL('image/png');
  
  console.log(readDataFromImage(outputImage));
});
