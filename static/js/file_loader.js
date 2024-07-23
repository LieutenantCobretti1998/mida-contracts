"use strict"

document.getElementById("pdf_file").addEventListener("change", (event) => {
    const file = event.target.files[0];
    const button_element = document.querySelector(".save-btn");
    if (!file) {
        document.getElementById('progress').style.width = '0';
        button_element.style.pointerEvents = "none";
        button_element.style.cursor = "default";
        button_element.style.backgroundColor = "#EEEDEB";
        return;
    }
    if (file) {
        button_element.setAttribute("disabled", "true");
        if(button_element.hasAttribute("disabled")) {
            button_element.style.pointerEvents = "none";
            button_element.style.cursor = "default";
            button_element.style.backgroundColor = "#EEEDEB";
        }
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
            button_element.removeAttribute("disabled");
            button_element.style.pointerEvents = "";
            button_element.style.cursor = "";
            button_element.style.backgroundColor = "#008000FF";
            document.getElementById('progress').style.width = '100%';
        };
        reader.readAsArrayBuffer(file);
    }
});