"use strict";

function updateSaveButtonState(input_fields= null, save_btn= null) {

    const should_disable_button = input_fields.every(input => input.value.trim() === "");

    save_btn.disabled = should_disable_button;
    save_btn.style.pointerEvents = should_disable_button ? "none" : "auto";
    save_btn.style.cursor = should_disable_button ? "default" : "pointer";
    save_btn.style.backgroundColor = should_disable_button ? "#EEEDEB" : "#008000FF";
}

function listenEditFields() {
    const save_button_element = document.querySelector("#save");
    save_button_element.disabled = true;
    save_button_element.style.pointerEvents = "none";
    save_button_element.style.cursor = "default";
    save_button_element.style.backgroundColor = "#EEEDEB";
    const input_fields = Array.from(document.querySelectorAll("table input")).slice(0, -1);

    const update_state = () => updateSaveButtonState(
        input_fields,
        save_button_element,
    );


    input_fields.forEach(el => {
        el.addEventListener("input", update_state);
    });

}

// Call the function to set up the listeners
listenEditFields();