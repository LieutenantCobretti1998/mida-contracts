"use strict"

export default function pdfReader(file=null, save_button=null, edit_mode=false, update_function=null) {
    const reader = new FileReader();
    if (file && !edit_mode) {
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
            save_button.removeAttribute("disabled");
            save_button.style.pointerEvents = "";
            save_button.style.cursor = "";
            save_button.style.backgroundColor = "#008000FF";
            document.getElementById('progress').style.width = '100%';
        };
        return reader.readAsArrayBuffer(file);
    }
    else if(file && !edit_mode) {
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
            document.getElementById("progress").style.width = '100%';
            update_function();
        };
        return reader.readAsArrayBuffer(file);
    }
}

document.getElementById("pdf_file").addEventListener("change", (event) => {
    const file = event.target.files[0];
    const button_element = document.querySelector(".save-btn");
            button_element.style.pointerEvents = "none";
            button_element.style.cursor = "default";
            button_element.style.backgroundColor = "#EEEDEB";
        pdfReader(file, button_element);
});