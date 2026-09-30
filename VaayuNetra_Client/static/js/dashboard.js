/**
 * VaayuNetra Municipal GIS Control Dashboard
 * Theme: Minimalist Soft Lavender GIS Palette
 */

// City registry and telemetry data
const CITIES = {
  'Mumbai': {
    lat: 19.0620,
    lon: 72.9150,
    zoom: 12.5,
    state: 'Maharashtra',
    country: 'India',
    aqi: 142,
    status: 'Moderate',
    statusClass: 'moderate',
    wind: 'E 2.1 m/s',
    temp: '30°C',
    humidity: '68%',
    pins: [
      { name: 'O3', pct: '38%', val: '38.11', unit: 'µg/m³', lat: 19.063, lon: 72.888, type: 'safe' },
      { name: 'NO2', pct: '28%', val: '7.04', unit: 'µg/m³', lat: 19.068, lon: 72.923, type: 'moderate' },
      { name: 'PM10', pct: '34%', val: '15.27', unit: 'µg/m³', lat: 19.049, lon: 72.903, type: 'moderate' },
      { name: 'PM2.5', pct: '74%', val: '148', unit: 'µg/m³', lat: 19.053, lon: 72.948, type: 'warning' }
    ],
    hazardCenter: [19.063, 72.916],
    hazardRadius: 1450,
    hourlyForecast: [132, 135, 142, 148, 158, 160, 156, 148, 140, 134, 130, 128, 130, 138, 150, 162, 168, 165]
  },
  'Delhi NCR': {
    lat: 28.6139,
    lon: 77.2090,
    zoom: 12,
    state: 'National Capital',
    country: 'India',
    aqi: 284,
    status: 'Poor',
    statusClass: 'warning',
    wind: 'NW 3.4 m/s',
    temp: '26°C',
    humidity: '52%',
    pins: [
      { name: 'PM2.5', pct: '88%', val: '242', unit: 'µg/m³', lat: 28.625, lon: 77.218, type: 'warning' },
      { name: 'PM10', pct: '79%', val: '190', unit: 'µg/m³', lat: 28.601, lon: 77.195, type: 'warning' },
      { name: 'NO2', pct: '44%', val: '28.4', unit: 'µg/m³', lat: 28.635, lon: 77.240, type: 'moderate' }
    ],
    hazardCenter: [28.620, 77.215],
    hazardRadius: 1800,
    hourlyForecast: [240, 248, 260, 275, 290, 284, 270, 255, 245, 240, 235, 230, 245, 265, 280, 292, 285, 278]
  },
  'Bengaluru': {
    lat: 12.9716,
    lon: 77.5946,
    zoom: 12.5,
    state: 'Karnataka',
    country: 'India',
    aqi: 68,
    status: 'Satisfactory',
    statusClass: 'safe',
    wind: 'SW 4.2 m/s',
    temp: '24°C',
    humidity: '62%',
    pins: [
      { name: 'PM2.5', pct: '28%', val: '32.4', unit: 'µg/m³', lat: 12.975, lon: 77.598, type: 'safe' },
      { name: 'PM10', pct: '32%', val: '45.1', unit: 'µg/m³', lat: 12.960, lon: 77.585, type: 'safe' }
    ],
    hazardCenter: [12.972, 77.595],
    hazardRadius: 1100,
    hourlyForecast: [55, 58, 62, 68, 72, 75, 70, 65, 62, 60, 58, 56, 58, 62, 66, 70, 68, 64]
  },
  'Patna': {
    lat: 25.5941,
    lon: 85.1376,
    zoom: 12.5,
    state: 'Bihar',
    country: 'India',
    aqi: 198,
    status: 'Moderate-High',
    statusClass: 'warning',
    wind: 'E 1.8 m/s',
    temp: '29°C',
    humidity: '72%',
    pins: [
      { name: 'PM2.5', pct: '82%', val: '178', unit: 'µg/m³', lat: 25.598, lon: 85.142, type: 'warning' },
      { name: 'PM10', pct: '65%', val: '112', unit: 'µg/m³', lat: 25.585, lon: 85.125, type: 'moderate' }
    ],
    hazardCenter: [25.596, 85.139],
    hazardRadius: 1500,
    hourlyForecast: [160, 168, 175, 185, 198, 204, 195, 185, 178, 170, 165, 160, 168, 180, 192, 205, 200, 190]
  },
  'Kolkata': { lat: 22.5726, lon: 88.3639, zoom: 12.5, state: 'West Bengal', aqi: 125, status: 'Moderate', statusClass: 'moderate', wind: 'S 3.0 m/s', temp: '31°C', humidity: '78%' },
  'Chennai': { lat: 13.0827, lon: 80.2707, zoom: 12.5, state: 'Tamil Nadu', aqi: 82, status: 'Satisfactory', statusClass: 'safe', wind: 'SE 3.8 m/s', temp: '32°C', humidity: '74%' },
  'Hyderabad': { lat: 17.3850, lon: 78.4867, zoom: 12.5, state: 'Telangana', aqi: 110, status: 'Moderate', statusClass: 'moderate', wind: 'W 2.5 m/s', temp: '28°C', humidity: '58%' },
  'Ahmedabad': { lat: 23.0225, lon: 72.5714, zoom: 12.5, state: 'Gujarat', aqi: 165, status: 'Moderate', statusClass: 'warning', wind: 'SW 2.8 m/s', temp: '33°C', humidity: '48%' },
  'Pune': { lat: 18.5204, lon: 73.8567, zoom: 12.5, state: 'Maharashtra', aqi: 95, status: 'Satisfactory', statusClass: 'safe', wind: 'W 2.2 m/s', temp: '27°C', humidity: '64%' },
  'Lucknow': { lat: 26.8467, lon: 80.9462, zoom: 12.5, state: 'Uttar Pradesh', aqi: 188, status: 'Moderate', statusClass: 'warning', wind: 'E 1.9 m/s', temp: '29°C', humidity: '66%' }
};

