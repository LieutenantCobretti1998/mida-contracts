"use strict";

const table = document.querySelector(".table");
const tbody = document.querySelector(".main-table-part");
const aside = document.querySelector(".main_container__nav");
const original_html = table.cloneNode(true);
let new_form;

document.addEventListener("DOMContentLoaded", () => {
    history.pushState({}, "", window.location.pathname);
});

function EditContract() {
    // Remove any existing edit form
    const existingForm = document.querySelector("#edit-form");
    if (existingForm) {
        existingForm.remove();
    }

    // Remove the second table if it exists

    // Prepare the form elements
    const form_elements = {
        company: form_data.company,
        voen: form_data.voen,
        contract: form_data.contract,
        date: form_data.date,
        amount: form_data.amount,
    };
    const save_button = form_data.save_button;

    // Create the new form
    new_form = `
    <form action="${window.url}" method="post" id="edit-form">
        ${window.token}       
    </form>
   `;

    // Insert the new form after the aside element
    aside.insertAdjacentHTML("afterend", new_form);

    // Get the newly created form element
    const form_edit = document.querySelector("#edit-form");

    // Append the original table to the new form
    form_edit.appendChild(table);

    // Update the first row of the table with the form buttons
    const first_tr = tbody.querySelector("tr:first-child td");
    first_tr.innerHTML = `
        <div class="buttons">
               <button type="button" class="cancel" onclick="CancelEdit()">Cancel</button>
               ${save_button}
        </div>
    `;

    // Replace the table cells with input elements
    for (const [id, html] of Object.entries(form_elements)) {
        document.getElementById(id).innerHTML = html;
    }

    // Add edit-mode slug in URL
    history.pushState({}, "", window.location.pathname + "?edit-mode");

    // Add data-edit-mode attribute to the table
    document.querySelector(".table").setAttribute("data-edit-mode", "true");

    const tables = document.querySelectorAll(".table");
    if (tables.length > 1) {
        tables[1].remove();
    }
    // Focus on the first input element
    FocusInput();
    fetchSubmission(form_edit);
}

// cancel logic
function CancelEdit() {
    // Remove the edit form
    const edit_form_element = document.querySelector("#edit-form");
    if (edit_form_element) {
        edit_form_element.remove();
    }

    // Revert to the original table HTML
    aside.insertAdjacentElement("afterend", original_html.cloneNode(true));

    // Remove edit-mode slug in URL
    history.pushState({}, "", window.location.pathname);
}

// Helper function to focus on the first input element in the form
function FocusInput() {
    const firstInput = document.querySelector("#edit-form input");
    if (firstInput) {
        firstInput.focus();
    }
}

function fetchSubmission(form) {
    console.log(form);
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const submitter = event.submitter;
        const form_data = new FormData(form, submitter);

        fetch(form.action, {
            method: "POST",
            body: form_data,
            headers: {
                "X-CSRFToken": form_data.get("csrf_token")
            }
        })
            .then(
                response => response.json()
            )
            .then(
                data => {
                    if (data.errors) {
                        // Clear previous error messages
                        document.querySelectorAll('.error-message').forEach(e => e.remove());

                        // Display new error messages
                        for(const [field, errors] of Object.entries(data.errors)) {
                            const field_element = document.querySelector(`#${field}`);
                            errors.forEach(error => {
                                const error_message = document.createElement("div");
                                error_message.classList.add("error-message");
                                error_message.innerText = error;
                                field_element.appendChild(error_message);
                            })
                        }
                    }
                    else {
                        window.location.href = data.redirect_url;
                    }
                }
            )
    })
}
