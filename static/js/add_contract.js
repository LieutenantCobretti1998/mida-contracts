"use strict"

document.addEventListener("DOMContentLoaded", function () {
    let successMessage = document.querySelector(".error");

    if (successMessage) {
        setTimeout(function () {
            // successMessage.style.display = "none";  // Hide the success message after 4 seconds
            successMessage.parentNode.removeChild(successMessage);  // Remove it from the DOM
        }, 8000);

    }
})



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
    })
    input.addEventListener("blur", function () {
        input.classList.remove("focused");
    })
})
