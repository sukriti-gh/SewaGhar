document.addEventListener('DOMContentLoaded', function () {
    // JavaScript to hide the preloader with a delay after the DOM is fully loaded
    var preloader = document.querySelector('.preloader');

    // Add a delay of 2000 milliseconds (2 seconds) before hiding the preloader
    setTimeout(function() {
        preloader.style.display = 'none';
        document.body.style.overflow = 'auto'; // Show the scrollbar after the page is fully loaded
    }, 1500);
});
