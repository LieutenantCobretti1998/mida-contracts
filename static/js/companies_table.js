import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css'; // Importing the CSS using the alias

const grid = new Grid({
    language: {
        "search": {
            "placeholder": "🔍 Axtar",
        },
        "pagination": {
            "previous": "Əvvəlki",
            "next": "Növbəti️",
            "showing": "Göstərilir",
             to: '-dən',
             of: '-qədər Cəmi',
            "results": "Nəticə",
        },
        noRecordsFound: "Uyğun qeydlər tapılmadı",
        error: "Məlumatların çıxarılması zamanı xəta baş verdi"
    },
    columns: [
                {
                    name: "Company Id",
                    hidden: true
                },

                {
                    name: "Şirkətin adı"
                },
                {
                    name: "Vöen"
                },
                {
                    name: "Əlaqədar Müqavilələr"
                },
                {
                    sort: false,
                    name: "Əməliyyatlar",
                    formatter: (cell, row) => {
                        const company_id = row.cells[0].data;
                        let action_html = `<button type="button" class="view-btn" data-id=${company_id}>Bax</button>`;
                        if(role === "admin") {
                            action_html += `<button data-csrf-token=${csrf_token} type="button" class="delete-btn" data-id=${company_id}>Sil</button>`
                        }
                         return html(`<span style="display: flex; justify-content: space-between">${action_html}</span>`)
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