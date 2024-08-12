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
            const open_icon = parent_container.querySelector(".submenu-icon");
            toggleSubMenu(sub_menu, open_icon)
        }
    }
});

// function toggleSubMenu(sub_menu, arrow) {
//     const is_shown = sub_menu.classList.contains("show");
//     sub_menu.classList.add("collapsing");
//     switch (is_shown) {
//         case true:
//                 sub_menu.classList.remove("show");
//                 sub_menu.classList.add("collapsing");
//                 arrow.classList.remove("rotated-up");
//                 arrow.classList.add("rotated-down");
//                 setTimeout(() => {
//                     arrow.classList.remove("rotated-down");
//                     sub_menu.classList.remove('collapsing');
//                     sub_menu.classList.add('hidden');
//                     }, 500)
//                 break;
//             case false:
//                 sub_menu.classList.remove("hidden");
//                 sub_menu.classList.add("collapsing");
//                 arrow.classList.add("rotated-up");
//                 setTimeout(() => {
//                     sub_menu.classList.remove('collapsing');
//                     sub_menu.classList.add('show');
//                     }, 500)
//                 break;
//     }
// }

function toggleSubMenu(sub_menu, open_icon) {
    const is_shown = sub_menu.classList.contains("show");

    switch (is_shown) {
        case true:
            sub_menu.classList.remove("show");
            sub_menu.classList.add("hidden");
            open_icon.innerHTML = `<svg fill="currentColor" clip-rule="evenodd" fill-rule="evenodd" stroke-linejoin="round" stroke-miterlimit="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m15.97 17.031c-1.479 1.238-3.384 1.985-5.461 1.985-4.697 0-8.509-3.812-8.509-8.508s3.812-8.508 8.509-8.508c4.695 0 8.508 3.812 8.508 8.508 0 2.078-.747 3.984-1.985 5.461l4.749 4.75c.146.146.219.338.219.531 0 .587-.537.75-.75.75-.192 0-.384-.073-.531-.22zm-5.461-13.53c-3.868 0-7.007 3.14-7.007 7.007s3.139 7.007 7.007 7.007c3.866 0 7.007-3.14 7.007-7.007s-3.141-7.007-7.007-7.007zm-.744 6.26h-2.5c-.414 0-.75.336-.75.75s.336.75.75.75h2.5v2.5c0 .414.336.75.75.75s.75-.336.75-.75v-2.5h2.5c.414 0 .75-.336.75-.75s-.336-.75-.75-.75h-2.5v-2.5c0-.414-.336-.75-.75-.75s-.75.336-.75.75z" fill-rule="nonzero"/></svg>`
            break;
        case false:
            sub_menu.classList.remove("hidden");
            sub_menu.classList.add("show");
            open_icon.innerHTML = `<svg fill="currentColor" clip-rule="evenodd" fill-rule="evenodd" stroke-linejoin="round" stroke-miterlimit="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m15.97 17.031c-1.479 1.238-3.384 1.985-5.461 1.985-4.697 0-8.509-3.812-8.509-8.508s3.812-8.508 8.509-8.508c4.695 0 8.508 3.812 8.508 8.508 0 2.078-.747 3.984-1.985 5.461l4.749 4.75c.146.146.219.338.219.531 0 .587-.537.75-.75.75-.192 0-.384-.073-.531-.22zm-5.461-13.53c-3.868 0-7.007 3.14-7.007 7.007s3.139 7.007 7.007 7.007c3.866 0 7.007-3.14 7.007-7.007s-3.141-7.007-7.007-7.007zm3.256 6.26h-6.5c-.414 0-.75.336-.75.75s.336.75.75.75h6.5c.414 0 .75-.336.75-.75s-.336-.75-.75-.75z" fill-rule="nonzero"/></svg>`
             break;

    }

}