let currentCityKey = 'Mumbai';
let map = null;
let currentMarkers = [];
let currentOverlays = [];
let forecastChart = null;

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  renderCityData(currentCityKey);
  initForecastChart();
  bindEvents();
  fetchMunicipalIncidents();
});

// Map Initialization
function initMap() {
  const city = CITIES[currentCityKey];
  map = L.map('map', {
    zoomControl: false,
    attributionControl: true
  }).setView([city.lat, city.lon], city.zoom);

  // Clean Leaflet tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Position zoom controls in top-right
  L.control.zoom({ position: 'topright' }).addTo(map);
}

// Render Map Elements for City
function renderMapElements(cityKey) {
  const city = CITIES[cityKey];
  if (!city || !map) return;

  // Clear previous markers and overlays
  currentMarkers.forEach(m => map.removeLayer(m));
  currentMarkers = [];
  currentOverlays.forEach(o => map.removeLayer(o));
  currentOverlays = [];

  // 1. Hazard Plume / Incident Radius (Soft Coral Dashed Perimeter)
  if (city.hazardCenter) {
    const hazardCircle = L.circle(city.hazardCenter, {
      color: '#F28D77',
      dashArray: '6, 8',
      weight: 2.5,
      fillColor: '#F28D77',
      fillOpacity: 0.18,
      radius: city.hazardRadius || 1400
    }).addTo(map);
    currentOverlays.push(hazardCircle);
  }

  // 2. Frosted Circular Data Pins
  const pins = city.pins || [
    { name: 'PM2.5', pct: '64%', val: city.aqi.toString(), unit: 'µg/m³', lat: city.lat, lon: city.lon, type: city.statusClass }
  ];

  pins.forEach(pin => {
    const pinHtml = `
      <div class="frosted-map-pin">
        <span class="pin-pollutant-badge ${pin.type}">${pin.name} ${pin.pct}</span>
        <span class="pin-val">${pin.val}</span>
        <span class="pin-unit">${pin.unit}</span>
      </div>
    `;

    const icon = L.divIcon({
      className: 'custom-leaflet-div-icon',
      html: pinHtml,
      iconSize: [80, 80],
      iconAnchor: [40, 40]
    });

    const marker = L.marker([pin.lat, pin.lon], { icon }).addTo(map);
    currentMarkers.push(marker);
  });
}

