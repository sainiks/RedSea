// static/chart.js

function formatTime(timeString) {
  const date = new Date(timeString);
  const options = {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
  };
  return new Intl.DateTimeFormat('en-US', options).format(date);
}

async function getSentimentData(companyName) {
  const response = await fetch(`/sentiment-data?company_name=${companyName}`);
  const data = await response.json();
  return data;
}

function createSentimentChart(data) {
  const ctx = document.getElementById('sentimentChart').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(item => formatTime(item.time)), // Use the 'time' field for labels
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

async function updateChart(chart, companyName) {
  const newData = await getSentimentData(companyName);
  chart.data.labels = newData.map(item => formatTime(item.time)); // Update labels with the 'time' field
  chart.data.datasets.forEach((dataset, index) => {
    if (index === 0) dataset.data = newData.map(item => item.positive);
    if (index === 1) dataset.data = newData.map(item => item.negative);
    if (index === 2) dataset.data = newData.map(item => item.neutral);
  });
  chart.update();
}

async function initializeChart() {
    const companyName = document.currentScript.dataset.companyName;
    if (!companyName) return;
  const initialData = await getSentimentData(companyName);
  const chart = createSentimentChart(initialData);
  setInterval(() => updateChart(chart, companyName), 3000); // Update every 3 seconds
}

initializeChart();