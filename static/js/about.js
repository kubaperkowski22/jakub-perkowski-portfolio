const toggleBtn = document.getElementById("toggle-all-btn");
const detailsElements = document.querySelectorAll("details.info-group");

let isExpanded = false;

toggleBtn.addEventListener("click", () => {
    isExpanded = !isExpanded;

    detailsElements.forEach((detail) => {
        if (isExpanded) {
            detail.setAttribute("open", "");
        } else {
            detail.removeAttribute("open");
        }
    });
});