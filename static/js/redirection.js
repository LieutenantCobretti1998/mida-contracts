"use strict"
import openPopUpMenu from "./delete.js";

function attachEventHandlers() {
    document.addEventListener('DOMContentLoaded', () => {
        const gridContainer = document.getElementById("results"); // The parent element of your grid
        gridContainer.addEventListener("click", (event) => {
            const contract_id = event.target.getAttribute("data-id");
            const data_voen = event.target.getAttribute("data-voen");
            const csrf_token = event.target.getAttribute("data-csrf-token");
            switch (true) {
                case event.target.classList.contains("pdf-btn"):
                     viewPdf(Number(contract_id));
                     break;
                case event.target.classList.contains("delete-btn"):
                    deleteFullUrl(contract_id, csrf_token);
                    break;
                case event.target.classList.contains("view-btn"):
                    viewContractOrCompany(contract_id);
                    break;
                case event.target.classList.contains("related-btn"):
                    openRelatedContracts(data_voen);
                    break;
            }
        });
    });
}
attachEventHandlers();

/**
 * Redirects to the pdf view url
 * @param {number} contract_id - The id of thew contract
 */
function viewPdf(contract_id) {

    window.open(`${pdf_url_base}${contract_id}`);
}

/**
 *
 * @param {number} id
 * @param {string} csrf_token
 */
function deleteFullUrl(id, csrf_token) {
    const url_for_deletion = `${delete_url_base}${id}`;
    openPopUpMenu(url_for_deletion, csrf_token);
}

/**
 *
 * @param {number} id
 */
function viewContractOrCompany(id) {
   window.open(`${view_url_base}${id}`);
}


/**
 *
 * @param {string} voen
 */
function openRelatedContracts(voen) {
    window.open(`${related_contracts_url_base}${voen}`)
}



