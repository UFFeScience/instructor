var r1_Array = [];
var theta_Array = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

var data = [{
//    r: r1_Array,
//    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
//    name: "% Points",
//    marker: {color: "black"},
//    type: "barpolar"
//    }, {
    r: [0, 0, 0, 0, 0, 0, 0, 0],
    theta: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    name: "< 3 knots",
    marker: {color: "grey"},
    type: "barpolar"
    }, {
    r: [0, 0, 0, 0, 0, 0, 0, 0],
    theta: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    name: "3-7 knots",
    marker: {color: "blue"},
    type: "barpolar"
    }, {
    r: [0, 0, 0, 0, 0, 0, 0, 0],
    theta: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    name: "7-11 knots",
    marker: {color: "green"},
    type: "barpolar"
    }, {
    r: [0, 0, 0, 0, 0, 0, 0, 0],
    theta: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    name: "11-15 knots",
    marker: {color: "yellow"},
    type: "barpolar"
    }, {
    r: [0, 0, 0, 0, 0, 0, 0, 0],
    theta: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    name: "15-20 knots",
    marker: {color: "orange"},
    type: "barpolar"
    }, {
    r: [0, 0, 0, 0, 0, 0, 0, 0],
    theta: ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    name: "20+ knots",
    marker: {color: "red"},
    type: "barpolar"
}]

var layout = {
    showlegend: false,
    title: "Historical",
    font: {size: 12},
    //legend: {
        
    //    font: {size: 16}
    //},
    polar: {
        barmode: "stack",//"group", //"stack",//"overlay",
        bargap: -1,
        //radialaxis: {ticksuffix: "%", angle: 45, dtick: 200},
        radialaxis: {angle: 45, dtick: 10},
        angularaxis: {direction: "clockwise"}
    }
}
var config = {
    responsive: true,
    staticPlot: true
}

function exibeWindRose(s3, s7, s11, s15, s20, s99){
    //data[0].r = [600, 400, 30, 30, 26, 40, 30, 20];
                //data[0].theta = theta_Array;
                // data[1].theta = theta_Array;
    
    //data[5].r = data20Plus;
    //data[6].r = [30, 20, 15, 15, 13, 20, 15, 10];
    data[0].r = s3;
    data[1].r = s7;
    data[2].r = s11;
    data[3].r = s15;
    data[4].r = s20;
    data[5].r = s99;
    //console.log ("windRose arrays - dentro do js = \n", s3, "\n", s7, "\n", s11, "\n", s15, "\n", s20, "\n",s99);

    Plotly.newPlot("vesselsSpeed", data, layout, config)
}

// used to show a blank WindRose in the page - first show
function exibe_Blank_WindRose(){
    var s3  = [0, 0, 0, 0, 0, 0, 0, 0];
    var s7  = [0, 0, 0, 0, 0, 0, 0, 0];
    var s11 = [0, 0, 0, 0, 0, 0, 0, 0];
    var s15 = [0, 0, 0, 0, 0, 0, 0, 0];
    var s20 = [0, 0, 0, 0, 0, 0, 0, 0];
    var s99 = [0, 0, 0, 0, 0, 0, 0, 0];
    
    data[0].r = s3;
    data[1].r = s7;
    data[2].r = s11;
    data[3].r = s15;
    data[4].r = s20;
    data[5].r = s99;
    
    Plotly.newPlot("vesselsSpeed", data, layout, config)
}
//////////////////
/*
function exibeWindRose_on_MAP(s3, s7, s11, s15, s20, s99){
    
    data[0].r = s3;
    data[1].r = s7;
    data[2].r = s11;
    data[3].r = s15;
    data[4].r = s20;
    data[5].r = s99;
    //console.log ("windRose arrays - dentro do js = \n", s3, "\n", s7, "\n", s11, "\n", s15, "\n", s20, "\n",s99);

    Plotly.newPlot("vesselsSpeed_on_MAP", data, layout, config)
}

//////////
function exibe_Blank_WindRose_on_MAP(){
    var s3  = [0, 0, 0, 0, 0, 0, 0, 0];
    var s7  = [0, 0, 0, 0, 0, 0, 0, 0];
    var s11 = [0, 0, 0, 0, 0, 0, 0, 0];
    var s15 = [0, 0, 0, 0, 0, 0, 0, 0];
    var s20 = [0, 0, 0, 0, 0, 0, 0, 0];
    var s99 = [0, 0, 0, 0, 0, 0, 0, 0];
    
    data[0].r = s3;
    data[1].r = s7;
    data[2].r = s11;
    data[3].r = s15;
    data[4].r = s20;
    data[5].r = s99;
    
    Plotly.newPlot("vesselsSpeed_on_MAP", data, layout, config)
}
*/