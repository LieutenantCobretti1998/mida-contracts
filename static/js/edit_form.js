"use strict";

const table = document.querySelector(".table");
const tbody = document.querySelector("tbody");
const aside = document.querySelector(".main_container__nav");
let original_html = tbody.outerHTML;
console.log(original_html);
let new_form;

document.addEventListener("DOMContentLoaded", () => {
    history.pushState({}, "", window.location.pathname);
});

function EditContract() {
    const form_elements = {
        company: form_data.company,
        voen: form_data.voen,
        contract: form_data.contract,
        date: form_data.date,
        amount: form_data.amount,
    };
    const save_button = form_data.save_button;
    new_form = `
    <form action="${window.url}" method="post" id="edit-form">
        ${window.token}       
    </form>
   `;
    aside.insertAdjacentHTML("afterend", new_form);
    const first_tr = tbody.querySelector("tr:first-child td");
    first_tr.innerHTML = `
        <div class="buttons">
               <button type="button" class="cancel" onclick="CancelEdit()">Cancel</button>
               ${save_button}
        </div>
    `;
    for (const [id, html] of Object.entries(form_elements)) {
        document.getElementById(id).innerHTML = html;
    }
    const form_edit = document.querySelector("#edit-form");
    form_edit.appendChild(table);
    // Add edit-mode slug in url
    history.pushState({}, "", window.location.pathname + "?edit-mode");
    document.querySelector(".table").setAttribute("data-edit-mode", "true");
    console.log(original_html);
    FocusInput();
}

// cancel logic
function CancelEdit() {
    // Revert original html
    const edit_form_element = document.querySelector("#edit-form");
    if (edit_form_element) {
        edit_form_element.remove();
    }
    console.log(original_html);
    tbody.innerHTML = original_html;
    aside.insertAdjacentElement("afterend", table);
    table.removeAttribute("data-edit-mode");
    history.pushState({}, "", window.location.pathname);
}

// Helper function to focus on the first input element in the form
function FocusInput() {
    const firstInput = document.querySelector("#edit-form input");
    if (firstInput) {
        firstInput.focus();
    }
}

