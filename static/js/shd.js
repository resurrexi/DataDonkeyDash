$(document).ready(function(){
	$.get('static/data/dsihealth_summary.csv', function(csv){
		$('#chart1').highcharts({
			chart: {
				zoomType: 'x',
				showAxes: true
			},
			data: {
				csv: csv
			},
			title: {
				text: 'Sandbox Usage Over Time'
			},
			legend: {
				enabled: true
			},
			credits: {
				enabled: false
			},
			yAxis: {
				title: {
					text: 'GB'
				}
			},
			plotOptions: {
				line: {
					dataLabels: {
						enabled: false
					},
				}
			}
		});
	});
	$.get('static/data/dsihealth_day.csv', function(csv){
		$('#chart2').highcharts({
			chart: {
				type: 'bar',
				showAxes: true
			},
			data: {
				csv: csv
			},
			title: {
				text: "Top 10 Hogs"
			},
			legend: {
				enabled: false
			},
			credits: {
				enabled: false
			},
			yAxis: {
				title: {
					text: 'GB'
				}
			}
		});
	});
	$.get('static/data/dsihealth_top10.csv', function(csv){
		$('#chart3').highcharts({
			chart: {
				type: 'bar',
				showAxes: true
			},
			data: {
				csv: csv
			},
			title: {
				text: "Top 10 Datasets"
			},
			legend: {
				enabled: false
			},
			credits: {
				enabled: false
			},
			yAxis: {
				title: {
					text: 'GB'
				}
			}
		});
	});
});