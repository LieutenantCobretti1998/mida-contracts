function updateSaveButtonState(
  input_fields = null,
  save_btn = null,
  adv_payer = null,
  status = null,
  categories = null,
  default_category = null,
  file_inputs = []
) {
  // Get the primary pdf file input by its ID (if exists)
  const pdf_file_input = document.getElementById("pdf_file");
  const file = pdf_file_input ? pdf_file_input.files[0] : null;

  // Save default states for adv_payer and status (their initial checked state)
  const default_adv_value = adv_payer.defaultChecked;
  const default_status_value = status.defaultChecked;

  // Check if all input fields are empty (ignoring whitespace)
  const all_fields_empty = input_fields.every(
    (input) => input.value.trim() === ""
  );
  // Check if adv_payer and status are still in their default state
  const adv_paid = adv_payer.checked === default_adv_value;
  const contract_finished = status.checked === default_status_value;
  // Check if the selected category equals the default category
  const category_selected = categories.value === default_category;

  // Check if no file is selected in both the main pdf_file input and any additional file inputs
  const no_file_selected =
    !file && file_inputs.every((input) => !input.files[0]);

  // Disable the save button if all conditions are met (i.e. nothing has changed)
  const should_disable_button =
    all_fields_empty &&
    adv_paid &&
    contract_finished &&
    no_file_selected &&
    category_selected;

  save_btn.disabled = should_disable_button;
  save_btn.style.pointerEvents = should_disable_button ? "none" : "auto";
  save_btn.style.cursor = should_disable_button ? "default" : "pointer";
  save_btn.style.backgroundColor = should_disable_button ? "#EEEDEB" : "#008000FF";
}

function listenEditFields() {
  // Grab references to the elements that control saving and the form inputs
  const save_button_element = document.querySelector("#save");
  const adv_payer = document.querySelector("#is_adv_payer");
  const status = document.querySelector("#status");
  const categories = document.querySelector("#categories");
  const comments = document.querySelector("#comments");
  const default_category = categories.value;

  // Initially disable the save button
  save_button_element.disabled = true;
  save_button_element.style.pointerEvents = "none";
  save_button_element.style.cursor = "default";
  save_button_element.style.backgroundColor = "#EEEDEB";

  // Gather all input fields from the table, excluding the last 3 inputs, then add comments field
  const input_fields = [
    ...Array.from(document.querySelectorAll("table input")).slice(0, -3),
    comments,
  ];
  // Gather all file input elements
  const file_inputs = Array.from(document.querySelectorAll("input[type='file']"));

  // Function to update the state of the save button based on form values
  const update_state = () =>
    updateSaveButtonState(
      input_fields,
      save_button_element,
      adv_payer,
      status,
      categories,
      default_category,
      file_inputs
    );

  // Attach change event listeners to adv_payer, status, and categories
  adv_payer.addEventListener("change", update_state);
  status.addEventListener("change", update_state);
  categories.addEventListener("change", update_state);

  // Attach input event listeners to all input fields
  input_fields.forEach((el) => {
    el.addEventListener("input", update_state);
  });

  // Attach change listeners to all file inputs (including dynamically added ones)
  file_inputs.forEach((file_input, index) => {
    file_input.addEventListener("change", (event) => {
      const file = event.target.files[0];
      // Query a progress bar element that corresponds to this file input (if exists)
      const progress_bar = document.querySelector(`#progress_${index}`);

      if (!file) {
        if (progress_bar) progress_bar.style.width = "0";
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
          if (progress_bar) progress_bar.style.width = "100%";
          update_state();
        };
        reader.readAsArrayBuffer(file);
      }
    });
  });

  // Handle the primary PDF input separately
  const pdf_input = document.getElementById("pdf_file");
  const pdf_files = document.getElementById("additional_files");
  if (pdf_input) {
    pdf_input.addEventListener("change", (event) => {
      const file = event.target.files[0];
      const reader_pdf = new FileReader();

      reader_pdf.onprogress = (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          document.getElementById("progress").style.width = `${percentComplete}%`;
        }
      };

      reader_pdf.onloadend = () => {
        document.getElementById("progress").style.width = "100%";
        update_state();
      };

      if (!file) {
        document.getElementById("progress").style.width = "0";
        update_state();
      } else {
        reader_pdf.readAsArrayBuffer(file);
      }
    });
  }
  if(pdf_files) {
      pdf_files.addEventListener("change", (event) => {
      const file = event.target.files[0];
      const reader_pdf = new FileReader();

      reader_pdf.onprogress = (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          document.getElementById("progress-files").style.width = `${percentComplete}%`;
        }
      };

      reader_pdf.onloadend = () => {
        document.getElementById("progress-files").style.width = "100%";
        update_state();
      };

      if (!file) {
        document.getElementById("progress-files").style.width = "0";
        update_state();
      } else {
        reader_pdf.readAsArrayBuffer(file);
      }
    });
  }
}

// Initialize the listeners when the component loads
listenEditFields();
