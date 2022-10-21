

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