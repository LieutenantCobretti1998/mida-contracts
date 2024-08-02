"use strict";

document.addEventListener("DOMContentLoaded", function() {
    const company_input = document.querySelector("input[list='companies_list']");
    const data_list = document.getElementById("companies_list");
    const contract_list = document.getElementById("contracts_list");

    company_input.addEventListener("input", e => {
        const query = company_input.value;
         data_list.innerHTML = "" ? company_input.value = '': null;
         contract_list.classList.add("hidden");
        if (query.length > 3) {
            contract_list.classList.remove("hidden");
            getRelatedContracts(query, data_list).then(data => {
                if(data.length > 0) {
                    updateList(data, data_list);
                    updateContractList(data, contract_list);

                }
            });
        }
    });
})

/**
 *
 * @param query {string}
 * @param data_list {HTMLDataListElement}
 * @returns {Promise<void>}
 */

async function getRelatedContracts(query, data_list) {
    const route = `/api/all_companies/related_contracts/${query}`;

    try {
        const response = await fetch(route);
        if (!response.ok) {
            throw new Error("Could not fetch related contracts");
        }
        return await response.json()
    }
    catch (error) {
        console.error(error.message)
    }
}

/**
 *
 * @param data{Object}
 * @param data_list{HTMLDataListElement}
 */
function updateList(data, data_list) {
    data_list.innerHTML = "";

    data.forEach(company => {
        const option = document.createElement("option");
        option.value = company;
        option.addEventListener("click", e => {
            console.log("clicked")
            const options = data_list.querySelectorAll("option");
            options.forEach((option) => {option.removeAttribute("selected")});


            if (e.target.tagName === 'option') {
            e.target.setAttribute('selected', 'selected');
            }
        })
        data_list.appendChild(option);
    });
}

/**
 *
 * @param data
 * @param contracts_list
 */
function updateContractList(data, contracts_list) {

}



