import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css';

const grid = new Grid({
   columns: [
                {
                    name: "User Id",
                    hidden: true
                },

                {
                    name: "User Name"
                },
                {
                    name: "Role"
                },
                {
                    sort: false,
                    name: "Actions",
                    formatter: (cell, row) => {
                        const user_id = row.cells[0].data;
                        return html(`<span style="display: flex; justify-content: space-between">\<button data-csrf-token=${csrf_token} type="button" class="delete-btn" data-id=${user_id}>Delete</button>\</span>`);
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
                        let colName = ["User Id", "User Name", "Role"][col.index];
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
                url:  "/api/all_users",
                then: data => data.data.map(user => [
                    user.id,
                    user.user_name,
                    user.role,
                ]),
                total: data => data.total_count
            },
        })
grid.render(document.getElementById("results"));