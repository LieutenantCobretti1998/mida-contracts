"use strict";

function openPopUpMenu() {
       const main_container = document.querySelector(".main_container");
       main_container.insertAdjacentHTML("afterend",
           `<div class="confirmation_dialog">
                    <h1>Are you sure you want to delete this contract ?</h1>
                    <div class="popup_buttons">
                        <button onclick="deleteContract()" type="button" class="yes">Yes</button>
                        <button onclick="closePopUpMenu()" type="button" class="no">No</button>
                    </div>
                 </div>`
       )
        main_container.insertAdjacentHTML("afterend", `<div class="backdrop"></div>`)

}

function closePopUpMenu() {
    const confirmation_dialog = document.querySelector(".confirmation_dialog");
    const back_drop = document.querySelector(".backdrop");
    confirmation_dialog.remove();
    back_drop.remove();

}

function deleteContract() {
    fetch(form_url, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrf_token
        }
    })
    .then(response => {response.json()
    .then(data => {
        if (data.status === "success") {
            window.location.href = data.redirect_url;
        }
    })
    })

}