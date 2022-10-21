/* Distance between two lat/lng coordinates in km using the Haversine formula */
function getDistanceFromLatLng(lat1, lng1, lat2, lng2, miles) { // miles optional
  if (typeof miles === "undefined"){miles=false;}
  function deg2rad(deg){return deg * (Math.PI/180);}
  function square(x){return Math.pow(x, 2);}
  var r=6371; // radius of the earth in km
  lat1=deg2rad(lat1);
  lat2=deg2rad(lat2);
  var lat_dif=lat2-lat1;
  var lng_dif=deg2rad(lng2-lng1);
  var a=square(Math.sin(lat_dif/2))+Math.cos(lat1)*Math.cos(lat2)*square(Math.sin(lng_dif/2));
  var d=2*r*Math.asin(Math.sqrt(a));
  if (miles){return d * 0.621371;} //return miles
  else{return d;} //return km
}
/* Copyright 2016, Chris Youderian, SimpleMaps, http://simplemaps.com/resources/location-distance
 Released under MIT license - https://opensource.org/licenses/MIT */ 