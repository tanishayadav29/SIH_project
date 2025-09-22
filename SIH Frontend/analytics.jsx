/*
Analytics Dashboard for Jharkhand Tourism Officials
- Exposes initAnalyticsDashboard(container, dataFetcher)
- container: HTMLElement or selector string where the dashboard mounts
- dataFetcher: async function returning { kpis, topLocations, topPlaces, trends }
  Shapes:
    kpis: { totalVisitors: number, avgStay: number, revenue: number, occupancy: number }
    topLocations: Array<{ name: string, visitors: number }>
    topPlaces: Array<{ name: string, visitors: number }>
    trends: Array<{ date: string, visitors: number }>
*/

(function (global) {
  const ensureChartJs = async () => {
    if (global.Chart) return;
    await new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };

  const createElement = (html) => {
    const template = document.createElement('template');
    template.innerHTML = html.trim();
    return template.content.firstChild;
  };

  function formatNumber(n) {
    return n.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }

  function formatCurrency(n) {
    return n.toLocaleString(undefined, { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });
  }

  function renderSkeleton(root) {
    root.innerHTML = '';
    const layout = createElement(`
      <div style="font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 16px; color: #0f172a;">
        <h2 style="margin: 0 0 16px; font-weight: 700;">Jharkhand Tourism Analytics</h2>
        <div id="kpi-row" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;"></div>
        <div style="display: grid; grid-template-columns: 1.5fr 1.5fr 1fr; gap: 12px;">
          <div id="chart-top-locations" style="background:#fff; border:1px solid #e2e8f0; border-radius: 8px; padding: 12px;"></div>
          <div id="chart-top-places" style="background:#fff; border:1px solid #e2e8f0; border-radius: 8px; padding: 12px;"></div>
          <div id="chart-trends" style="background:#fff; border:1px solid #e2e8f0; border-radius: 8px; padding: 12px;"></div>
        </div>
      </div>
    `);
    root.appendChild(layout);

    const kpiRow = layout.querySelector('#kpi-row');
    const kpiCard = (label, value, sub) => createElement(`
      <div style="background:#fff; border:1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
        <div style="font-size:12px; color:#64748b;">${label}</div>
        <div style="font-size:22px; font-weight:700;">${value}</div>
        ${sub ? `<div style=\"font-size:12px; color:#64748b; margin-top:4px;\">${sub}</div>` : ''}
      </div>
    `);
    kpiRow.appendChild(kpiCard('Total Visitors', '—'));
    kpiRow.appendChild(kpiCard('Avg Stay (days)', '—'));
    kpiRow.appendChild(kpiCard('Revenue', '—'));
    kpiRow.appendChild(kpiCard('Occupancy %', '—'));

    const addChartCard = (title, canvasId) => {
      const el = createElement(`
        <div>
          <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="margin:0; font-size:14px; color:#334155;">${title}</h3>
          </div>
          <canvas id="${canvasId}" height="200"></canvas>
        </div>
      `);
      return el;
    };

    layout.querySelector('#chart-top-locations').appendChild(addChartCard('Most Visited Locations', 'canvasTopLocations'));
    layout.querySelector('#chart-top-places').appendChild(addChartCard('Most Visited Places', 'canvasTopPlaces'));
    layout.querySelector('#chart-trends').appendChild(addChartCard('Visitor Trends', 'canvasTrends'));

    return layout;
  }

  function renderKPIs(root, kpis) {
    const cards = root.querySelectorAll('#kpi-row > div');
    if (!kpis) return;
    cards[0].querySelector('div:nth-child(2)').textContent = formatNumber(kpis.totalVisitors || 0);
    cards[1].querySelector('div:nth-child(2)').textContent = (kpis.avgStay || 0).toFixed(1);
    cards[2].querySelector('div:nth-child(2)').textContent = formatCurrency(kpis.revenue || 0);
    cards[3].querySelector('div:nth-child(2)').textContent = ((kpis.occupancy || 0)).toFixed(1) + '%';
  }

  function buildBarChart(ctx, labels, data, label, color) {
    return new global.Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label,
          data,
          backgroundColor: color,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  function buildLineChart(ctx, labels, data, label, color) {
    return new global.Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label,
          data,
          borderColor: color,
          backgroundColor: color + '33',
          fill: true,
          tension: 0.35,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  async function initAnalyticsDashboard(container, dataFetcher) {
    await ensureChartJs();

    const root = typeof container === 'string' ? document.querySelector(container) : container;
    if (!root) throw new Error('Analytics container not found');

    const layout = renderSkeleton(root);

    // Fetch data
    let data;
    try {
      data = await dataFetcher();
    } catch (e) {
      console.error('Analytics data fetch failed:', e);
      data = {
        kpis: { totalVisitors: 0, avgStay: 0, revenue: 0, occupancy: 0 },
        topLocations: [],
        topPlaces: [],
        trends: [],
      };
    }

    // KPIs
    renderKPIs(layout, data.kpis);

    // Top Locations
    const locLabels = (data.topLocations || []).map((d) => d.name);
    const locValues = (data.topLocations || []).map((d) => d.visitors);
    const ctxLoc = layout.querySelector('#canvasTopLocations').getContext('2d');
    buildBarChart(ctxLoc, locLabels, locValues, 'Visitors', '#0ea5e9');

    // Top Places
    const placeLabels = (data.topPlaces || []).map((d) => d.name);
    const placeValues = (data.topPlaces || []).map((d) => d.visitors);
    const ctxPlace = layout.querySelector('#canvasTopPlaces').getContext('2d');
    buildBarChart(ctxPlace, placeLabels, placeValues, 'Visitors', '#22c55e');

    // Trends
    const trendLabels = (data.trends || []).map((d) => d.date);
    const trendValues = (data.trends || []).map((d) => d.visitors);
    const ctxTrend = layout.querySelector('#canvasTrends').getContext('2d');
    buildLineChart(ctxTrend, trendLabels, trendValues, 'Visitors', '#8b5cf6');

    return {
      root,
      update: async () => {
        const fresh = await dataFetcher();
        renderKPIs(layout, fresh.kpis);
        // For brevity, charts are not dynamically updated here; reinit as needed
      },
    };
  }

  // UMD-style export
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initAnalyticsDashboard };
  } else {
    global.initAnalyticsDashboard = initAnalyticsDashboard;
  }
})(typeof window !== 'undefined' ? window : globalThis);
