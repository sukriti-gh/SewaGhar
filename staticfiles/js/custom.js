

//client section owl carousel
$(".owl-carousel").owlCarousel({
    loop: true,
    margin: 10,
    nav: true,
    dots: false,
    navText: [
        '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
        '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
    ],
    autoplay: true,
    autoplayHoverPause: true,
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1000: {
            items: 2
        }
    }
});


function myMap() {
    var mapProp = {
        center: new google.maps.LatLng(27.6895, 85.3268), // Coordinates for Herald College
        zoom: 15,
    };

    var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);

    var heraldCollegeCoords = new google.maps.LatLng(27.6895, 85.3268);

    var marker = new google.maps.Marker({
        position: heraldCollegeCoords,
        map: map,
        title: "Herald College Kathmandu"
    });

    // Create an info window for Herald College with an iframe
    var infoContent = '<div style="max-width: 300px;"><iframe width="100%" height="200" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3531.005047114716!2d85.3246113150769!3d27.689553982792836!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39eb19e1e8b9b147%3A0x1831a669ffab0f3a!2sHerald%20College!5e0!3m2!1sen!2snp!4v1648575613771!5m2!1sen!2snp" frameborder="0" allowfullscreen></iframe></div>';
    
    var infoWindow = new google.maps.InfoWindow({
        content: infoContent
    });

    // Open the info window when the marker is clicked
    marker.addListener("click", function() {
        infoWindow.open(map, marker);
    });
}


