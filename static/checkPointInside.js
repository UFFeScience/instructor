    // Callbacks
    function onMapClick(e) {
    var contained = polygon.contains(e.latlng);
    var message = contained ? "This is inside the polygon!" : "This is not inside the polygon.";
    popup
        .setLatLng(e.latlng)
        .setContent(message)
        .openOn(mymap);
    }

    function onMarkerClick(e) {
    var contained = polygon.contains(e.latlng);
    var message = contained ? "This marker is inside the polygon!" : "This marker is not inside the polygon.";
    popup
        .setLatLng(e.latlng)
        .setContent(message)
        .openOn(mymap);
    }
    // Setup
    var mymap = L.map('mapid').setView([51.505, -0.09], 13);
    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiY29uZG9ydGhlZ3JlYXQiLCJhIjoiY2l6MXYwaDQyMDRneDMzcWZ4djRibWdiYiJ9.rbvqKXa9H0axkE3EAPSzgQ', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'mapid',
    accessToken: 'pk.eyJ1IjoiY29uZG9ydGhlZ3JlYXQiLCJhIjoiY2l6MXYwaDQyMDRneDMzcWZ4djRibWdiYiJ9.rbvqKXa9H0axkE3EAPSzgQ'
    }).addTo(mymap);
    var polygon = L.polygon([
    [51.51, -0.08],
    [51.503, -0.06],
    [51.51, -0.047]
    ]).addTo(mymap);
    var popup = L.popup();
    mymap.on('click', onMapClick);
    var m1 = L.marker([51.515, -0.07]).addTo(mymap).on('click', onMarkerClick);
    var m2 = L.marker([51.506, -0.06]).addTo(mymap).on('click', onMarkerClick);
    var m3 = L.marker([51.505, -0.074]).addTo(mymap).on('click', onMarkerClick);
    var m4 = L.marker([51.51, -0.067]).addTo(mymap).on('click', onMarkerClick);
    console.log(polygon.contains(m1.getLatLng()));
    // ==> false
    console.log(polygon.contains(m2.getLatLng()));
    // ==> true
    console.log(polygon.contains(m3.getLatLng()));
    // ==> false
    console.log(polygon.contains(m4.getLatLng()));
    // ==> true