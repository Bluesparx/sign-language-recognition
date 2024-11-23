let videoElement = document.getElementById("webcam");
let canvasElement = document.getElementById("boundingBox");
let context = canvasElement.getContext("2d");
let predictionDiv = document.getElementById("prediction");
let accumulatedTextDiv = document.getElementById("accumulated-text");

let addSpaceBtn = document.getElementById("addSpace");
let backspaceBtn = document.getElementById("backspace");
let clearBtn = document.getElementById("clear");

let accumulatedText = "";
let lastPrediction = "";

const constraints = {
    video: {
        facingMode: "user",
        width: { ideal: 640 },
        height: { ideal: 480 }
    }
};

navigator.mediaDevices.getUserMedia(constraints)
    .then(function(stream) {
        videoElement.srcObject = stream;
    })
    .catch(function(error) {
        console.log("Error accessing webcam: ", error);
    });

// Button event listeners
addSpaceBtn.addEventListener("click", () => {
    accumulatedText += " ";
    updateAccumulatedText();
});

backspaceBtn.addEventListener("click", () => {
    accumulatedText = accumulatedText.slice(0, -1);
    updateAccumulatedText();
});

clearBtn.addEventListener("click", () => {
    accumulatedText = "";
    updateAccumulatedText();
});

function updateAccumulatedText() {
    accumulatedTextDiv.textContent = accumulatedText;
}

// Send every 200ms
setInterval(() => {
    if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA && videoElement.paused === false) {

        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;

        context.clearRect(0, 0, canvasElement.width, canvasElement.height);
        
        context.beginPath();
        context.rect(100, 100, 200, 200);
        context.strokeStyle = "green";
        context.lineWidth = 4;
        context.stroke();
        context.drawImage(videoElement, 0, 0, videoElement.videoWidth, videoElement.videoHeight);
        let imgData = canvasElement.toDataURL("image/jpeg").replace(/^data:image\/(png|jpeg);base64,/, "");

        fetch("/", {
            method: "POST",
            body: new URLSearchParams({
                image_data: imgData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.prediction) {
                console.log("Prediction:", data.prediction);
                predictionDiv.textContent = "Predicted Sign: " + data.prediction;
                
                if (data.prediction !== lastPrediction) {
                    accumulatedText += data.prediction;
                    updateAccumulatedText();
                    lastPrediction = data.prediction;
                }
            } else {
                predictionDiv.textContent = "Error: " + data.error;
            }
        })
        .catch(error => {
            predictionDiv.textContent = "Error occurred!";
            console.error("Error during prediction:", error);
        });
    }
}, 200);