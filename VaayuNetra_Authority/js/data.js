// VaayuNetra Client Data & Real-Time API Sync Layer

let EVENTS = [
  {
    id: 'EVT-2026-0847',
    title: 'Open burning cluster — Okhla landfill perimeter',
    city: 'Delhi NCR',
    status: 'ACTIVE',
    severity: 'critical',
    confidence: 0.87,
    pollutant: 'PM2.5',
    peakValue: 312,
    unit: 'µg/m³',
    baseline: 68,
    anomalyScore: 4.6,
    lat: 28.5355,
    lng: 77.2910,
    detectedAt: '2026-09-05T18:42:00+05:30',
    sourceHypotheses: [
      { category: 'OPEN_BURNING', prob: 0.62 },
      { category: 'INDUSTRIAL_EMISSION', prob: 0.18 },
      { category: 'UNKNOWN', prob: 0.12 },
      { category: 'CONSTRUCTION_DUST', prob: 0.08 }
    ],
    evidence: [
      { type: 'sensor', label: 'CAAQMS Okhla Phase-2', detail: 'PM2.5 298→312 µg/m³ in 45 min', time: '18:42' },
      { type: 'citizen', label: 'Citizen report #CR-2291', detail: 'Visible smoke + burning smell, geotagged photo', time: '18:28' },
      { type: 'cv', label: 'CV validation', detail: 'Smoke plume detected (confidence 0.91)', time: '18:31' },
      { type: 'weather', label: 'Wind context', detail: 'NE 6 km/h, low mixing height', time: '18:00' }
    ],
    forecast: [
      { hour: 1, pm25: 285 }, { hour: 2, pm25: 240 }, { hour: 3, pm25: 198 },
      { hour: 4, pm25: 165 }, { hour: 5, pm25: 142 }, { hour: 6, pm25: 125 }
    ],
    exposure: { population: 48200, schools: 6, hospitals: 2, corridors: ['Mathura Road freight'] },
    priority: 94,
    jurisdiction: 'SDM South-East Delhi + DPCC',
    recommendedAction: 'Immediate field inspection + fire service alert. Issue notice to landfill operator. Activate local public advisory for 2 km radius.',
    timeline: [
      { time: '17:30', text: 'First anomalous reading at Okhla CAAQMS' },
      { time: '18:05', text: 'Local baseline exceeded (z > 3.5)' },
      { time: '18:28', text: 'Citizen report received with image' },
      { time: '18:31', text: 'CV confirmed smoke plume' },
      { time: '18:42', text: 'Event created → escalated to ACTIVE' },
      { time: '18:55', text: 'Priority 94 — routed to SDM + DPCC' }
    ]
  },
  {
    id: 'EVT-2026-0841',
    title: 'Construction dust plume — Outer Ring Road, Sarita Vihar',
    city: 'Delhi NCR',
    status: 'ACTIVE',
    severity: 'high',
    confidence: 0.74,
    pollutant: 'PM10',
    peakValue: 428,
    unit: 'µg/m³',
    baseline: 145,
    anomalyScore: 2.9,
    lat: 28.5340,
    lng: 77.2700,
    detectedAt: '2026-09-05T16:15:00+05:30',
    sourceHypotheses: [
      { category: 'CONSTRUCTION_DUST', prob: 0.71 },
      { category: 'ROAD_TRAFFIC', prob: 0.19 },
      { category: 'UNKNOWN', prob: 0.10 }
    ],
    evidence: [
      { type: 'sensor', label: 'IoT node ORR-SV-03', detail: 'PM10 sustained >350 for 90 min', time: '16:15' },
      { type: 'citizen', label: 'Citizen report #CR-2284', detail: 'Uncovered debris & earthwork', time: '15:50' }
    ],
    forecast: [
      { hour: 1, pm25: 110 }, { hour: 2, pm25: 95 }, { hour: 3, pm25: 82 }
    ],
    exposure: { population: 21500, schools: 3, hospitals: 0, corridors: ['Outer Ring Road'] },
    priority: 71,
    jurisdiction: 'MCD South + Traffic Police',
    recommendedAction: 'Issue stop-work / dust-suppression notice. Request water sprinkling on ORR stretch.',
    timeline: [
      { time: '15:20', text: 'IoT sensors show rising PM10' },
      { time: '15:50', text: 'Citizen geotagged construction site' },
      { time: '16:15', text: 'Event confirmed ACTIVE' }
    ]
  },
  {
    id: 'EVT-2026-0839',
    title: 'Traffic corridor spike — ITO to Rajghat',
    city: 'Delhi NCR',
    status: 'CORROBORATED',
    severity: 'moderate',
    confidence: 0.68,
    pollutant: 'NO2',
    peakValue: 89,
    unit: 'ppb',
    baseline: 42,
    anomalyScore: 2.1,
    lat: 28.6280,
    lng: 77.2410,
    detectedAt: '2026-09-05T14:40:00+05:30',
    sourceHypotheses: [
      { category: 'ROAD_TRAFFIC', prob: 0.78 },
      { category: 'UNKNOWN', prob: 0.22 }
    ],
    evidence: [
      { type: 'sensor', label: 'CAAQMS ITO', detail: 'NO2 elevated during peak hour', time: '14:40' },
      { type: 'weather', label: 'Calm winds', detail: 'Wind < 3 km/h, inversion layer', time: '14:00' }
    ],
    forecast: [
      { hour: 1, pm25: 72 }, { hour: 2, pm25: 58 }
    ],
    exposure: { population: 34000, schools: 2, hospitals: 1, corridors: ['Ring Road', 'ITO'] },
    priority: 58,
    jurisdiction: 'Traffic Police + DPCC',
    recommendedAction: 'Monitor. Consider temporary traffic diversion if persists beyond 2 h.',
    timeline: [
      { time: '14:10', text: 'Peak-hour NO2 rise detected' },
      { time: '14:40', text: 'Corroborated with wind context' }
    ]
  },
  {
    id: 'EVT-2026-0822',
    title: 'Agricultural residue burning — fringe NCR (Haryana border)',
    city: 'Delhi NCR',
    status: 'RESOLVED',
    severity: 'high',
    confidence: 0.81,
    pollutant: 'PM2.5',
    peakValue: 265,
    unit: 'µg/m³',
    baseline: 55,
    anomalyScore: 3.8,
    lat: 28.7200,
    lng: 76.9800,
    detectedAt: '2026-09-04T21:10:00+05:30',
    sourceHypotheses: [
      { category: 'AGRICULTURAL_BURNING', prob: 0.69 },
      { category: 'OPEN_BURNING', prob: 0.21 },
      { category: 'UNKNOWN', prob: 0.10 }
    ],
    evidence: [
      { type: 'firms', label: 'FIRMS thermal anomaly', detail: 'Hotspot cluster within 8 km', time: '20:55' },
      { type: 'sensor', label: 'CAAQMS Bawana', detail: 'PM2.5 surge overnight', time: '21:10' }
    ],
    forecast: [],
    exposure: { population: 19000, schools: 1, hospitals: 0, corridors: [] },
    priority: 0,
    jurisdiction: 'Haryana PCB + Delhi DPCC',
    recommendedAction: 'Closed — residual monitoring for 12 h.',
    timeline: [
      { time: '20:55', text: 'FIRMS hotspot detected' },
      { time: '21:10', text: 'Ground sensors confirmed' },
      { time: '09:00', text: 'Levels returned to baseline — RESOLVED' }
    ]
  },
  {
    id: 'EVT-2026-0849',
    title: 'Candidate: Industrial stack anomaly — Mayapuri',
    city: 'Delhi NCR',
    status: 'CANDIDATE',
    severity: 'moderate',
    confidence: 0.52,
    pollutant: 'SO2',
    peakValue: 48,
    unit: 'ppb',
    baseline: 12,
    anomalyScore: 2.4,
    lat: 28.6300,
    lng: 77.1200,
    detectedAt: '2026-09-05T19:05:00+05:30',
    sourceHypotheses: [
      { category: 'INDUSTRIAL_EMISSION', prob: 0.55 },
      { category: 'UNKNOWN', prob: 0.45 }
    ],
    evidence: [
      { type: 'sensor', label: 'IoT Mayapuri-01', detail: 'SO2 elevated, single sensor', time: '19:05' }
    ],
    forecast: [],
    exposure: { population: 12000, schools: 1, hospitals: 0, corridors: [] },
    priority: 41,
    jurisdiction: 'DPCC Industrial',
    recommendedAction: 'Await corroboration from second sensor or citizen evidence before escalation.',
    timeline: [
      { time: '19:05', text: 'Single-sensor anomaly flagged as CANDIDATE' }
    ]
  },
  {
    id: 'EVT-2026-0901',
    title: 'Landfill combustion flare — Deonar sector',
    city: 'Mumbai',
    status: 'ACTIVE',
    severity: 'critical',
    confidence: 0.92,
    pollutant: 'PM2.5',
    peakValue: 288,
    unit: 'µg/m³',
    baseline: 45,
    anomalyScore: 4.1,
    lat: 19.0550,
    lng: 72.9300,
    detectedAt: '2026-09-06T01:20:00+05:30',
    sourceHypotheses: [
      { category: 'OPEN_BURNING', prob: 0.75 },
      { category: 'INDUSTRIAL_EMISSION', prob: 0.25 }
    ],
    evidence: [
      { type: 'firms', label: 'NASA FIRMS VIIRS Hotspot', detail: 'FRP 18.5 MW detected at Deonar ridge', time: '01:15' },
      { type: 'sensor', label: 'Chembur East CAAQMS', detail: 'PM2.5 reached 288 µg/m³', time: '01:20' }
    ],
    forecast: [
      { hour: 1, pm25: 260 }, { hour: 2, pm25: 210 }, { hour: 3, pm25: 175 }
    ],
    exposure: { population: 54000, schools: 7, hospitals: 3, corridors: ['Eastern Freeway'] },
    priority: 91,
    jurisdiction: 'BMC Solid Waste & MPCB',
    recommendedAction: 'Dispatch Chembur Fire Squad and deploy mist cannons along Mankhurd corridor.',
    timeline: [
      { time: '01:15', text: 'Satellite thermal match confirmed' },
      { time: '01:20', text: 'Event marked CRITICAL' }
    ]
  },
  {
    id: 'EVT-2026-0902',
    title: 'Solid waste burning — Dhapa dumpsite',
    city: 'Kolkata',
    status: 'ACTIVE',
    severity: 'high',
    confidence: 0.84,
    pollutant: 'PM2.5',
    peakValue: 245,
    unit: 'µg/m³',
    baseline: 52,
    anomalyScore: 3.4,
    lat: 22.5450,
    lng: 88.4200,
    detectedAt: '2026-09-06T00:45:00+05:30',
    sourceHypotheses: [
      { category: 'OPEN_BURNING', prob: 0.68 },
      { category: 'UNKNOWN', prob: 0.32 }
    ],
    evidence: [
      { type: 'sensor', label: 'EM Bypass CAAQMS', detail: 'PM2.5 spike >220', time: '00:45' }
    ],
    forecast: [
      { hour: 1, pm25: 225 }, { hour: 2, pm25: 185 }, { hour: 3, pm25: 150 }
    ],
    exposure: { population: 38000, schools: 4, hospitals: 1, corridors: ['EM Bypass'] },
    priority: 78,
    jurisdiction: 'KMC Solid Waste & WBPCB',
    recommendedAction: 'Deploy water dousing tankers to Dhapa southern perimeter.',
    timeline: [
      { time: '00:45', text: 'Elevated ground reading at EM Bypass node' }
    ]
  },
  {
    id: 'EVT-2026-0903',
    title: 'Industrial metallurgical stack emissions — Peenya',
    city: 'Bengaluru',
    status: 'ACTIVE',
    severity: 'moderate',
    confidence: 0.72,
    pollutant: 'PM10',
    peakValue: 195,
    unit: 'µg/m³',
    baseline: 65,
    anomalyScore: 2.6,
    lat: 13.0300,
    lng: 77.5100,
    detectedAt: '2026-09-05T22:15:00+05:30',
    sourceHypotheses: [
      { category: 'INDUSTRIAL_EMISSION', prob: 0.79 },
      { category: 'ROAD_TRAFFIC', prob: 0.21 }
    ],
    evidence: [
      { type: 'sensor', label: 'Peenya Industrial Node 4', detail: 'PM10 elevated for 3 hours', time: '22:15' }
    ],
    forecast: [
      { hour: 1, pm25: 95 }, { hour: 2, pm25: 80 }
    ],
    exposure: { population: 26000, schools: 3, hospitals: 1, corridors: ['Tumkur Road'] },
    priority: 62,
    jurisdiction: 'KSPCB Industrial Vigilance',
    recommendedAction: 'Issue inspection notice to smelting cluster on 4th Phase.',
    timeline: [
      { time: '22:15', text: 'IoT anomaly verified' }
    ]
  },
  {
    id: 'EVT-2026-0904',
    title: 'Transport hub congestion & road dust — Transport Nagar',
    city: 'Lucknow',
    status: 'ACTIVE',
    severity: 'high',
    confidence: 0.79,
    pollutant: 'PM2.5',
    peakValue: 275,
    unit: 'µg/m³',
    baseline: 72,
    anomalyScore: 3.5,
    lat: 26.7900,
    lng: 80.8800,
    detectedAt: '2026-09-06T02:10:00+05:30',
    sourceHypotheses: [
      { category: 'ROAD_TRAFFIC', prob: 0.58 },
      { category: 'CONSTRUCTION_DUST', prob: 0.42 }
    ],
    evidence: [
      { type: 'sensor', label: 'Sarojini Nagar CAAQMS', detail: 'PM2.5 persistent elevation', time: '02:10' }
    ],
    forecast: [
      { hour: 1, pm25: 250 }, { hour: 2, pm25: 220 }, { hour: 3, pm25: 190 }
    ],
    exposure: { population: 31000, schools: 2, hospitals: 1, corridors: ['Kanpur Road Highway'] },
    priority: 76,
    jurisdiction: 'LMC & UPPCB',
    recommendedAction: 'Operate anti-smog sweepers and divert freight trucks.',
    timeline: [
      { time: '02:10', text: 'Freight corridor spike detected' }
    ]
  }
];