// Render Telemetry & UI for City
function renderCityData(cityKey) {
  const city = CITIES[cityKey];
  if (!city) return;

  currentCityKey = cityKey;

  // Update Top Nav Location Capsule
  const locCapsule = document.getElementById('top-location-label');
  if (locCapsule) locCapsule.textContent = `${cityKey}, ${city.country || 'India'}`;

  // Update Gauge Card
  const cityTitleEl = document.getElementById('gauge-city-name');
  if (cityTitleEl) cityTitleEl.textContent = cityKey;

  const subLocEl = document.getElementById('gauge-sub-loc');
  if (subLocEl) subLocEl.textContent = `IN India • ${city.state || ''}`;

  const aqiNumEl = document.getElementById('gauge-aqi-val');
  if (aqiNumEl) aqiNumEl.textContent = city.aqi;

  const statusPill = document.getElementById('gauge-status-pill');
  if (statusPill) {
    statusPill.textContent = city.status;
    statusPill.className = `gauge-status-pill ${city.statusClass}`;
  }

  const metaEl = document.getElementById('gauge-telemetry-meta');
  if (metaEl) {
    metaEl.innerHTML = `<span>💨 ${city.wind}</span> • <span>🌡️ ${city.temp}</span>`;
  }

  // Update SVG Gauge Ring
  updateGaugeRing(city.aqi);

  // Update Forecast Title
  const forecastTitle = document.getElementById('forecast-chart-title');
  if (forecastTitle) {
    forecastTitle.textContent = `Air Quality Forecast — ${cityKey}`;
  }

  // Update Chart Data
  if (forecastChart) {
    const hourlyData = city.hourlyForecast || generateHourlyData(city.aqi);
    forecastChart.data.datasets[0].data = hourlyData;
    forecastChart.update('active');
  }

  // Pan Map
  if (map) {
    map.flyTo([city.lat, city.lon], city.zoom, { duration: 1.2 });
    renderMapElements(cityKey);
  }
}

// Helper: Circular Gauge SVG Update
function updateGaugeRing(aqi) {
  const progressCircle = document.getElementById('gauge-svg-progress');
  if (!progressCircle) return;

  // Total circumference for r=54 is 2 * PI * 54 = ~339.29
  const circumference = 339.29;
  // Map AQI (0 to 300) to dashoffset
  const pct = Math.min(Math.max(aqi / 300, 0.05), 1.0);
  const offset = circumference * (1 - pct * 0.75); // 270 degree arc

  progressCircle.style.strokeDasharray = `${circumference}`;
  progressCircle.style.strokeDashoffset = `${offset}`;

  // Color gradient
  if (aqi <= 75) {
    progressCircle.style.stroke = '#6ECBA8'; // Safe pastel sage
  } else if (aqi <= 150) {
    progressCircle.style.stroke = '#F6B26B'; // Moderate amber
  } else {
    progressCircle.style.stroke = '#F28D77'; // Hazard coral
  }
}

// Helper: Generate Smooth Hourly Curve
function generateHourlyData(baseAqi) {
  const deltas = [-10, -7, -2, 5, 16, 22, 18, 8, 0, -6, -12, -15, -12, -4, 8, 20, 24, 18];
  return deltas.map(d => Math.max(20, baseAqi + d));
}

