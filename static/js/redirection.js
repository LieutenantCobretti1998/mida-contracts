"use strict"
import openPopUpMenu from "./delete.js";

function attachEventHandlers() {
    document.addEventListener('DOMContentLoaded', () => {
        const gridContainer = document.querySelectorAll(".results-table");
        gridContainer.forEach(grid => {
            grid.addEventListener("click", (event) => {
            const contract_id = event.target.getAttribute("data-id");
            const category_name = event.target.getAttribute("data-value");
            const data_voen = event.target.getAttribute("data-voen");
            const csrf_token = event.target.getAttribute("data-csrf-token");
            console.log("hello")
            switch (true) {
                case event.target.classList.contains("pdf-btn"):
                     viewPdf(Number(contract_id));
                     break;
                case event.target.classList.contains("delete-btn"):
                    if (event.target.classList.contains("additions")) {
                        deleteFullUrl(contract_id, csrf_token, true);
                        break;
                    }
                    deleteFullUrl(contract_id, csrf_token);
                    break;
                case event.target.classList.contains("view-btn"):
                    if(event.target.classList.contains("additions")) {
                        viewContractOrCompany(contract_id, true);
                    }
                    viewContractOrCompany(contract_id);
                    break;
                case event.target.classList.contains("related-btn"):
                    openRelatedContracts(data_voen);
                    break;
                case event.target.classList.contains("edit-btn"):
                    editCategory(contract_id, category_name, csrf_token);
                    break;
            }
        });
        })

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
 * @param {boolean} addition
 */
function deleteFullUrl(id, csrf_token, addition= false) {
    const url_for_deletion = `${!addition ? delete_url_base: delete_url_base_addition}${id}`;
    openPopUpMenu(url_for_deletion, csrf_token);
}

/**
 *
 * @param {number} id
 * @param {boolean} addition
 */
function viewContractOrCompany(id, addition= false) {
  !addition ? window.open(`${view_url_base}${id}`): window.open(`${view_url_base_addition}${id}`);
}


/**
 *
 * @param {string} voen
 */
function openRelatedContracts(voen) {
    window.open(`${related_contracts_url_base}${voen}`)
}

/**
 *
 * @param {number} id
 * @param {string} category_name
 * @param {string} csrf_token
 */
async function editCategory(id, category_name, csrf_token) {
    const message_container = document.getElementById("message-container");
    if(category_name === "") {
            alert("Please enter a category name, not an empty input :3");
            return;
        }
    const data = {
        id: id,
        category_name: category_name,
    }
    try {
        const response = await fetch('/api/all_categories/update_category', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrf_token
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message);
        }
        const update_status = await response.json();
        message_container.innerHTML = `
                <div class="error">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                        <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-1.25 16.518l-4.5-4.319 1.396-1.435 3.078 2.937 6.105-6.218 1.421 1.409-7.5 7.626z"></path>
                    </svg>
                    <div class="error__description">
                        <strong>Success</strong>
                        <p class="error__text">${update_status.message}</p>
                    </div>
                </div>
                `;
    }
    catch(error) {
        message_container.innerHTML = `
                <div class="error">
                    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="256" height="256" viewBox="0 0 256 256" xml:space="preserve">
                        <defs></defs>
                        <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;" transform="translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)">
                            <path d="M 45 90 C 20.187 90 0 69.813 0 45 C 0 20.187 20.187 0 45 0 c 24.813 0 45 20.187 45 45 C 90 69.813 69.813 90 45 90 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(229,0,0); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0)" stroke-linecap="round"></path>
                            <path d="M 45 57.469 L 45 57.469 c -1.821 0 -3.319 -1.434 -3.399 -3.252 L 38.465 23.95 c -0.285 -3.802 2.722 -7.044 6.535 -7.044 h 0 c 3.813 0 6.82 3.242 6.535 7.044 l -3.137 30.267 C 48.319 56.036 46.821 57.469 45 57.469 z" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(255,255,255); fill-rule: nonzero; opacity: 1;" transform=" matrix(1 0 0 1 0 0)" stroke-linecap="round"></path>
                            <circle cx="45" cy="67.67" r="5.42" style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(255,255,255); fill-rule: nonzero; opacity: 1;" transform="  matrix(1 0 0 1 0 0)"></circle>
                        </g>
                    </svg>
                    <div class="error__description">
                        <strong>Error</strong>
                        <p class="error__text">${error}</p>
                    </div>
                </div>
                `;
    }
}