let HOURLY = [
  { t: '04:00', aqi: 178 }, { t: '05:00', aqi: 185 }, { t: '06:00', aqi: 192 },
  { t: '07:00', aqi: 198 }, { t: '08:00', aqi: 205 }, { t: '09:00', aqi: 210 },
  { t: '10:00', aqi: 202 }, { t: '11:00', aqi: 195 }, { t: '12:00', aqi: 188 },
  { t: '13:00', aqi: 182 }, { t: '14:00', aqi: 175 }, { t: '15:00', aqi: 170 },
  { t: '16:00', aqi: 178 }, { t: '17:00', aqi: 190 }, { t: '18:00', aqi: 205 },
  { t: '19:00', aqi: 215 }, { t: '20:00', aqi: 220 }, { t: '21:00', aqi: 212 }
];

let ACTIONS = [
  { id: 'ACT-112', eventId: 'EVT-2026-0847', type: 'FIELD_INSPECTION', assignee: 'SDM South-East', status: 'DISPATCHED', createdAt: '2026-09-05T18:58:00+05:30', eta: '19:40' },
  { id: 'ACT-111', eventId: 'EVT-2026-0847', type: 'NOTICE_DRAFT', assignee: 'DPCC Legal', status: 'IN_PROGRESS', createdAt: '2026-09-05T19:02:00+05:30', eta: null },
  { id: 'ACT-109', eventId: 'EVT-2026-0841', type: 'DUST_SUPPRESSION', assignee: 'MCD South', status: 'PENDING', createdAt: '2026-09-05T16:30:00+05:30', eta: null }
];

