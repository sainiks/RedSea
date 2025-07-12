// static/chart.js

async function getSentimentData() {
  const response = await fetch('/sentiment-data');
  const data = await response.json();
  return data;
}

function createSentimentChart(data) {
  const ctx = document.getElementById('sentimentChart').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(item => item.time), // Use the 'time' field for labels
      datasets: [
        {
          label: 'Positive',
          data: data.map(item => item.positive),
          borderColor: 'rgba(54, 162, 235, 1)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderWidth: 1
        },
        {
          label: 'Negative',
          data: data.map(item => item.negative),
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderWidth: 1
        },
        {
          label: 'Neutral',
          data: data.map(item => item.neutral),
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Sentiment Score'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        }
      },
      plugins: {
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
    }
  });
  return chart;
}

async function updateChart(chart) {
  const newData = await getSentimentData();
  chart.data.labels = newData.map(item => item.time); // Update labels with the 'time' field
  chart.data.datasets.forEach((dataset, index) => {
    if (index === 0) dataset.data = newData.map(item => item.positive);
    if (index === 1) dataset.data = newData.map(item => item.negative);
    if (index === 2) dataset.data = newData.map(item => item.neutral);
  });
  chart.update();
}

async function initializeChart() {
  const initialData = await getSentimentData();
  const chart = createSentimentChart(initialData);
  setInterval(() => updateChart(chart), 3000); // Update every 3 seconds
}

initializeChart();