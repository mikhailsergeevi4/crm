var geocoder;
var map;

function initMap() {
  address = document.getElementById('address').innerHTML;
  geocoder = new google.maps.Geocoder();
  latlang = geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == 'OK') {
      latlang = results[0].geometry.location;
      var mapOptions = {
        zoom: 15,
        center: latlang
      };
      map = new google.maps.Map(document.getElementById('map'), mapOptions);
      var marker = new google.maps.Marker({
          map: map,
          position: latlang
      });
    } else {
      document.getElementById('map').innerHTML = "К сожалению, такого адреса не существует на карте";
    }
  });
}