let ADVISORIES = [
  { id: 'ADV-041', eventId: 'EVT-2026-0847', title: 'Public health advisory — Okhla / Sarita Vihar', audience: 'Residents within 2 km', languages: ['EN', 'HI'], status: 'SENT', sentAt: '2026-09-05T19:10:00+05:30', channels: ['SMS', 'IVR', 'App'] },
  { id: 'ADV-040', eventId: 'EVT-2026-0841', title: 'Dust advisory — Outer Ring Road', audience: 'Commuters & nearby residents', languages: ['EN', 'HI'], status: 'DRAFT', sentAt: null, channels: [] },
  { id: 'ADV-039', eventId: 'EVT-2026-0839', title: 'Traffic pollution note — ITO corridor', audience: 'Sensitive groups', languages: ['EN'], status: 'SENT', sentAt: '2026-09-05T15:20:00+05:30', channels: ['App'] }
];

let REGIONS = [
  { name: 'Delhi NCR', state: 'Delhi', lat: 28.6139, lng: 77.2090, current_aqi: 186, status: 'Poor', dominant_pollutant: 'PM2.5', weather_desc: 'NW 3.8 m/s · 29°C' },
  { name: 'Mumbai', state: 'Maharashtra', lat: 19.0760, lng: 72.8777, current_aqi: 142, status: 'Moderate', dominant_pollutant: 'PM2.5', weather_desc: 'WSW 4.2 m/s · 31°C' },
  { name: 'Bengaluru', state: 'Karnataka', lat: 12.9716, lng: 77.5946, current_aqi: 85, status: 'Satisfactory', dominant_pollutant: 'PM10', weather_desc: 'E 3.1 m/s · 24°C' },
  { name: 'Kolkata', state: 'West Bengal', lat: 22.5726, lng: 88.3639, current_aqi: 168, status: 'Poor', dominant_pollutant: 'PM2.5', weather_desc: 'S 2.8 m/s · 30°C' },
  { name: 'Chennai', state: 'Tamil Nadu', lat: 13.0827, lng: 80.2707, current_aqi: 94, status: 'Satisfactory', dominant_pollutant: 'PM10', weather_desc: 'SE 4.5 m/s · 32°C' },
  { name: 'Hyderabad', state: 'Telangana', lat: 17.3850, lng: 78.4867, current_aqi: 118, status: 'Moderate', dominant_pollutant: 'PM2.5', weather_desc: 'ESE 3.4 m/s · 28°C' },
  { name: 'Ahmedabad', state: 'Gujarat', lat: 23.0225, lng: 72.5714, current_aqi: 172, status: 'Poor', dominant_pollutant: 'PM2.5', weather_desc: 'WNW 3.9 m/s · 33°C' },
  { name: 'Pune', state: 'Maharashtra', lat: 18.5204, lng: 73.8567, current_aqi: 104, status: 'Moderate', dominant_pollutant: 'PM10', weather_desc: 'W 3.2 m/s · 27°C' },
  { name: 'Lucknow', state: 'Uttar Pradesh', lat: 26.8467, lng: 80.9462, current_aqi: 215, status: 'Very Poor', dominant_pollutant: 'PM2.5', weather_desc: 'NE 2.6 m/s · 29°C' },
  { name: 'Patna', state: 'Bihar', lat: 25.5941, lng: 85.1376, current_aqi: 238, status: 'Very Poor', dominant_pollutant: 'PM2.5', weather_desc: 'E 2.1 m/s · 30°C' },
  { name: 'Ranchi', state: 'Jharkhand', lat: 23.3441, lng: 85.3096, current_aqi: 131, status: 'Moderate', dominant_pollutant: 'PM2.5', weather_desc: 'NE 2.9 m/s · 27°C' },
];

