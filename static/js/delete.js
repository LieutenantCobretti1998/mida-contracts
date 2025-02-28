"use strict";
export default function openPopUpMenu(url, csrf_token) {
       const main_container = document.querySelector(".main_container");
       let delete_type;
       switch (true) {
           case url.includes("delete_company"):
               delete_type = "kompaniyanı";
               break;
           case url.includes("delete_contract"):
               delete_type = "müqaviləni";
               break;
           case url.includes("delete_pdf"):
               delete_type = "əlavə faylı";
               break;
           case url.includes("delete_act"):
               delete_type = "aktı";
               break;
           case url.includes("delete_addition"):
               delete_type = "əlavəni";
               break;
           case url.includes("remove_category"):
               delete_type = "kategoriyanı";
               break;

           case url.includes("delete_user"):
               delete_type = "istifadəçini";
               break;
       }
       main_container.insertAdjacentHTML("afterend",
           `<div class="confirmation_dialog">
                    <h1>Bu ${delete_type} sil ?</h1>
                    <div class="popup_buttons">
                        <button type="button" class="yes">Bəli</button>
                        <button type="button" class="no">Xeyr</button>
                    </div>
                 </div>`
       )
        main_container.insertAdjacentHTML("afterend", `<div class="backdrop"></div>`)
        // Attach event listeners directly to buttons
        const confirmationDialog = document.querySelector(".confirmation_dialog");
        confirmationDialog.querySelector(".yes").addEventListener("click", () => {
            deleteContract(url, csrf_token);
            closePopUpMenu();
        });
        confirmationDialog.querySelector(".no").addEventListener("click", closePopUpMenu);

}

function closePopUpMenu() {
    const confirmation_dialog = document.querySelector(".confirmation_dialog");
    const back_drop = document.querySelector(".backdrop");
    confirmation_dialog.remove();
    back_drop.remove();

}

function deleteContract(url, csrf_token) {
    console.log(url);
    console.log(csrf_token)
    fetch(`${url}`, {
        method: "DELETE",
        headers: {
            "X-CSRF-Token": csrf_token,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {response.json()
        .then(() => {
            window.location.reload();
        })
    })
}

function deletePdf(csrf_token, contract_id, pdf_id) {
    fetch(`/contracts/delete_pdf/${contract_id}/${pdf_id}`, {
        method: "DELETE",
        headers: {
            "X-CSRF-Token": csrf_token,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Deletion failed");
            }
            return response.json();
        })
        .then(data => {
            window.location.href = data.redirect;
        })
        .catch(error => {
            console.error("Error:", error);
        })
}

window.deletePdf = deletePdf;