"use strict"
import pdfReader from "./file_loader.js";
function updateSaveButtonState(input_fields= null, save_btn= null, adv_payer = null) {
    const pdf_file_input = document.getElementById("pdf_file");
    const file = pdf_file_input.files[0];
    const default_adv_value = adv_payer.defaultChecked;

    const all_fields_empty = input_fields.every(input => input.value.trim() === "");
    const adv_paid = adv_payer.checked === default_adv_value;
    const no_file_selected = !file;

    const should_disable_button = all_fields_empty && adv_paid && no_file_selected;

    save_btn.disabled = should_disable_button;
    save_btn.style.pointerEvents = should_disable_button ? "none" : "auto";
    save_btn.style.cursor = should_disable_button ? "default" : "pointer";
    save_btn.style.backgroundColor = should_disable_button ? "#EEEDEB" : "#008000FF";
}

function listenEditFields() {
    const save_button_element = document.querySelector("#save");
    const adv_payer = document.querySelector("#is_adv_payer");
    save_button_element.disabled = true;
    save_button_element.style.pointerEvents = "none";
    save_button_element.style.cursor = "default";
    save_button_element.style.backgroundColor = "#EEEDEB";
    const input_fields = Array.from(document.querySelectorAll("table input")).slice(0, -3);

    const update_state = () => updateSaveButtonState(
        input_fields,
        save_button_element,
        adv_payer
    );

    adv_payer.addEventListener("change", update_state);

    input_fields.forEach(el => {
        el.addEventListener("input", update_state);
    });

    document.getElementById("pdf_file").addEventListener("change", (event) => {
    const file = event.target.files[0];
    const reader_pdf = pdfReader(file, null, true, update_state)
    if (!file) {
        document.getElementById('progress').style.width = '0';
        update_state();
    } else {
        reader_pdf
    }
    });
}

// Call the function to set up the listeners
listenEditFields();
