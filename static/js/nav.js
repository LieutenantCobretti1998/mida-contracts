// toggleMenu

const toggle_menu_element = document.querySelector(".main_container__nav__parameters");
toggle_menu_element.addEventListener("click", (cur_ev) => {
    if(cur_ev.target.classList.contains("remove-pointer") || !cur_ev.target.classList.contains("toggle-menu-button__text")) {
        return;
    }
    const toggle_button = cur_ev.target.closest(".toggle-menu-button");
    if (toggle_button) {
        const parent_container = toggle_button.parentElement;
        const sub_menu = parent_container.nextElementSibling;
        if(sub_menu) {
            toggleSubMenu(sub_menu)
        }
    }
});

function toggleSubMenu(sub_menu) {
    const is_shown = sub_menu.classList.contains("show");
    sub_menu.classList.add("collapsing");
    switch (is_shown) {
            case true:
                sub_menu.classList.remove("show");
                sub_menu.classList.add("collapsing");
                setTimeout(() => {
                    sub_menu.classList.remove('collapsing');
                    sub_menu.classList.add('hidden');
                    }, 500)
                break;
            case false:
                sub_menu.classList.remove("hidden");
                sub_menu.classList.add("collapsing");
                setTimeout(() => {
                    sub_menu.classList.remove('collapsing');
                    sub_menu.classList.add('show');
                    }, 500)
                break;
    }
}