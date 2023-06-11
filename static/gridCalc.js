

function calculaGridParametros(latInfAOI, latMedAOI, latSupAOI, lonInfAOI, lonSupAOI, tamCel){ // adaptação de CalculaQtdeCel2
    //# distX e distY  - distâncias a partir da origem refGrid
    var distX = 1000*(getDistanceFromLatLng(parseFloat(latMedAOI),parseFloat(lonInfAOI),parseFloat(latMedAOI),parseFloat(lonSupAOI)));
    var distY = 1000*(getDistanceFromLatLng(parseFloat(latInfAOI),parseFloat(lonInfAOI),parseFloat(latSupAOI),parseFloat(lonInfAOI)));
    
    var qtdeCel_X = parseInt((distX / parseInt(tamCel)) + 1);
    var qtdeCel_Y = parseInt((distY / parseInt(tamCel)) + 1);
    console.log ("distX = ",distX, " qtdeCelX = ", qtdeCel_X, " qtdeCelY = ", qtdeCel_Y);
    var difLatAOI  = parseFloat(latSupAOI) - parseFloat(latInfAOI);
    var difLongAOI = parseFloat(lonSupAOI) - parseFloat(lonInfAOI);

    var alturaCel  = difLatAOI / qtdeCel_Y; 
    var larguraCel = difLongAOI / qtdeCel_X; 
    console.log("larguraCel = ", larguraCel, " alturaCel = ", alturaCel);

    return [qtdeCel_X, qtdeCel_Y, larguraCel, alturaCel]
}

function GridNavio2(latNavio,lonNavio){ // Identificacao posicao do navio no Grid - gridNavio

    var distLat = parseFloat(latNavio) - parseFloat(latInfAOI);
    var distLon = parseFloat(lonNavio) - parseFloat(lonInfAOI);
    var posXGridNavio = (distLon / larguraCelula) + 1;
    var posYGridNavio = (distLat / alturaCelula) + 1;
    var gridNavio = posXGridNavio + (posYGridNavio - 1) * qtdeCelulasX;
    return gridNavio, posXGridNavio, posYGridNavio;
}

function calcVerticesCell(latNavio,lonNavio, latInfAOI, lonInfAOI, larguraCelula, alturaCelula){

    //[Grid, k, j] = GridNavio2(latNavio,lonNavio); // k: cell axis X    J: cell axis Y
    var distLat = parseFloat(latNavio) - parseFloat(latInfAOI);
    var distLon = parseFloat(lonNavio) - parseFloat(lonInfAOI);
    var k = parseInt(distLon / larguraCelula);//= posXGridNavio /// + 1 ?;
    var j = parseInt(distLat / alturaCelula);// = posYGridNavio // + 1 ?;
    //var gridNavio = posXGridNavio + (posYGridNavio - 1) * qtdeCelulasX;
    //console.log("larguraCel = ", larguraCelula, " alturaCel = ", alturaCelula);
    //console.log("k = ", k, " j = ", j);
    
    vertA_Cel = [parseFloat(latInfAOI + j * alturaCelula)      ,parseFloat(lonInfAOI + k * larguraCelula)];
    vertB_Cel = [parseFloat(latInfAOI + (j + 1) * alturaCelula),parseFloat(lonInfAOI + k * larguraCelula)];
    vertC_Cel = [parseFloat(latInfAOI + (j + 1) * alturaCelula),parseFloat(lonInfAOI + (k + 1)* larguraCelula)];
    vertD_Cel = [parseFloat(latInfAOI + j * alturaCelula)      ,parseFloat(lonInfAOI + (k + 1)* larguraCelula)];
    return vertices  = [vertA_Cel, vertB_Cel, vertC_Cel, vertD_Cel];

}