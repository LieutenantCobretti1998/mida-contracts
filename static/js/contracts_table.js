import { Grid, html } from 'gridJs'; // Using the alias
import 'gridJs/dist/theme/mermaid.css';


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
                    name: "Contract Id",
                    hidden: true
                },

                {
                    name: "Şirkətin adı",
                    sort: !search_mode
                },
                {
                    name: "VÖEN",
                    label: "VÖEN",
                    sort: !search_mode
                },
                {
                    name: "Müqavilə Nömrəsi"
                },
                {
                    name: "Başlama tarixi"
                },
                {
                    name: "Bitmə tarixi"
                },
                {
                    name: "Məbləğ"
                },
                {
                    name: "Qalan məbləğ"
                },
                {
                    name: "Kategoriya"
                },
                {
                    name: "Status",
                    formatter: (_, row) => {
                        const contract_status = row.cells[9].data;
                        return html(
                            `<span>${contract_status ? "Davam Edir": "Bitib"}</span>`
                        )
                    }
                },
                {
                    sort: false,
                    name: "Əməliyyatlar",
                    formatter: (cell, row) => {
                        const contract_id = row.cells[0].data;
                        let action_html = `<button type="button" class="view-btn" data-id=${contract_id}>Bax</button>`
                        if(role === "admin") {
                            action_html += `<button data-csrf-token=${csrf_token} type="button" class="delete-btn" data-id=${contract_id}>Sil</button>`
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
                        let colName = ["Contract Id", "Company Name", "Voen", "Contract Number", "Start Date", "End Date", "Amount", "Remained Amount", "Category", "Is Existed"][col.index];
                        return `${prev}?order_by=${colName}&dir=${dir}`;
                    }
                }
            },
            server: {
                url:  search_mode ? `/api/all_contracts/${company_voen}`: "/api/all_contracts",
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
                    Boolean(contract.is_existed),
                ]),
                total: data => data.total_count
            },
            ...(!search_mode && {
                    search: {
                        server: {
                            url: (prev, keyword) => `${prev}/${encodeURIComponent(keyword)}`
                        }
                    }
            })
        })
grid.render(document.getElementById("results"));

const headers = document.querySelectorAll("#results th");  // Select header elements
headers.forEach((header, index) => {
    const columnName = grid.config.columns[index].name;
    header.textContent = columnName;  // Replace with label if available
});