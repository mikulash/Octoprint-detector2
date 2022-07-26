/*
 * View model for OctoPrint-Detector2
 *
 * Author: Mikulas Heinz
 * License: AGPLv3
 */
$(function () {
    function Detector2ViewModel(parameters) {
        var self = this;
        self.dev = false //TODO change when released
        self.dev_array = []
        //data
        self.state_text = undefined;
        self.last_image = undefined;
        //ML
        // self.modelURL = "./plugin/detector2/static/js/graphMobileNetModel/model.json";
        // self.modelURL = "./plugin/detector2/static/js/graphEffNetB3Model/model.json";
        self.modelURL = "./plugin/detector2/static/js/graphEffNetB3Model2/model.json";
        // self.modelInputShape = [300, 300]; // mobilenet
        self.modelInputShape = [300, 300];  //Effnet B3 a MobileNet
        self.modelLabels = ["OK", "Spaghetti", "Stringing or blobs"];
        self.model = undefined;
        //simpleCV
        self.objectHueColor = undefined;
        self.canvas = undefined;
        self.prevImage = undefined;
        //notify user
        self.emailSent = false;
        self.sendEmail = true;
        self.imgNotEncoded = undefined;
        self.user = undefined;
        self.alarmCounter = 0;

        self.onStartup = function () {
            //runs on loading octoprint page in browser
            console.log("DETECTOR STARTUP");
            console.log("DETECTOR 222222");
            //placeholder for user information settings
            self.user = {
                host: "smtp.office365.com",
                username: "your new outlook mail",
                password: "password",
                port: 587,
                to: "your personal mail",
                confidence: 75
            };
            //create HTML elements to show results of prediction
            self.state_text = document.createElement("span");
            self.state_text.id = "plugin-detector-state";
            self.last_image = new Image();
            self.last_image.id = "plugin-detector-last-img";

            let stateField = document.createElement("span");

            stateField.append(self.state_text);
            stateField.append(self.last_image);

            let container = document.createElement("div");
            container.append(stateField);
            document.getElementById("detector2-tab-start").appendChild(stateField);

            (async () => await self.loadTFModel())();
        };
        self.loadTFModel = async function () {
            self.model = await tf.loadGraphModel(self.modelURL);
        };

        self.onDataUpdaterPluginMessage = function (plugin, message) {
            //next version with octolapse stabilisation
            // if (plugin === "octolapse" && message.type === 'new-thumbnail-available'){
            //     let src = "plugin/octolapse/getSnapshot?file_type=snapshot&camera_guid=" + message.guid + "&apikey=";
            //     let img = new Image();
            //     img.src = src
            //     let ctx = self.canvas.getContext("2d");
            //     let ratio = self.canvas.width / img.width
            //     ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, img.width*ratio, img.height*ratio)
            //     self.detectWithCV()
            // }
            if (plugin === "detector2") {
                //message is intended for this plugin
                if (message.type === "snap") {
                    // console.log("new image from basic timelapse...");
                    let img_src = "data:image/png;base64," + message.img;
                    self.imgNotEncoded = message.img;
                    self.state_text.innerHTML =
                        "Snapshot taken at: " + message.time + " <br> ";
                    self.last_image.src = img_src;
                    self.last_image.onload = function () {
                        // run prediction once the image is loaded
                        (async () => await self.modelPredict(self.last_image))();
                    };
                } else if (message.type === "userChange") {
                    Object.keys(message.data).forEach(function (key) {
                        self.user[key] = message.data[key];
                    });
                    if (self.user.to === ""){
                        self.sendEmail = false
                    }
                }
                else if (message.type === "test") {
                    //testing purposes
                    console.log(message.data)
                }
            }
        };

        self.sendInfoToBackend = function (errorType, confidence){
            let url = API_BASEURL + 'plugin/detector2'
            $.ajax({
                url: url,
                type: "GET",
                dataType: "json",
                data:   { errorType: errorType, confidence: confidence} ,
                contentType: "application/json; charset=UTF-8",
                success: function(response) {
                    console.log("info about error sent to backend successfully")
                },
                error: function() {
                    console.log("sending info about error failed")
                }

            })
        }

        self.modelPredict = async function (theImg) {
            // function for image recognition using Tensorflow JS
            let starttime = undefined
            if(self.dev){
                starttime = Date.now()
                console.log(starttime)
            }
            //getting tensor from html image from https://github.com/tensorflow/tfjs/issues/193#issuecomment-381330663
            const tfImg = tf.browser.fromPixels(theImg);
            const smalImg = tf.image.resizeBilinear(tfImg, self.modelInputShape);
            const resized = tf.cast(smalImg, "float32");
            const t4d = tf.tensor4d(Array.from(resized.dataSync()), [1, 300, 300, 3]);

            let prediction = self.model.execute(t4d); //run TF model on image
            let dataS = prediction.softmax().dataSync(); //get prediction certainty

            if (self.dev) {
                let duration = Date.now() - starttime
                console.log("prediction duration = ", duration)
                if( self.dev_array.length > 10){
                    self.dev_array.shift()
                }
                self.dev_array.push(duration)
                let total = 0, count = 0
                self.dev_array.forEach(function(item, index) {
                total += item;
                count++;
                  });
                console.log(count)
                console.log("prumerna doba = ", total/count)
            }
            let max = Math
                .max(...dataS);
            let index = dataS.indexOf(max);
            let confidence = max * 100;
            confidence = confidence.toFixed(2);
            if (index > 0) {
                // if result is not OK
                self.state_text.innerHTML =
                    self.state_text.innerHTML +
                    "Detecting " +
                    self.modelLabels[index] +
                    " with confidence " +
                    confidence +
                    " %<br>";
                if (confidence >= parseInt(self.user.confidence)) {
                    // if confidence of error is above thresh set by user, send info and sound the alarm
                    if (self.alarmCounter < 1){
                        self.sendInfoToBackend(self.modelLabels[index], confidence)
                    }
                    if (self.alarmCounter < 3) {
                        alarm();
                        self.emailSent = true;
                        self.sendEmail = false;
                        self.alarmCounter++;
                    }
                }
            } else {
                // AI detected OK
                self.state_text.innerHTML =
                    self.state_text.innerHTML +
                    "Looking good. I'm " +
                    confidence +
                    " % confident about it.";
            }
        };

        self.detectWithCV = function () {
            // NOT USED, maybe to be released in future version
            if (self.objectHueColor === undefined) return;
            let src = cv.imread(self.canvas);
            let dst = new cv.Mat();
            let blur = new cv.Mat();
            let mask = new cv.Mat();
            let hue = new cv.Mat();
            // let low = new cv.Mat(src.rows, src.cols, src.type(), [self.objectHueColor[0]-15, 100, 100, 0]);
            // let high = new cv.Mat(src.rows, src.cols, src.type(), [self.objectHueColor[0]+15, 255, 255, 255]);
            let low = new cv.Mat(src.rows, src.cols, src.type(), [0, 0, 0, 0]);
            let high = new cv.Mat(src.rows, src.cols, src.type(), [150, 150, 150, 255]);
            let low_thresh = [self.objectHueColor[0] - 15, 100, 100];
            let high_thresh = [self.objectHueColor[0] + 15, 255, 255];
            cv.cvtColor(src, src, cv.COLOR_BGR2HLS_FULL, 0);
            // cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY , 0);
            cv.bilateralFilter(src, blur, 5, 75, 75); // snizit d=velikost filtru, pokud nebude stihat
            // cv.inRange(blur, low, high, dst);
            outputCanvas = document.querySelector("#canvasOutput");
            if (self.prevImage === undefined) {
                self.prevImage = blur;
            } else {
                let diff = new cv.Mat();
            }
            cv.imshow(outputCanvas, blur);
            src.delete();
        };

        self.getCursorPosition = function (canvas, event) {
            // https://stackoverflow.com/a/18053642
            //not used, would have been used for changes detection
            //gets color and position on canvas mouse click
            const rect = canvas.getBoundingClientRect();
            console.log(canvas);
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            let color = canvas.getContext("2d").getImageData(x, y, 1, 1).data;
            color = Array.from(color);
            console.log("x: " + x + " y: " + y, "|", color);
            self.objectHueColor = color;
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        //generated by Octoprint
        construct: Detector2ViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [
            /* "loginStateViewModel", "settingsViewModel" */
        ],
        // Elements to bind to, e.g. #settings_plugin_detector2, #tab_plugin_detector2, ...
        elements: [
            /* ... */
        ]
    });
});

function alarm() {
    // alarm file is from https://www.youtube.com/watch?v=iNpXCzaWW1s
    let audio = new Audio("./plugin/detector2/static/alarm.mp3");
    audio.play();
}
