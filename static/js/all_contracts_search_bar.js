const search_label = document.querySelector(".table__header__search__label");

if (search_label) {
    search_label.addEventListener("focus", toggleFocus);
    search_label.addEventListener("blur", toggleFocus);
}

function toggleFocus(event) {
    if (event.type === "focus") {
        search_label.classList.add("focused");
    }
    else if (event.type === "blur") {
        search_label.classList.remove("focused");
    }
}

document.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        document.getElementById("search").focus()
    }
})