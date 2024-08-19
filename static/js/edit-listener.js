"use strict"
import pdfReader from "./file_loader.js";

/**
 *
 * @param input_fields
 * @param save_btn
 * @param adv_payer
 * @param categories
 * @param default_category
 */
function updateSaveButtonState(input_fields= null, save_btn= null, adv_payer = null, categories = null, default_category = null) {
    const pdf_file_input = document.getElementById("pdf_file");
    const file = pdf_file_input.files[0];
    const default_adv_value = adv_payer.defaultChecked;

    const all_fields_empty = input_fields.every(input => input.value.trim() === "");
    const adv_paid = adv_payer.checked === default_adv_value;
    const category_selected = categories.value === default_category;

    const no_file_selected = !file;

    const should_disable_button = all_fields_empty && adv_paid && no_file_selected && category_selected;

    save_btn.disabled = should_disable_button;
    save_btn.style.pointerEvents = should_disable_button ? "none" : "auto";
    save_btn.style.cursor = should_disable_button ? "default" : "pointer";
    save_btn.style.backgroundColor = should_disable_button ? "#EEEDEB" : "#008000FF";
}

function listenEditFields() {
    const save_button_element = document.querySelector("#save");
    const adv_payer = document.querySelector("#is_adv_payer");
    const categories = document.querySelector("#categories");
    const default_category = categories.value;

    save_button_element.disabled = true;
    save_button_element.style.pointerEvents = "none";
    save_button_element.style.cursor = "default";
    save_button_element.style.backgroundColor = "#EEEDEB";
    const input_fields = Array.from(document.querySelectorAll("table input")).slice(0, -3);


    const update_state = () => updateSaveButtonState(
        input_fields,
        save_button_element,
        adv_payer,
        categories,
        default_category
    );

    adv_payer.addEventListener("change", update_state);
    categories.addEventListener("change", update_state);

    input_fields.forEach(el => {
        el.addEventListener("input", update_state);
    });

    document.getElementById("pdf_file").addEventListener("change", (event) => {
    const file = event.target.files[0];
    const reader_pdf = pdfReader(file, null, true, update_state);
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
