import {Grid} from "gridjs";
import 'gridJs/dist/theme/mermaid.css';
const contract_end_date_grid = new Grid({
    style: {
        table: {
            'font-size': '1.5rem'
        },
        td: {
            'backgroundColor': '#669ac5',
            'color': 'white',
        },
        th: {
            'backgroundColor': '#669ac5',
            'color': 'white',
        },
        footer: {
            'backgroundColor': '#669ac5',
            'color': 'white',
        },
        container: {
            "borderRadius": "10px",
        }
    },
   columns: [
                {
                    name: "#",
                },

                {
                  name: "Company Name"
                },

                {
                    name: "Contract Number"
                },
                {
                    name: "Days Left"
                },

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

            server: {
                url:  "/api/contracts_ending",
                then: (data) => data.contracts_to_end.map((contract, index) => [
                    contract.offset + 1 + index,
                    contract.company_name,
                    contract.contract_name,
                    contract.contract_days_left,
                ]),
                total: data => data.total_count
            },
        })
contract_end_date_grid.render(document.getElementById("calculations-date"));

const contract_end_money_grid = new Grid({
    style: {
        table: {
            'font-size': '1.5rem'
        },
        td: {
            'backgroundColor': '#669ac5',
            'color': 'white',
        },
        th: {
            'backgroundColor': '#669ac5',
            'color': 'white',
        },
        footer: {
            'backgroundColor': '#669ac5',
            'color': 'white',
        },
        container: {
            "borderRadius": "10px",
        }
    },
   columns: [
                {
                    name: "#",
                },

                {
                    name: "Company Name",
                },

                {
                    name: "Contract Number"
                },
                {
                    name: "Amount Left"
                },

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

            server: {
                url:  "/api/contracts_ending_amount",
                then: (data) => data.contracts_to_end.map((contract, index) => [
                    contract.offset + 1 + index,
                    contract.company_name,
                    contract.contract_name,
                    parseFloat(contract.contract_amount_left).toFixed(2),
                ]),
                total: data => data.total_count
            },
})

contract_end_money_grid.render(document.getElementById("calculations-amount"));