var data = [{
    r: [2.5, 72.5, 70.0, 45.0, 22.5, 42.5, 40.0, 62.5],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "< 2 knots",
    marker: {color: "black"},
    type: "barpolar"
    }, {
    r: [7.5, 50.0, 45.0, 35.0, 20.0, 22.5, 37.5, 55.0],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "2-5 knots",
    marker: {color: "rgb(158,154,200)"},
    type: "barpolar"
    }, {
    r: [13.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "5-9 knots",
    marker: {color: "blue"},
    type: "barpolar"
    }, {
    r: [19.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "9-12 knots",
    marker: {color: "green"},
    type: "barpolar"
    }, {
    r: [27.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "12-15 knots",
    marker: {color: "yellow"},
    type: "barpolar"
    }, {
    r: [30.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "20+ knots",
    marker: {color: "red"},
    type: "barpolar"
}]

var layout = {
    showlegend: false,
    title: "Vessels Speed",
    font: {size: 14},
    //legend: {
        
    //    font: {size: 16}
    //},
    polar: {
        barmode: "stack",//"group", //"stack",//"overlay",
        bargap: -1,
        radialaxis: {ticksuffix: "%", angle: 45, dtick: 200},
        angularaxis: {direction: "clockwise"}
    }
}
var config = {
    responsive: true,
    staticPlot: true
}

function exibeWindRose(){
    Plotly.newPlot("vesselsSpeed", data, layout, config)
}

