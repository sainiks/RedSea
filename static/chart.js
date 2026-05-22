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

function getOrCreateTooltip(chart) {
  let tooltipEl = document.getElementById('chartjs-tooltip');

  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.id = 'chartjs-tooltip';
    tooltipEl.innerHTML = `
      <div class="tooltip-title"></div>
      <div class="tooltip-body"></div>
    `;
    chart.canvas.parentNode.appendChild(tooltipEl);
  }

  return tooltipEl;
}

function externalTooltipHandler(context) {
  // Tooltip Element
  const {chart, tooltip} = context;
  const tooltipEl = getOrCreateTooltip(chart);

  // Hide if no tooltip
  if (tooltip.opacity === 0) {
    tooltipEl.style.opacity = '0';
    return;
  }

  // Set Text
  if (tooltip.body) {
    const titleLines = tooltip.title || [];
    const titleEl = tooltipEl.querySelector('.tooltip-title');
    titleEl.innerHTML = titleLines.join('<br>');

    const bodyEl = tooltipEl.querySelector('.tooltip-body');
    bodyEl.innerHTML = '';

    tooltip.dataPoints.forEach((dataPoint) => {
      const itemEl = document.createElement('div');
      itemEl.className = 'tooltip-item';

      const labelEl = document.createElement('span');
      labelEl.className = 'tooltip-item-label';
      
      const dotEl = document.createElement('span');
      dotEl.className = 'legend-dot';
      dotEl.style.backgroundColor = dataPoint.dataset.borderColor;
      
      labelEl.appendChild(dotEl);
      
      const labelText = document.createTextNode(` ${dataPoint.dataset.label}`);
      labelEl.appendChild(labelText);

      const valEl = document.createElement('span');
      valEl.className = 'tooltip-item-value';
      valEl.style.color = dataPoint.dataset.borderColor;
      valEl.innerText = parseFloat(dataPoint.raw).toFixed(2);

      itemEl.appendChild(labelEl);
      itemEl.appendChild(valEl);
      bodyEl.appendChild(itemEl);
    });
  }

  const {offsetLeft: positionX, offsetTop: positionY} = chart.canvas;

  // Display, position, and set styles for font
  tooltipEl.style.opacity = '1';
  tooltipEl.style.left = positionX + tooltip.caretX + 'px';
  tooltipEl.style.top = positionY + tooltip.caretY - tooltip.height - 15 + 'px';
}

function createCustomLegend(chart) {
  const container = chart.canvas.parentNode;
  
  // Remove existing legend if any
  const existingLegend = container.querySelector('.custom-legend');
  if (existingLegend) {
    existingLegend.remove();
  }

  const legendWrapper = document.createElement('div');
  legendWrapper.className = 'custom-legend';

  const datasets = chart.data.datasets;
  datasets.forEach((dataset, index) => {
    const pill = document.createElement('button');
    pill.type = 'button';
    
    // Add custom classes matching sentiment colors
    let labelLower = dataset.label.toLowerCase();
    pill.className = `legend-pill ${labelLower.substring(0, 3)}`;
    
    const dot = document.createElement('span');
    dot.className = 'legend-dot';
    
    const text = document.createElement('span');
    text.innerText = dataset.label;

    pill.appendChild(dot);
    pill.appendChild(text);

    pill.addEventListener('click', () => {
      const isVisible = chart.isDatasetVisible(index);
      if (isVisible) {
        chart.hide(index);
        pill.classList.add('dataset-hidden');
      } else {
        chart.show(index);
        pill.classList.remove('dataset-hidden');
      }
    });

    legendWrapper.appendChild(pill);
  });

  // Insert centered right above the chart canvas
  container.insertBefore(legendWrapper, chart.canvas);
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
            borderColor: '#2ecc71',
            backgroundColor: 'rgba(46, 204, 113, 0.04)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 8,
            pointBackgroundColor: '#2ecc71',
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#2ecc71',
            pointHoverBorderWidth: 3,
            fill: true
          },
          {
            label: 'Negative',
            data: data.map(item => item.negative),
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.04)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 8,
            pointBackgroundColor: '#e74c3c',
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#e74c3c',
            pointHoverBorderWidth: 3,
            fill: true
          },
          {
            label: 'Neutral',
            data: data.map(item => item.neutral),
            borderColor: '#f1c40f',
            backgroundColor: 'rgba(241, 196, 15, 0.04)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 8,
            pointBackgroundColor: '#f1c40f',
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#f1c40f',
            pointHoverBorderWidth: 3,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(255, 255, 255, 0.05)',
              drawBorder: false
            },
            ticks: {
              color: '#a0a0a0',
              font: {
                family: "'Inter', sans-serif"
              }
            },
            title: {
              display: true,
              text: 'Sentiment Score',
              color: '#e0e0e0',
              font: {
                family: "'Inter', sans-serif",
                weight: '600'
              }
            }
          },
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)',
              drawBorder: false
            },
            ticks: {
              color: '#a0a0a0',
              font: {
                family: "'Inter', sans-serif"
              }
            },
            title: {
              display: true,
              text: 'Time',
              color: '#e0e0e0',
              font: {
                family: "'Inter', sans-serif",
                weight: '600'
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false // Hide default legend
          },
          tooltip: {
            enabled: false, // Hide default tooltip
            external: externalTooltipHandler // Wire up custom HTML tooltip
          }
        }
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
  
  /**
   * Initialize the chart for companyName and update it every 10s
   * Only update if the page is visible (not in background tab)
   */
  async function initializeChart() {
      const companyName = document.currentScript.dataset.companyName;
      if (!companyName) return;
    // Render immediately from server-provided data, then refresh in the background.
    const preloaded = Array.isArray(window.initialSentimentData) ? window.initialSentimentData : [];
    const initialData = preloaded.length ? preloaded : await getSentimentData(companyName);
    const chart = createSentimentChart(initialData);
    
    // Create Custom Legend controls!
    createCustomLegend(chart);

    if (preloaded.length) {
      updateChart(chart, companyName);
    }
    setInterval(() => {
      if (!document.hidden) updateChart(chart, companyName);
    }, 10000); // Poll every 10 seconds
  }
  
  initializeChart();
