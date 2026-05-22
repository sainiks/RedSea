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
    const response = await fetch(`/sentiment-data?company_name=${encodeURIComponent(companyName)}`);
    const data = await response.json();
    return data;
}
  
function createSentimentChart(data) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    // Create modern glowing color gradients for area fills under lines
    const positiveGradient = ctx.createLinearGradient(0, 0, 0, 300);
    positiveGradient.addColorStop(0, 'rgba(16, 185, 129, 0.18)');
    positiveGradient.addColorStop(1, 'rgba(16, 185, 129, 0.00)');

    const negativeGradient = ctx.createLinearGradient(0, 0, 0, 300);
    negativeGradient.addColorStop(0, 'rgba(239, 68, 68, 0.18)');
    negativeGradient.addColorStop(1, 'rgba(239, 68, 68, 0.00)');

    const neutralGradient = ctx.createLinearGradient(0, 0, 0, 300);
    neutralGradient.addColorStop(0, 'rgba(245, 158, 11, 0.15)');
    neutralGradient.addColorStop(1, 'rgba(245, 158, 11, 0.00)');

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(item => formatTime(item.time)),
        datasets: [
          {
            label: 'Bullish',
            data: data.map(item => item.positive),
            borderColor: 'rgb(16, 185, 129)',
            backgroundColor: positiveGradient,
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(16, 185, 129)',
            pointBorderColor: 'rgba(255, 255, 255, 0.8)',
            pointRadius: 2,
            pointHoverRadius: 6
          },
          {
            label: 'Bearish',
            data: data.map(item => item.negative),
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: negativeGradient,
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(239, 68, 68)',
            pointBorderColor: 'rgba(255, 255, 255, 0.8)',
            pointRadius: 2,
            pointHoverRadius: 6
          },
          {
            label: 'Neutral',
            data: data.map(item => item.neutral),
            borderColor: 'rgb(245, 158, 11)',
            backgroundColor: neutralGradient,
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(245, 158, 11)',
            pointBorderColor: 'rgba(255, 255, 255, 0.8)',
            pointRadius: 2,
            pointHoverRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(255, 255, 255, 0.04)',
              drawBorder: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.55)',
              font: {
                family: 'Plus Jakarta Sans',
                size: 11
              }
            },
            title: {
              display: true,
              text: 'Discussion Volumetrics',
              color: 'rgba(255, 255, 255, 0.65)',
              font: {
                family: 'Outfit',
                size: 12,
                weight: '600'
              }
            }
          },
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.04)',
              drawBorder: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.55)',
              font: {
                family: 'Plus Jakarta Sans',
                size: 11
              }
            },
            title: {
              display: true,
              text: 'Scanned Interval',
              color: 'rgba(255, 255, 255, 0.65)',
              font: {
                family: 'Outfit',
                size: 12,
                weight: '600'
              }
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: 'rgba(255, 255, 255, 0.8)',
              font: {
                family: 'Outfit',
                size: 12,
                weight: '600'
              },
              usePointStyle: true,
              boxWidth: 8,
              padding: 15
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(10, 10, 15, 0.9)',
            titleColor: 'rgb(255, 255, 255)',
            titleFont: {
              family: 'Outfit',
              weight: '700',
              size: 13
            },
            bodyColor: 'rgba(255, 255, 255, 0.8)',
            bodyFont: {
              family: 'Plus Jakarta Sans',
              size: 12
            },
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 10,
            caretSize: 6,
            boxWidth: 8,
            boxHeight: 8,
            boxPadding: 4,
            usePointStyle: true
          },
        },
      }
    });
    return chart;
}
  
async function updateChart(chart, companyName) {
    const newData = await getSentimentData(companyName);
    if (!newData || !newData.length) return;
    
    chart.data.labels = newData.map(item => formatTime(item.time));
    chart.data.datasets.forEach((dataset, index) => {
      if (index === 0) dataset.data = newData.map(item => item.positive);
      if (index === 1) dataset.data = newData.map(item => item.negative);
      if (index === 2) dataset.data = newData.map(item => item.neutral);
    });
    chart.update();
}
  
/**
 * Initialize the chart for companyName and update it every 10s
 * Only update if the page is visible (not in background tab)
 */
async function initializeChart() {
    const scriptTag = document.querySelector('script[src*="chart.js"]');
    if (!scriptTag) return;
    
    const companyName = scriptTag.dataset.companyName;
    if (!companyName) return;
    
    const preloaded = Array.isArray(window.initialSentimentData) ? window.initialSentimentData : [];
    const initialData = preloaded.length ? preloaded : await getSentimentData(companyName);
    
    if (!initialData || !initialData.length) return;

    const chart = createSentimentChart(initialData);
    if (preloaded.length) {
      updateChart(chart, companyName);
    }
    
    setInterval(() => {
      if (!document.hidden) updateChart(chart, companyName);
    }, 10000); // Poll every 10 seconds
}
  
initializeChart();
