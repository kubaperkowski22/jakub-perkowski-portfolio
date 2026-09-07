lucide.createIcons();

const menuToggle = document.querySelector(".menu-toggle");
const mainNavigation = document.getElementById("main-navigation");

if (menuToggle && mainNavigation) {

    const closeMenu = () => {
        mainNavigation.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
    };

    menuToggle.addEventListener("click", () => {
        const isOpen = mainNavigation.classList.toggle("is-open");

        menuToggle.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    mainNavigation.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
            menuToggle.focus();
        }
    });
}