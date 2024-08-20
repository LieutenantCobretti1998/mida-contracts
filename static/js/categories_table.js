"use strict";
import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css'; // Importing the CSS using the alias

const grid = new Grid( {
    columns: [
        {
            hidden: true,
            name: "Category id"
        },

        {
            name: "Category",
        },

        {
            sort: false,
            name: "Actions",
            formatter: (cell, row) => {
                        const category_id = row.cells[0].data;
                         return html(
                               `<span style="display: flex; justify-content: space-between">` +
                                    `<button data-csrf-token=${csrf_token} type="button" class="delete-btn" data-id=${category_id}>Delete</button>`+
                               `</span>`
                           );
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
                        let colName = ["Category id", "Category"][col.index];
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
                url: `/api/all_categories`,
                then: data => data.data.map(category => [
                    category.id,
                    category.category_name,
                ]),
                total: data => data.total_count
            },
})
grid.render(document.getElementById("results"));

document.getElementById("save").addEventListener("click", () => {
    const category_input = document.getElementById("default_input");
    const category_name = category_input.value.trim();
    if(category_name === "") {
        alert("Please enter a category name, not an empty input :3");
        return;
    }

    fetch(`/api/all_categories/add_category`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrf_token // Include CSRF token if needed
        },
        body: JSON.stringify({category: category_name})
    })

        .then(() => {
            // Clear the input field
            // Update the grid with the new data
            grid.updateConfig({
                server: {
                    url: `/api/all_categories`,
                    then: data => data.data.map(category => [
                         category.id,
                        category.category_name,
                    ]),
                    total: data => data.total_count
                }
            }).forceRender();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while saving the category.');
        })
        .finally(() => {
             category_input.value = "";
        })

})