let CURRENT_CITY = 'Delhi NCR';
let ALERTS = [];

let ACTIVE_FILTERS = {
  pollutants: { 'PM2.5': true, 'PM10': true, 'O3': false, 'NO2': false, 'SO2': false },
  statuses: { 'ACTIVE': true, 'CANDIDATE': true, 'RESOLVED': false },
  layers: { 'footprints': true, 'sensors': true, 'plumes': true, 'hotspots': true, 'receptors': true },
  aqiColorArea: true,
};

function getEvent(id) { return EVENTS.find(e => e.id === id) || null; }

function getRegion(name) {
  const n = (name || '').toLowerCase();
  return REGIONS.find(r => r.name.toLowerCase().includes(n) || n.includes(r.name.toLowerCase())) || REGIONS[0];
}

function formatTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false });
}

function sevPill(s) {
  return { critical: 'pill-critical', high: 'pill-high', moderate: 'pill-moderate', low: 'pill-low' }[s] || 'pill-moderate';
}

function statusPill(s) {
  return { ACTIVE: 'pill-active', CANDIDATE: 'pill-candidate', CORROBORATED: 'pill-high', RESOLVED: 'pill-resolved' }[s] || 'pill-resolved';
}

// ===== Robust API Client Connected to FastAPI Backend =====
const API_BASE = (typeof window !== 'undefined' && window.location.origin && window.location.origin !== 'null' && window.location.protocol !== 'file:')
  ? window.location.origin
  : 'http://127.0.0.1:8000';

