function updateSaveButtonState(input_fields = null, save_btn = null, adv_payer = null, status = null, categories = null, default_category = null, file_inputs = []) {
    const pdf_file_input = document.getElementById("pdf_file");
    const file = pdf_file_input ? pdf_file_input.files[0] : null;

    const default_adv_value = adv_payer.defaultChecked;
    const default_status_value = status.defaultChecked;

    const all_fields_empty = input_fields.every(input => input.value.trim() === "");
    const adv_paid = adv_payer.checked === default_adv_value;
    const contract_finished = status.checked === default_status_value;
    const category_selected = categories.value === default_category;

    const no_file_selected = !file && file_inputs.every(input => !input.files[0]);

    const should_disable_button = all_fields_empty && adv_paid && contract_finished && no_file_selected && category_selected;

    save_btn.disabled = should_disable_button;
    save_btn.style.pointerEvents = should_disable_button ? "none" : "auto";
    save_btn.style.cursor = should_disable_button ? "default" : "pointer";
    save_btn.style.backgroundColor = should_disable_button ? "#EEEDEB" : "#008000FF";
}

function listenEditFields() {
    const save_button_element = document.querySelector("#save");
    const adv_payer = document.querySelector("#is_adv_payer");
    const status = document.querySelector("#status");
    const categories = document.querySelector("#categories");
    const comments = document.querySelector("#comments");
    const default_category = categories.value;

    save_button_element.disabled = true;
    save_button_element.style.pointerEvents = "none";
    save_button_element.style.cursor = "default";
    save_button_element.style.backgroundColor = "#EEEDEB";

    // Gather all input fields including dynamic file inputs
    const input_fields = [...Array.from(document.querySelectorAll("table input")).slice(0, -3), comments];
    const file_inputs = Array.from(document.querySelectorAll("input[type='file']"));

    const update_state = () => updateSaveButtonState(
        input_fields,
        save_button_element,
        adv_payer,
        status,
        categories,
        default_category,
        file_inputs
    );

    adv_payer.addEventListener("change", update_state);
    status.addEventListener("change", update_state);
    categories.addEventListener("change", update_state);

    input_fields.forEach(el => {
        el.addEventListener("input", update_state);
    });

    // Listen to all file inputs including dynamically added ones
    file_inputs.forEach((file_input, index) => {
        file_input.addEventListener("change", (event) => {
            const file = event.target.files[0];
            const progress_bar = document.querySelector(`#progress_${index}`);

            if (!file) {
                if (progress_bar) progress_bar.style.width = '0';
                update_state();
            } else {
                const reader = new FileReader();
                reader.onprogress = (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        if (progress_bar) progress_bar.style.width = `${percentComplete}%`;
                    }
                };
                reader.onloadend = () => {
                    if (progress_bar) progress_bar.style.width = '100%';
                    update_state();
                };
                reader.readAsArrayBuffer(file);
            }
        });
    });

    const pdf_input = document.getElementById("pdf_file");
    if (pdf_input) {
        pdf_input.addEventListener("change", (event) => {
            const file = event.target.files[0];
            const reader_pdf = new FileReader();

            reader_pdf.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    document.getElementById('progress').style.width = `${percentComplete}%`;
                }
            };

            reader_pdf.onloadend = () => {
                document.getElementById('progress').style.width = '100%';
                update_state();
            };

            if (!file) {
                document.getElementById('progress').style.width = '0';
                update_state();
            } else {
                reader_pdf.readAsArrayBuffer(file);
            }
        });
    }
}

// Call the function to set up the listeners
listenEditFields();
