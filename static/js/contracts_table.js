import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css';


const grid = new Grid({
   columns: [
                {
                    name: "Contract Id",
                    hidden: true
                },

                {
                    name: "Company Name"
                },
                {
                    name: "Voen"
                },
                {
                    name: "Contract Number"
                },
                {
                    name: "Start Date"
                },
                {
                    name: "End Date"
                },
                {
                    name: "Amount"
                },
                {
                    name: "Remained Amount"
                },
                {
                    name: "Category"
                },
                {
                    name: "Adv Payer",
                    formatter: (_, row) => {
                        const advPayer = row.cells[9].data;
                        return html(
                            `<span>${advPayer ? "Yes": "No"}</span>`
                        )
                    }
                },
                {
                    sort: false,
                    name: "Actions",
                    formatter: (cell, row) => {
                        const contract_id = row.cells[0].data;
                        let action_html = `<button type="button" class="view-btn" data-id=${contract_id}>View</button>`
                        if(role === "admin") {
                            action_html += `<button data-csrf-token=${csrf_token} type="button" class="delete-btn" data-id=${contract_id}>Delete</button>`
                        }
                        return html(`<span style="display: flex; gap: .5rem">${action_html}</span>`);
                    }
                }
            ],
            pagination: {
                limit: 10,
                server : {
                    url: (prev, page, limit) => {
                        const hasQuery = prev.includes("?");
                        const prefix = hasQuery ? "&": "?";
                        return `${prev}${prefix}limit=${limit}&page=${page + 1}`;
                    }
                }
            },
            sort: {
                multiColumn: false,
                server: {
                    url: (prev, columns) => {
                        if (!columns.length) return prev;

                        const col = columns[0];
                        const dir = col.direction === 1 ? "asc": "desc";
                        let colName = ["Contract Id", "Company Name", "Voen", "Contract Number", "Start Date", "End Date", "Amount", "Remained Amount", "Adv Payer", "Category"][col.index];
                        return `${prev}?order_by=${colName}&dir=${dir}`;
                    }
                }
            },
            search: {
                server: {
                    url: (prev, keyword) => `${prev}/${encodeURIComponent(keyword)}`
                }
            },
            server: {
                url:  "/api/all_contracts",
                then: data => data.data.map(contract => [
                    contract.id,
                    contract.company_name,
                    contract.voen,
                    contract.contract_number,
                    new Date(contract.start_date).toLocaleDateString(),
                    new Date(contract.end_date).toLocaleDateString(),
                    parseFloat(contract.amount).toFixed(2),
                    parseFloat(contract.remained_amount).toFixed(2),
                    contract.category,
                    Boolean(contract.adv_payer),
                ]),
                total: data => data.total_count
            },
        })
grid.render(document.getElementById("results"));