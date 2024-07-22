"use strict"
function FocusInput() {
     if (document.querySelector(".table").getAttribute("data-edit-mode") === "true") {
         // Focus on input field when press the enter button
        document.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                document.getElementById("default_input").focus();
            }
        })
            // Make the scale when focus on the inout label
            document.querySelectorAll(".table__input").forEach(input => {
                input.addEventListener("focus", function() {
                    input.classList.add("focused");
                });
                input.addEventListener("blur", function () {
                       input.classList.remove("focused");
                });
            });
     }
}
FocusInput();

