// Get all sidebar links
const links = document.querySelectorAll(".nav-link[data-target]");
const defaultSection = document.getElementById("default-section");
const sections = document.querySelectorAll(".content-section");

// Function to filter tables
function filterTable(inputId, tableId) {
  document.getElementById(inputId).addEventListener('keyup', function () {
    let filter = this.value.toUpperCase();
    let rows = document.querySelectorAll(`#${tableId} tr`);

    rows.forEach(function (row) {
      let td = row.getElementsByTagName('td')[0];
      if (td) {
        let txtValue = td.textContent || td.innerText;
        row.style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
      }
    });
  });
}

// Filtering tables
filterTable('myInput', 'myTable');
filterTable('myInput2', 'myTable');

// Event listener for each link
links.forEach((link) => {
  link.addEventListener("click", function (e) {
    e.preventDefault();
    sections.forEach((section) => { section.style.display = "none"; });
    defaultSection.style.display = "none";

    const target = link.getAttribute("data-target");
    const targetSection = document.getElementById(target);
    if (targetSection) { targetSection.style.display = "block"; }
    else { defaultSection.style.display = "block"; }
  });
});
