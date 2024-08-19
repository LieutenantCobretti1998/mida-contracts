"use strict";

document.addEventListener("DOMContentLoaded", function() {
    const company_input = document.querySelector("input[list='companies_list']");
    const data_list = document.getElementById("companies_list");
    const contract_list = document.getElementById("contracts_list");

    company_input.addEventListener("input", e => {
        const query = company_input.value;
         data_list.innerHTML = "" ? company_input.value = '': null;
         contract_list.innerHTML = "" ? company_input.value = '': null;
         contract_list.classList.add("hidden");
        if (query.length > 3) {
            contract_list.classList.remove("hidden");
            getRelatedCompanies(query).then(data => {
                if(data.length > 0) {
                    let final_value = updateList(data, data_list);
                    if(final_value) {
                        getRelatedContracts(query).then(data => {
                            if(data.length > 0) {
                                updateContractList(data, contract_list);

                            }
                        })
                    }
                }
            })
        }
    })
})

/**
 *
 * @param query {string}
 * @returns {Promise<void>}
 */

async function getRelatedCompanies(query) {
    const route = `/api/all_companies/related_companies/${query}`;

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
 * @param query
 * @return {Promise<void>}
 */
async function getRelatedContracts(query) {
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
 * @param query {string}
 * @return {Promise<void>}
 */
async function getContractInfo(query) {
    const route = `/api/all_contracts/related_contract/${query}`;

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
 * @return {string}
 */
function updateList(data, data_list) {
    data_list.innerHTML = "";

    data.forEach(company => {
        const option = document.createElement("option");
        option.value = company;
        data_list.appendChild(option);
    });

    if (data_list.children.length === 1) {
        return data_list.children[0].getAttribute("value");
    }
}

/**
 *
 * @param data {Object}
 * @param contracts_list {HTMLSelectElement}
 */
function updateContractList(data, contracts_list) {
    contracts_list.innerHTML = "";

    data.forEach(contract => {
        const option = document.createElement("option");
        option.value = contract.contract_number;
        option.textContent = contract.contract_number;
        option.setAttribute("data-id", contract.id);
        contracts_list.appendChild(option);
    });

    const handle_selection_change = function () {
        const selected_option = this.options[this.selectedIndex];
        const data_id = selected_option.getAttribute("data-id");
        const act_amount_el = document.querySelector("#act_amount");
        const addition_amount_el = document.querySelector("#addition_amount");
        const remained_amount_el = document.querySelector("#remained_amount");
        getContractInfo(data_id).then(data => {
            if (data && type_of_page === "acts") {
                updateContractDetails(data);
                act_amount_el.addEventListener("input", () => {
                    calculateRemainedMoney(remained_amount_el, data.remained_amount, act_amount_el);
                })
            } else {
                updateContractDetails(data);
                const total_contract_amount_el = document.querySelector("#amount");
                addition_amount_el.addEventListener("input", () => {
                    calculateAdditionalMoney(remained_amount_el, data.remained_amount, addition_amount_el, total_contract_amount_el, data.amount);
                })
            }
        })
    }
    contracts_list.addEventListener("change",handle_selection_change);
    if (contracts_list.options.length > 0) {
        contracts_list.selectedIndex = 0;
        handle_selection_change.call(contracts_list);
    }

    contracts_list.addEventListener("change", function () {
        const selected_option = this.options[this.selectedIndex];
        const data_id = selected_option.getAttribute("data-id");
        getContractInfo(data_id).then(data => {
            if (data) {
                updateContractDetails(data);
            }
        })

    })
}

/**
 *
 * @param data{Object}
 */
function updateContractDetails(data) {
    for(const key in data) {
        if(key === "id") {
            const contract_id = document.getElementById("contract_id");
            contract_id.value = data["id"];
            continue
        }
        const element = document.getElementById(key);
        switch (element.id) {
                        case "amount":
                            element.innerText = parseFloat(data[key]).toFixed(2);
                            break;
                        case "remained_amount":
                            const remained_amount_el = document.querySelector("#remained_amount");
                            remained_amount_el.innerText = parseFloat(data[key]).toFixed(2);
                            break;
                        case "date":
                            element.innerText = new Date(data[key]).toLocaleDateString();
                            break;
                        case "adv_payer":
                         element.innerText = data[key] ? "Yes" : "No";
                         break;
                        case "pdf_file":
                            element.innerHTML = "";
                            const button = document.createElement("button");
                            button.classList.add("pdf-btn");
                            button.type = "button";
                            button.textContent = "View";
                            button.addEventListener("click", function (event) {
                                window.open(`/contracts/preview_pdf/${data["id"]}`)
                            });
                            element.appendChild(button);
                            break;
                        default:
                            element.innerText = data[key];
                }
            }
}

/**
 *
 * @param {HTMLElement} remained_amount_el
 * @param {string} remain_contract_amount
 * @param {HTMLElement} act_amount_el
 */
function calculateRemainedMoney(remained_amount_el, remain_contract_amount, act_amount_el) {
    if (act_amount_el.value === "") {
         remained_amount_el.innerText = Number.parseFloat(remain_contract_amount).toFixed(2);
        return;
    }
    const remained_amount = Number.parseFloat(remain_contract_amount) - Number.parseFloat(act_amount_el.value);
    remained_amount_el.innerText = remained_amount.toFixed(2);
}


/**
 *
 * @param {HTMLElement} remained_amount_el
 * @param {string} remain_contract_amount
 * @param {HTMLElement} addition_amount_el
 * @param {HTMLElement} total_amount_el
 * @param {string} total_amount
 */
function calculateAdditionalMoney(remained_amount_el, remain_contract_amount, addition_amount_el,
                                  total_amount_el, total_amount) {
    if (addition_amount_el.value === "") {
         remained_amount_el.innerText = Number.parseFloat(remain_contract_amount).toFixed(2);
         total_amount_el.innerText = Number.parseFloat(total_amount).toFixed(2);
        return;
    }
    const remained_amount = Number.parseFloat(remain_contract_amount) + Number.parseFloat(addition_amount_el.value);
    const new_total_amount = Number.parseFloat(total_amount) + Number.parseFloat(addition_amount_el.value);
    remained_amount_el.innerText = remained_amount.toFixed(2);
    total_amount_el.innerText = new_total_amount.toFixed(2);
}



