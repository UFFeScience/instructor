var data = [{
    r: [1,0,0,0,0,0,0,0],
    theta: ["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"],
    name: "< 2 knots",
    marker: {color: "black"},
    type: "barpolar"
  
}]

var layout = {
    showlegend: false,
    //title: "Vessels Speed",
    font: {size: 2},
    
    polar: {
        barmode: "stack",//"group", //"stack",//"overlay",
        bargap: -1,
        radialaxis: {angle: 45, dtick: 1}, //{ticksuffix: "%", angle: 45, dtick: 200},
        angularaxis: {direction: "clockwise"}
    }
}
var config = {
    responsive: true,
    staticPlot: true
}

function exibeWindRoseAISPoint(){
    Plotly.newPlot("windRoseSpeedCourseAISPoint", data, layout, config)
}