// Initialize Chart.js 24-hr Forecast Chart
function initForecastChart() {
  const ctx = document.getElementById('forecastChart');
  if (!ctx) return;

  const labels = ['04:00', '07:00', '10:00', '13:00', '16:00', '19:00', '22:00', '01:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00', '00:00', '02:00', '05:00'];
  const city = CITIES[currentCityKey];
  const initialData = city.hourlyForecast || generateHourlyData(city.aqi);

  // Gradient area fill
  const chartCtx = ctx.getContext('2d');
  const gradient = chartCtx.createLinearGradient(0, 0, 0, 180);
  gradient.addColorStop(0, 'rgba(120, 96, 184, 0.22)');
  gradient.addColorStop(0.65, 'rgba(163, 136, 232, 0.08)');
  gradient.addColorStop(1, 'rgba(255, 255, 255, 0.0)');

  forecastChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'AQI Forecast',
        data: initialData,
        borderColor: '#7860B8',
        borderWidth: 2.6,
        backgroundColor: gradient,
        fill: true,
        tension: 0.42,
        pointBackgroundColor: '#FFFFFF',
        pointBorderColor: '#7860B8',
        pointBorderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#7860B8',
        pointHoverBorderColor: '#FFFFFF',
        pointHoverBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(29, 22, 53, 0.92)',
          titleColor: '#F8F6FD',
          bodyColor: '#FFFFFF',
          padding: 10,
          cornerRadius: 10,
          displayColors: false,
          callbacks: {
            label: (item) => `AQI: ${item.formattedValue}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false, drawBorder: false },
          ticks: {
            color: '#6E648B',
            font: { family: 'Outfit', size: 10.5 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8
          }
        },
        y: {
          grid: {
            color: '#EDE8F8',
            drawBorder: false
          },
          ticks: {
            color: '#6E648B',
            font: { family: 'Outfit', size: 10.5 },
            stepSize: 15
          },
          suggestedMin: 120,
          suggestedMax: 175
        }
      }
    }
  });
}

// Fetch Incidents from FastAPI Backend
async function fetchMunicipalIncidents() {
  try {
    const res = await fetch('/api/v1/municipal/incidents');
    if (!res.ok) return;
    const geojson = await res.json();
    if (!geojson || !geojson.features) return;

    geojson.features.forEach(feat => {
      if (feat.geometry.type === 'Point') {
        const [lon, lat] = feat.geometry.coordinates;
        const priority = feat.properties.alert_priority || 'MODERATE';
        const color = priority === 'CRITICAL' ? '#F28D77' : '#7860B8';

        const circleMarker = L.circleMarker([lat, lon], {
          radius: 9,
          fillColor: color,
          color: '#FFFFFF',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9
        }).addTo(map);

        circleMarker.bindPopup(`
          <div style="font-family: Outfit, sans-serif; font-size: 12px; color: #1D1635;">
            <strong>Incident ${feat.properties.ticket_id || 'Alert'}</strong><br/>
            Category: ${feat.properties.category || 'Emission'}<br/>
            Priority: <span style="color: ${color}; font-weight: 700;">${priority}</span>
          </div>
        `);
        currentOverlays.push(circleMarker);
      } else if (feat.geometry.type === 'Polygon') {
        const poly = L.geoJSON(feat, {
          style: {
            color: '#7860B8',
            weight: 1.5,
            fillColor: '#7860B8',
            fillOpacity: 0.22,
            dashArray: '4, 4'
          }
        }).addTo(map);
        currentOverlays.push(poly);
      }
    });
  } catch (err) {
    console.log('Using local baseline map data:', err);
  }
}

// Bind UI Interactive Events
function bindEvents() {
  // Region Selector Chips
  const chips = document.querySelectorAll('.region-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const cityKey = chip.getAttribute('data-city') || chip.textContent.trim();
      renderCityData(cityKey);
    });
  });

  // Forecast Timeframe Tabs
  const forecastTabs = document.querySelectorAll('.forecast-tab');
  forecastTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      forecastTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const mode = tab.getAttribute('data-mode');
      if (forecastChart) {
        const city = CITIES[currentCityKey];
        if (mode === 'daily') {
          forecastChart.data.labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
          forecastChart.data.datasets[0].data = [city.aqi - 15, city.aqi - 5, city.aqi, city.aqi + 18, city.aqi + 10, city.aqi - 8, city.aqi - 12];
        } else if (mode === 'monthly') {
          forecastChart.data.labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
          forecastChart.data.datasets[0].data = [city.aqi - 20, city.aqi - 5, city.aqi + 15, city.aqi];
        } else {
          // hourly
          forecastChart.data.labels = ['04:00', '07:00', '10:00', '13:00', '16:00', '19:00', '22:00', '01:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00', '00:00', '02:00', '05:00'];
          forecastChart.data.datasets[0].data = city.hourlyForecast || generateHourlyData(city.aqi);
        }
        forecastChart.update();
      }
    });
  });

  // Pitch Demo Spike Trigger
  const demoSpikeBtn = document.getElementById('pitch-demo-spike-btn');
  if (demoSpikeBtn) {
    demoSpikeBtn.addEventListener('click', async () => {
      const city = CITIES[currentCityKey];
      demoSpikeBtn.style.opacity = '0.6';
      demoSpikeBtn.textContent = 'Injecting Spike...';

      try {
        const res = await fetch('/api/v1/simulate/spike', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latitude: city.lat,
            longitude: city.lon,
            category: 'agricultural_stubble_burning'
          })
        });

        if (res.ok) {
          await fetchMunicipalIncidents();
        }
      } catch (e) {
        console.error('Demo spike injection failed:', e);
      } finally {
        demoSpikeBtn.style.opacity = '1';
        demoSpikeBtn.innerHTML = `
          <svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          Pitch Demo Spike
        `;
      }
    });
  }

  // View Options Apply / Cancel
  const btnApply = document.getElementById('btn-apply-options');
  if (btnApply) {
    btnApply.addEventListener('click', () => {
      btnApply.textContent = 'Applied';
      setTimeout(() => { btnApply.textContent = 'Apply'; }, 1000);
    });
  }

  const btnCancel = document.getElementById('btn-cancel-options');
  if (btnCancel) {
    btnCancel.addEventListener('click', () => {
      // Revert checkboxes to default
      document.getElementById('chk-pm25').checked = true;
      document.getElementById('chk-pm10').checked = true;
      document.getElementById('chk-o3').checked = false;
      document.getElementById('chk-no2').checked = false;
      document.getElementById('chk-aqi-area').checked = true;
    });
  }
}
