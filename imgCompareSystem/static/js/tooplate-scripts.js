const width_threshold = 480;

function drawLineChart() {

}

function drawBarChart() {

}

function drawPieChart() {

}

function updateLineChart() {
  if (lineChart) {
    lineChart.options = optionsLine;
    lineChart.update();
  }
}

function updateBarChart() {
  if (barChart) {
    barChart.options = optionsBar;
    barChart.update();
  }
}
