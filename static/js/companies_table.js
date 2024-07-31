import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css'; // Importing the CSS using the alias

const grid = new Grid({
    columns: [
                {
                    name: "Company Id",
                    hidden: true
                },

                {
                    name: "Company Name"
                },
                {
                    name: "Voen"
                },
                {
                    name: "Related Contracts"
                },
                {
                    sort: false,
                    name: "Actions",
                    formatter: (cell, row) => {
                        const company_id = row.cells[0].data;
                         return html(
                               `<span style="display: flex; justify-content: space-between">` +
                                    `<button type="button" class="view-btn" data-id=${company_id}>View</button>` +
                                    `<button data-csrf-token=${csrf_token} type="button" class="delete-btn" data-id=${company_id}>Delete</button>`+
                               `</span>`
                           );
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
                        let colName = ["Company Id", "Company Name", "Voen", "Related Contracts"][col.index];
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
                url: "/api/all_companies",
                then: data => data.data.map(company => [
                    company.id,
                    company.company_name,
                    company.voen,
                    company.related_contracts
                ]),
                total: data => data.total_count
            },
})
grid.render(document.getElementById("results"));