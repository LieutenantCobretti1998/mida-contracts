// Loading screen logic
const form = document.querySelector("form");
const loader = document.querySelector(".loader");
const table = document.querySelector(".table");

document.addEventListener("DOMContentLoaded", function () {
    // loader.style.display = "none";
    // table.style.display = "table";
    form.onsubmit = function () {
        loader.style.display = "block";
        table.style.display = "none";
    };
})
