function findMinMax(pontos) {
            
    var len = pontos.length; 
    
    var somaLat = 0;
    var medLat = 0;
    var minValueLat = parseFloat(pontos[0][0]);
    var maxValueLat = parseFloat(pontos[0][0]);
    var minValueLon = parseFloat(pontos[0][1]);
    var maxValueLon = parseFloat(pontos[0][1]);

    for (var i = 0; i < len; i++) {
        // find minimum value
        if (parseFloat(pontos[i][0]) < minValueLat){
            minValueLat = parseFloat(pontos[i][0]);
        };
        // find maximum value
        if (parseFloat(pontos[i][0]) > maxValueLat){
            maxValueLat = parseFloat(pontos[i][0]);
        };
        if (parseFloat(pontos[i][1]) < minValueLon){
            minValueLon = parseFloat(pontos[i][1]);
        };
        // find maximum value
        if (parseFloat(pontos[i][1]) > maxValueLon){
            maxValueLon = parseFloat(pontos[i][1]);
        };
        somaLat = somaLat + parseFloat(pontos[i][0]);
        //console.log("parcial ", i, " ", minValueLat,maxValueLat, minValueLon, maxValueLon, somaLat);
    };
    medLat = (somaLat / len).toFixed(5);
    return [minValueLat,maxValueLat, minValueLon, maxValueLon, medLat];
}