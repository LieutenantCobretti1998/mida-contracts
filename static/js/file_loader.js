"use strict"

document.getElementById("pdf_file").addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onloadstart = function () {
            document.getElementById("progress").style.width = "0"; // Reset progress bar on new file load
        };
        reader.onprogress = function (event) {
            if (event.lengthComputable) {
                const percentage = (event.loaded / event.total) * 100;
                document.getElementById("progress").style.width = `${percentage}%`;
            }
        };
        reader.onloadend = function () {
            document.getElementById('progress').style.width = '100%';
        };
        reader.readAsArrayBuffer(file);
    }
});