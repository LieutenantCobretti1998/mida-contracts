"use strict";
import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css'; // Importing the CSS using the alias

const grid = new Grid( {
    columns: [
        {
            name: 'Act id',
            hidden: true
        },

        {
            name: "Act Number",
        },
        {
            name: "Act Amount",
        },
        {
            name: "Date"
        },
        {
            sort: false,
            name: "Actions",
            formatter: (cell, row) => {
                        const act_id = row.cells[0].data;
                        let action_html = `<button type="button" class="view-btn" data-id=${act_id}>View</button>`;
                        if(role === "admin") {
                            action_html += `<button type="button" class="delete-btn" data-id=${act_id}>Delete</button>`
                        }
                         return html(`<span style="display: flex; justify-content: space-between">${action_html}</span>`)
                    }
        }
    ],
    pagination: {
                limit: 5,
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
                        let colName = ["Act id", "Act number", "Act amount", "Date"][col.index];
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
                url: `/api/related_acts/${contract_id}`,
                then: data => data.data.map(act => [
                    act.id,
                    act.act_number,
                    parseFloat(act.amount).toFixed(2),
                    new Date(act.date).toLocaleDateString()
                ]),
                total: data => data.total_count
            },
})
grid.render(document.getElementById("results"));