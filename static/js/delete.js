"use strict";

export default function openPopUpMenu(url, csrf_token) {
       const main_container = document.querySelector(".main_container");
       let delete_type;
       switch (true) {
           case url.includes("delete_company"):
               delete_type = "company";
               break;
           case url.includes("delete_contract"):
               delete_type = "contract";
               break;
           case url.includes("delete_act"):
               delete_type = "act";
               break;
           case url.includes("remove_category"):
               delete_type = "category";
               break;
       }
       main_container.insertAdjacentHTML("afterend",
           `<div class="confirmation_dialog">
                    <h1>Are you sure you want to delete this ${delete_type} ?</h1>
                    <div class="popup_buttons">
                        <button type="button" class="yes">Yes</button>
                        <button type="button" class="no">No</button>
                    </div>
                 </div>`
       )
        main_container.insertAdjacentHTML("afterend", `<div class="backdrop"></div>`)
        // Attach event listeners directly to buttons
        const confirmationDialog = document.querySelector(".confirmation_dialog");
        confirmationDialog.querySelector(".yes").addEventListener("click", () => deleteContract(url, csrf_token));
        confirmationDialog.querySelector(".no").addEventListener("click", closePopUpMenu);

}

function closePopUpMenu() {
    const confirmation_dialog = document.querySelector(".confirmation_dialog");
    const back_drop = document.querySelector(".backdrop");
    confirmation_dialog.remove();
    back_drop.remove();

}

function deleteContract(url, csrf_token) {
    fetch(`${url}`, {
        method: "DELETE",
        headers: {
            "X-CSRF-Token": csrf_token,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {response.json()
        .then(data => {
            if (data.status === "success") {
                window.location.reload();
            }
            else {
                window.location.reload();
            }
        })
    })
}