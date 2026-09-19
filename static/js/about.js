document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn =
        document.getElementById("toggle-all-btn");

    const detailsElements = [
        ...document.querySelectorAll(
            "details.info-group"
        ),
    ];


    // Expand / collapse all sections
    if (toggleBtn) {
        toggleBtn.addEventListener(
            "click",
            () => {
                const shouldOpen =
                    !detailsElements.every(
                        (detail) => detail.open
                    );

                detailsElements.forEach(
                    (detail) => {
                        detail.open =
                            shouldOpen;
                    }
                );
            }
        );
    }


    // Open section referenced by URL hash
    function openSectionFromHash() {
        const sectionId =
            decodeURIComponent(
                window.location.hash.slice(1)
            );

        if (!sectionId) {
            return;
        }

        const target =
            document.getElementById(
                sectionId
            );

        if (!target) {
            return;
        }

        let detail = null;

        // ID is directly on <details>
        if (
            target.matches(
                "details.info-group"
            )
        ) {
            detail = target;
        }

        // ID is on a wrapper containing <details>
        if (!detail) {
            detail = target.querySelector(
                "details.info-group"
            );
        }

        // ID is somewhere inside <details>
        if (!detail) {
            detail = target.closest(
                "details.info-group"
            );
        }

        if (detail) {
            detail.open = true;
        }

        requestAnimationFrame(() => {
            target.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        });
    }


    // Direct entry:
    // /o-mnie?lang=pl#education
    openSectionFromHash();


    // Hash changed while page is already open
    window.addEventListener(
        "hashchange",
        openSectionFromHash
    );
});