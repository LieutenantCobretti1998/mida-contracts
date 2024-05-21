"use strict"

function clearURL() {
    const form = document.querySelector(".table__header__search form");
    const all_contracts =  document.querySelector("button[name='action'][value='all']");
    const search_button = document.querySelector("button[name='action'][value='search']")

    form.addEventListener("submit", () => {
        if (document.activeElement === all_contracts) {
            document.getElementById('filter-selection').value = '';
            document.getElementById('order-selection').value = '';
        }
    })
}

clearURL();