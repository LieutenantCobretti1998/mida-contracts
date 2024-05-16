// pagination for check list

document.addEventListener("DOMContentLoaded", () => {
    const nextButton = document.querySelector(".next");
    const prevButton = document.querySelector(".prev");
    nextButton.style.pointerEvents = nextButton.hasAttribute("disabled") ? "none": "auto";
    prevButton.style.pointerEvents = prevButton.hasAttribute("disabled") ? "none": "auto";

})


