function Scanner(videoId, scanFunction=null, extraOpts={}) {
    const self = this
    this.videoId = videoId
    this.popup = extraOpts.popup ?? false
    let opts = {
        maxScansPerSecond: 4,
        highlightScanRegion: true,
        highlightCodeOutline: false,
        ...extraOpts,
    }
    let video = $(`#${videoId}`)
    if (this.popup) {
        video.wrap('<div id="video-scan-all" style="display: none; position: relative; overflow: hidden; border-radius: 5px" class="mt-4 bg-primary">')
    } else {
        video.wrap('<div id="video-scan-all" style="display: none; position: relative; overflow: hidden; border-radius: 5px; width: 100%" class="mt-4 bg-primary">')

    }
    video.after('<i id="toggle-flash" class="bi bi-lightning fs-1" style="display: none; position: absolute; z-index: 1252; right: 3%; top: 3%; cursor: pointer"></i>')
    video.after('<i id="toggle-cam" class="bi bi-arrow-repeat fs-1" style="display: none; position: absolute; z-index: 1252; right: 3%; bottom: 3%; cursor: pointer"></i>')
    video.show()
    if (this.popup) {
        let video_wrap = video.parent()
        video_wrap.before('<div class="row m-0 mt-3">' +
    '                          <div class="col-2 text-start"><h2><i id="close-button" class="bi bi-arrow-left" style="cursor: pointer"></i></h2></div>' +
    `                          <div class="col-8"><h2>${extraOpts.popup_title ?? 'QR scanner'}</h2></div>` +
    '                      </div>')
        let all = $.merge(video_wrap.prev(), video_wrap)

        all.wrapAll(`<div id="popup-scan-container" class="${extraOpts.popup_class ?? ''} p-2 col-lg-4 mt-lg-5 text-center">`).first().parent()
            .wrap('<div class="row justify-content-center m-0">').parent()
            .wrap('<div id="popup-scan" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none">')

        $(document).on('keyup', function(e) {
            if (e.key === "Escape") self.hide()
        })
        const div = document.createElement('div')
        div.style = 'display: none;'
        div.className = 'veil'
        div.id = 'veil'
        document.body.appendChild(div)
        $('#close-button').on('click', () => {self.hide()})
        $('#popup-scan').on('click', () => {self.hide()})
        $('#popup-scan-container').on('click', (e) => e.stopPropagation())
    }
    this.scanner = new QrScanner(video.get(0), scanFunction, opts)
    this.scanner.hasFlash().then((response) => {
        let flash = $('#toggle-flash')
        if (response) {
            flash.show()
            flash.on('click', () => {
                flash.toggleClass('bi-lightning bi-lightning-fill')
                self.scanner.toggleFlash()
            })
        }
    })
    QrScanner.listCameras(true).then(function (cameras) {
        if (cameras.length > 0) {
            let cameraId = localStorage.getItem("camera-id")
            if (cameraId === null || cameraId === undefined) {
                cameraId = "0"
                localStorage.setItem("camera-id", cameraId)
            }
            let camera_choices = ['environment', 'user']
            self.scanner.setCamera(camera_choices[parseInt(cameraId)])
            if (cameras.length > 1) {
                let toggle_cam = $('#toggle-cam')
                toggle_cam.show()
                let switcher = {0: "1", 1: "0"}
                toggle_cam.on('click', () => {
                    cameraId = switcher[cameraId] ?? "0"
                    localStorage.setItem("camera-id", cameraId)
                    self.scanner.setCamera(camera_choices[parseInt(cameraId)])
                })
            }
        } else {
            console.error('No cameras found.');
        }
    }).catch(function (e) {
        console.error(e);
    });
}

Scanner.prototype.start = function () {
    this.scanner.start()
}

Scanner.prototype.stop = function () {
    this.scanner.stop()
}

Scanner.prototype.show = function () {
    $('#video-scan-all').css('display', 'inline-block')
    $('#popup-scan').show()
    $('#veil').show()
    this.start()
}

Scanner.prototype.hide = function () {
    $('#video-scan-all').hide()
    $('#popup-scan').hide()
    $('#veil').hide()
    this.stop()
}

Scanner.prototype.addPhotoToForm = function (formId, inputId) {
    const self = this
    $(`#${formId}`).on("submit", (ev)=>{
        var video = document.getElementById(self.videoId);
	    var canvas = document.createElement("canvas");
        document.body.appendChild(canvas);
	    canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
	    canvas.getContext('2d').drawImage(video, 0, 0);
        document.getElementById(inputId).value = canvas.toDataURL("image/png");
    })
}
