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
    
    // Create ultra-clean, soft Apple pastel gradients for area fills under lines
    const positiveGradient = ctx.createLinearGradient(0, 0, 0, 300);
    positiveGradient.addColorStop(0, 'rgba(52, 199, 89, 0.08)');
    positiveGradient.addColorStop(1, 'rgba(52, 199, 89, 0.00)');

    const negativeGradient = ctx.createLinearGradient(0, 0, 0, 300);
    negativeGradient.addColorStop(0, 'rgba(255, 59, 48, 0.08)');
    negativeGradient.addColorStop(1, 'rgba(255, 59, 48, 0.00)');

    const neutralGradient = ctx.createLinearGradient(0, 0, 0, 300);
    neutralGradient.addColorStop(0, 'rgba(255, 204, 0, 0.08)');
    neutralGradient.addColorStop(1, 'rgba(255, 204, 0, 0.00)');

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(item => formatTime(item.time)),
        datasets: [
          {
            label: 'Bullish',
            data: data.map(item => item.positive),
            borderColor: 'rgb(52, 199, 89)', // Mint Green
            backgroundColor: positiveGradient,
            borderWidth: 2.5,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(52, 199, 89)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 1.5,
            pointRadius: 2,
            pointHoverRadius: 6
          },
          {
            label: 'Bearish',
            data: data.map(item => item.negative),
            borderColor: 'rgb(255, 59, 48)', // System Red
            backgroundColor: negativeGradient,
            borderWidth: 2.5,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(255, 59, 48)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 1.5,
            pointRadius: 2,
            pointHoverRadius: 6
          },
          {
            label: 'Neutral',
            data: data.map(item => item.neutral),
            borderColor: 'rgb(255, 204, 0)', // System Gold
            backgroundColor: neutralGradient,
            borderWidth: 2.5,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(255, 204, 0)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 1.5,
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
              color: 'rgba(0, 0, 0, 0.035)',
              drawBorder: false
            },
            ticks: {
              color: 'rgba(28, 28, 30, 0.55)',
              font: {
                family: 'Plus Jakarta Sans',
                size: 11,
                weight: '500'
              }
            },
            title: {
              display: true,
              text: 'Discussion Volumetrics',
              color: 'rgba(28, 28, 30, 0.65)',
              font: {
                family: 'Outfit',
                size: 12,
                weight: '600'
              }
            }
          },
          x: {
            grid: {
              color: 'rgba(0, 0, 0, 0.035)',
              drawBorder: false
            },
            ticks: {
              color: 'rgba(28, 28, 30, 0.55)',
              font: {
                family: 'Plus Jakarta Sans',
                size: 11,
                weight: '500'
              }
            },
            title: {
              display: true,
              text: 'Scanned Interval',
              color: 'rgba(28, 28, 30, 0.65)',
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
              color: 'rgba(28, 28, 30, 0.8)',
              font: {
                family: 'Outfit',
                size: 11,
                weight: '600'
              },
              usePointStyle: true,
              boxWidth: 6,
              padding: 15
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: 'rgb(28, 28, 30)',
            titleFont: {
              family: 'Outfit',
              weight: '700',
              size: 13
            },
            bodyColor: 'rgba(28, 28, 30, 0.8)',
            bodyFont: {
              family: 'Plus Jakarta Sans',
              size: 12
            },
            borderColor: 'rgba(0, 0, 0, 0.08)',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 12,
            caretSize: 6,
            boxWidth: 8,
            boxHeight: 8,
            boxPadding: 4,
            usePointStyle: true,
            shadowColor: 'rgba(0, 0, 0, 0.1)',
            shadowBlur: 10
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
