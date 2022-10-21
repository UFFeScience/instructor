/**
 * Verify if point of coordinates (longitude, latitude) is polygon of coordinates
 * https://github.com/substack/point-in-polygon/blob/master/index.js
 * @param {number} latitude Latitude
 * @param {number} longitude Longitude
 * @param {array<[number,number]>} polygon Polygon contains arrays of points. One array have the following format: [latitude,longitude]
 */
function isPointInPolygon (latitude, longitude, polygon) {
 // if (typeof latitude !== 'number' || typeof longitude !== 'number') {
 //   throw new TypeError('Invalid latitude or longitude. Numbers are expected')
 // } else 
//  if (!polygon || !Array.isArray(polygon)) {
//    throw new TypeError('Invalid polygon. Array with locations expected')
//  } else if (polygon.length === 0) {
//    throw new TypeError('Invalid polygon. Non-empty Array expected')
//  }

  const x = parseFloat(latitude); const y = parseFloat(longitude);

  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = parseFloat(polygon[i][0]); const yi = parseFloat(polygon[i][1]);
    const xj = parseFloat(polygon[j][0]); const yj = parseFloat(polygon[j][1]);

    const intersect = ((yi > y) !== (yj > y)) &&
            (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside
  }

  return inside
};