const VaayuAPI = {
  // Sync all entities from FastAPI backend
  async syncWithBackend() {
    try {
      const [eventsRes, actionsRes, advRes, forecastRes, regionsRes, alertsRes] = await Promise.allSettled([
        fetch(`${API_BASE}/api/v1/events`),
        fetch(`${API_BASE}/api/v1/actions`),
        fetch(`${API_BASE}/api/v1/advisories`),
        fetch(`${API_BASE}/api/v1/forecast/hourly?city=${encodeURIComponent(CURRENT_CITY)}`),
        fetch(`${API_BASE}/api/v1/forecast/regions`),
        fetch(`${API_BASE}/api/v1/alerts`),
      ]);

      if (eventsRes.status === 'fulfilled' && eventsRes.value.ok) {
        const remoteEvents = await eventsRes.value.json();
        if (Array.isArray(remoteEvents) && remoteEvents.length > 0) {
          EVENTS = remoteEvents;
        }
      }

      if (actionsRes.status === 'fulfilled' && actionsRes.value.ok) {
        const remoteActions = await actionsRes.value.json();
        if (Array.isArray(remoteActions) && remoteActions.length > 0) {
          ACTIONS = remoteActions;
        }
      }

      if (advRes.status === 'fulfilled' && advRes.value.ok) {
        const remoteAdv = await advRes.value.json();
        if (Array.isArray(remoteAdv) && remoteAdv.length > 0) {
          ADVISORIES = remoteAdv;
        }
      }

      if (regionsRes.status === 'fulfilled' && regionsRes.value.ok) {
        const remoteRegions = await regionsRes.value.json();
        if (Array.isArray(remoteRegions) && remoteRegions.length > 0) {
          REGIONS = remoteRegions;
        }
      }

      if (forecastRes.status === 'fulfilled' && forecastRes.value.ok) {
        const remoteForecast = await forecastRes.value.json();
        if (remoteForecast.hourly && remoteForecast.hourly.length > 0) {
          HOURLY = remoteForecast.hourly;
        }
      }

      if (alertsRes.status === 'fulfilled' && alertsRes.value.ok) {
        const remoteAlerts = await alertsRes.value.json();
        if (Array.isArray(remoteAlerts) && remoteAlerts.length > 0) {
          ALERTS = remoteAlerts;
        }
      }
    } catch (err) {
      console.warn('Backend sync completed with local cache fallback:', err);
    }
  },

  // Fetch forecast for specific Indian city
  async fetchForecastForCity(cityName) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/forecast/hourly?city=${encodeURIComponent(cityName)}`);
      if (res.ok) {
        const data = await res.json();
        CURRENT_CITY = data.city;
        HOURLY = data.hourly;
        return data;
      }
    } catch (err) {
      console.warn(`Fallback local forecast for ${cityName}:`, err);
    }
    const reg = getRegion(cityName);
    CURRENT_CITY = reg.name;
    return {
      city: reg.name,
      country: 'India',
      current_aqi: reg.current_aqi,
      category: reg.status,
      dominant_pollutant: reg.dominant_pollutant,
      hourly: HOURLY,
    };
  },

  // Dispatch Action
  async dispatchAction(payload) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const action = await res.json();
        ACTIONS.unshift(action);
        const ev = getEvent(payload.eventId);
        if (ev) {
          ev.timeline.push({
            time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false }),
            text: `Action ${action.id} (${action.type}) dispatched to ${action.assignee}`,
          });
        }
        return action;
      }
    } catch (e) {
      console.warn('Fallback: local action dispatch');
    }

    const localId = `ACT-${ACTIONS.length + 115}`;
    const newAction = {
      id: localId,
      eventId: payload.eventId,
      type: payload.type || 'FIELD_INSPECTION',
      assignee: payload.assignee || 'SDM South-East',
      status: 'DISPATCHED',
      createdAt: new Date().toISOString(),
      eta: '35 min',
      notes: payload.notes || '',
    };
    ACTIONS.unshift(newAction);
    return newAction;
  },

  // Broadcast Advisory
  async createAdvisory(payload) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/advisories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const adv = await res.json();
        ADVISORIES.unshift(adv);
        return adv;
      }
    } catch (e) {
      console.warn('Fallback: local advisory compose');
    }

    const localId = `ADV-0${ADVISORIES.length + 42}`;
    const newAdv = {
      id: localId,
      eventId: payload.eventId,
      title: payload.title || `Public health advisory — ${payload.eventId}`,
      audience: payload.audience || 'Residents within 2 km',
      languages: payload.languages || ['EN', 'HI'],
      channels: payload.channels || ['SMS', 'IVR', 'App'],
      status: 'SENT',
      sentAt: new Date().toISOString(),
      message: payload.message || '',
    };
    ADVISORIES.unshift(newAdv);
    return newAdv;
  },

  // Send Draft Advisory
  async sendAdvisory(advId) {
    try {
      await fetch(`${API_BASE}/api/v1/advisories/${advId}/send`, { method: 'POST' });
    } catch (e) {
      console.warn('Local draft status update');
    }
    const adv = ADVISORIES.find(a => a.id === advId);
    if (adv) {
      adv.status = 'SENT';
      adv.sentAt = new Date().toISOString();
    }
    return adv;
  },

  // Generate Legal Notice Document
  async generateNotice(eventId) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/events/${eventId}/notice`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Fallback: local notice generator');
    }

    const ev = getEvent(eventId);
    if (!ev) return null;
    const ref = `DPCC/ENV/VIG/2026/${eventId.replace('EVT-', '')}`;
    return {
      notice_id: `NOT-${eventId}`,
      event_id: eventId,
      reference_no: ref,
      issuing_authority: ev.jurisdiction || 'Delhi Pollution Control Committee',
      recipient: `Occupier / In-charge, ${ev.title}`,
      issued_at: new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }),
      subject: `Statutory Direction under Section 31A Air Act 1981 — ${ev.title}`,
      event_title: ev.title,
      severity: ev.severity,
      coordinates: `${ev.lat.toFixed(4)}, ${ev.lng.toFixed(4)}`,
      peak_pollutant: `${ev.pollutant} ${ev.peakValue} ${ev.unit}`,
      baseline: `${ev.baseline} ${ev.unit}`,
      anomaly: `${ev.anomalyScore}σ`,
      evidence_summary: ev.evidence.map(e => ({ source: e.label, details: e.detail })),
      impact_summary: ev.exposure,
      directives: [
        'Cease and desist all open emissions immediately.',
        'Deploy wet dust suppression within 4 hours.',
        'Submit written compliance within 24 hours.',
      ],
      compliance_deadline_hours: 24,
      penal_provisions: 'Section 37 Air Act 1981 & Section 15 Environment Protection Act 1986',
      html_document: `<h1>STATUTORY NOTICE: ${ref}</h1><p>Event: ${ev.title}</p><p>Peak: ${ev.pollutant} ${ev.peakValue} ${ev.unit}</p>`,
    };
  },

  // Fetch Alerts
  async fetchAlerts() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/alerts`);
      if (res.ok) {
        ALERTS = await res.json();
        return ALERTS;
      }
    } catch (e) {
      console.warn('Fallback alerts');
    }
    return ALERTS;
  },

  // Acknowledge Alert
  async acknowledgeAlert(alertId) {
    try {
      await fetch(`${API_BASE}/api/v1/alerts/${alertId}/acknowledge`, { method: 'POST' });
    } catch (e) {}
    const alt = ALERTS.find(a => a.id === alertId);
    if (alt) alt.acknowledged = true;
    return alt;
  },
};
