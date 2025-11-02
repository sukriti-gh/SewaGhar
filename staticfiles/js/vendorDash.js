
    // JavaScript code for handling sidebar navigation
    const links = document.querySelectorAll(".nav-link[data-target]");
    const defaultSection = document.getElementById("default-section");
    const sections = document.querySelectorAll(".content-section");

    // Event listener for each link
    links.forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent default link behavior

            // Hide all sections including default
            sections.forEach((section) => {
                section.style.display = "none";
            });
            defaultSection.style.display = "none";

            // Show the targeted section
            const target = link.getAttribute("data-target");
            const targetSection = document.getElementById(target);
            if (targetSection) {
                targetSection.style.display = "block";
            } else {
                defaultSection.style.display = "block";
            }
        });
    });
