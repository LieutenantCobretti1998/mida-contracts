"use strict"
const table = document.querySelector(".table");
let original_html

document.addEventListener("DOMContentLoaded", () => {
    history.pushState({}, "", window.location.pathname);
})

function EditContract() {
   const form_elements = {
       company: form_data.company,
       voen: form_data.voen,
       contract: form_data.contract,
       date: form_data.date,
       amount: form_data.amount,
   };
   original_html = table.innerHTML;
    const save_button = form_data.save_button;
   for (const[id, html] of Object.entries(form_elements))  {
       document.getElementById(id).innerHTML = html;
   }
   const form_td = document.getElementById("form");
   form_td.innerHTML = `
    <form action=${window.url} method="post">
            ${window.token}
            <div class="buttons">
                <button type="button" class="cancel" onclick="CancelEdit()">Cancel</button>
                ${save_button}
            </div>
        </form>
   `
   // Add edit-mode slug in url
    history.pushState({}, "", window.location.pathname + "?edit-mode")
   document.querySelector(".table").setAttribute("data-edit-mode", "true");
   FocusInput();
}

// cancel logic
function CancelEdit() {
    // Revert original html
    table.innerHTML = original_html;
    history.pushState({}, "", window.location.pathname);
}

