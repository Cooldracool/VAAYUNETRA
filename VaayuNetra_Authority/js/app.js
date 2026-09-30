let map = null;
let charts = {};

// Map Layer Groups for Dynamic Filtering
let layerGroups = {
  footprints: null,
  sensors: null,
  plumes: null,
  hotspots: null,
  receptors: null,
  glow: null,
};

function destroyCharts() {
  Object.values(charts).forEach(c => {
    try { c.destroy(); } catch (e) {}
  });
  charts = {};
}

function clearMap() {
  if (map) {
    try { map.remove(); } catch (e) {}
    map = null;
  }
  layerGroups = { footprints: null, sensors: null, plumes: null, hotspots: null, receptors: null, glow: null };
}

function toast(title, msg) {
  const box = document.getElementById('toasts');
  if (!box) return;
  const el = document.createElement('div');
  el.className = 'toast';
  el.innerHTML = `<div>✅</div><div><strong>${title}</strong><span>${msg}</span></div>`;
  box.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 300);
  }, 3200);
}

function setNav(page) {
  document.querySelectorAll('.nav-item').forEach(a => {
    a.classList.toggle('active', a.dataset.page === page);
  });
}

/* ========== BILINGUAL LOCALIZATION (EN / HI) ========== */
const I18N = {
  en: {
    nav_home: "Home",
    nav_map: "Air Maps",
    nav_events: "Events",
    nav_forecast: "Forecast",
    nav_actions: "Actions",
    nav_advisories: "Advisories",
    user_role: "Authority Officer",
    search_placeholder: "Search Indian cities (e.g. Mumbai, Bengaluru, Kolkata, Delhi)...",
    toast_lang_title: "Language Changed",
    toast_lang_body: "Authority console switched to English",
    region_label: "📍 INDIA REGION:",
    view_options: "◎ View Options",
    layers_filters_btn: "🎛️ Layers & Filters",
    pollutant: "Pollutant",
    aqi_color_area: "AQI Color Area",
    close: "Close",
    apply: "Apply",
    events_heading: "Environmental Events",
    events_sub: "Event-centric priority queue · multi-source evidence corroboration",
    actions_heading: "Authority Actions & Dispatch",
    actions_sub: "Dispatch, notices, field inspections, anti-smog deployments",
    draft_notice_btn: "📜 Draft notice",
    generate_notice_btn: "Generate notice",
  },
  hi: {
    nav_home: "होम",
    nav_map: "वायु मानचित्र",
    nav_events: "प्रदूषण घटनाएं",
    nav_forecast: "पूर्वानुमान",
    nav_actions: "त्वरित कार्रवाई",
    nav_advisories: "जन परामर्श",
    user_role: "प्राधिकरण अधिकारी",
    search_placeholder: "भारतीय शहर खोजें (उदा. दिल्ली, मुंबई, बेंगलुरु, कोलकाता)...",
    toast_lang_title: "भाषा परिवर्तित",
    toast_lang_body: "प्राधिकरण कंसोल हिंदी (Hindi) में सक्रिय किया गया।",
    region_label: "📍 भारत क्षेत्र:",
    view_options: "◎ दृश्य विकल्प (फिल्टर)",
    layers_filters_btn: "🎛️ परतें एवं फिल्टर",
    pollutant: "प्रदूषक तत्व",
    aqi_color_area: "AQI रंग क्षेत्र",
    close: "बंद करें",
    apply: "लागू करें",
    events_heading: "पर्यावरणीय घटनाएं (प्रदूषण)",
    events_sub: "घटना-केंद्रित प्राथमिकता सूची · बहु-स्रोत साक्ष्य सत्यापन",
    actions_heading: "प्राधिकरण कार्रवाई एवं प्रेषण",
    actions_sub: "दल प्रेषण, वैधानिक नोटिस (धारा 31A), फील्ड निरीक्षण",
    draft_notice_btn: "📜 नोटिस तैयार करें",
    generate_notice_btn: "नोटिस जारी करें",
  }
};

let CURRENT_LANG = localStorage.getItem('vaayunetra_lang') || 'en';

function t(key) {
  return (I18N[CURRENT_LANG] && I18N[CURRENT_LANG][key]) || (I18N.en[key] || key);
}

function setLanguage(lang, triggerToast = true) {
  if (lang !== 'en' && lang !== 'hi') lang = 'en';
  CURRENT_LANG = lang;
  try { localStorage.setItem('vaayunetra_lang', lang); } catch (e) {}

  // Update pills active status
  const pillEn = document.getElementById('langBtnEn');
  const pillHi = document.getElementById('langBtnHi');
  if (pillEn && pillHi) {
    pillEn.classList.toggle('active', lang === 'en');
    pillHi.classList.toggle('active', lang === 'hi');
  }

  // Update static DOM elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const k = el.dataset.i18n;
    if (I18N[lang] && I18N[lang][k]) {
      el.textContent = I18N[lang][k];
    }
  });

  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.placeholder = t('search_placeholder');
  }

  if (triggerToast) {
    toast(t('toast_lang_title'), t('toast_lang_body'));
  }

  // Re-render current page
  router();
}

function toggleMobileViewOptions() {
  const panel = document.getElementById('dashViewOptions');
  const fab = document.getElementById('mobileFilterFab');
  if (!panel) return;
  panel.classList.toggle('open');
  if (fab) {
    fab.style.display = panel.classList.contains('open') ? 'none' : 'inline-flex';
  }
}

/* ========== ROUTER ========== */
function router() {
  destroyCharts();
  clearMap();
  const hash = (window.location.hash.slice(1) || '/').replace(/^\//, '');
  const [page, id] = hash.split('/');
  const p = page || 'dashboard';
  setNav(p === 'event' ? 'events' : p);

  const root = document.getElementById('pageRoot');
  if (!root) return;

  switch (p) {
    case 'dashboard':
    case '':
      root.innerHTML = viewDashboard();
      setTimeout(() => {
        initMainMap('mainMap');
        initForecastChart('dashChart');
      }, 40);
      break;
    case 'map':
      root.innerHTML = viewMap();
      setTimeout(() => {
        initAirMap('fullMap');
      }, 40);
      break;
    case 'events':
      root.innerHTML = viewEvents();
      break;
    case 'event':
      root.innerHTML = viewEvent(id);
      if (id) setTimeout(() => { initEventMap(id); initEventChart(id); }, 40);
      break;
    case 'forecast':
      root.innerHTML = viewForecast();
      setTimeout(() => {
        initForecastChart('fullChart');
      }, 40);
      break;
    case 'actions':
      root.innerHTML = viewActions();
      break;
    case 'advisories':
      root.innerHTML = viewAdvisories();
      break;
    default:
      root.innerHTML = viewDashboard();
      setTimeout(() => { initMainMap('mainMap'); initForecastChart('dashChart'); }, 40);
  }
  bindActions();
}

/* ========== REGION METRIC BUBBLES (live pollutant values per region) ========== */
function _bubbleData(reg) {
  const m = (reg && reg.metrics && Object.keys(reg.metrics).length) ? reg.metrics
    : { 'PM2.5': 108, 'PM10': 245, 'NO2': 62, 'O3': 41 };
  const total = (m['PM2.5'] || 0) + (m['PM10'] || 0) + (m['NO2'] || 0) + (m['O3'] || 0);
  const pct = k => total > 0 ? Math.round(((m[k] || 0) / total) * 100) : 0;
  return {
    'O3':  { label: 'O₃',    pct: pct('O3'),    val: (m['O3'] || 0).toFixed(2) },
    'NO2': { label: 'NO₂',   pct: pct('NO2'),   val: (m['NO2'] || 0).toFixed(2) },
    'PM10':{ label: 'PM10',  pct: pct('PM10'),  val: (m['PM10'] || 0).toFixed(2) },
    'PM2.5':{ label: 'PM2.5', pct: pct('PM2.5'), val: (m['PM2.5'] || 0).toFixed(0) },
  };
}

function updateMetricBubbles(reg) {
  const data = _bubbleData(reg);
  const map = { bubbleO3: 'O3', bubbleNo2: 'NO2', bubblePm10: 'PM10', bubblePm25: 'PM2.5' };
  Object.entries(map).forEach(([id, key]) => {
    const el = document.getElementById(id);
    if (!el) return;
    const pctEl = el.querySelector('.pct');
    const valEl = el.querySelector('.val');
    if (pctEl) pctEl.textContent = `${data[key].label} ${data[key].pct}%`;
    if (valEl) valEl.textContent = data[key].val;
  });
}

/* ========== REGION SWITCHER LOGIC ========== */
async function switchRegion(cityName) {
  toast('Region Switching', `Loading live environmental telemetry for ${cityName}...`);
  const forecastData = await VaayuAPI.fetchForecastForCity(cityName);
  CURRENT_CITY = forecastData.city;
  const reg = getRegion(CURRENT_CITY);

  // Update Region Bar Pills in UI
  document.querySelectorAll('.region-pill').forEach(pill => {
    pill.classList.toggle('active', pill.dataset.city === CURRENT_CITY);
  });

  // Update Search input
  const searchInput = document.getElementById('searchInput');
  if (searchInput) searchInput.value = `${CURRENT_CITY}, India`;

  // Update Dashboard AQI Card if present
  const aqiNum = document.querySelector('.aqi-card .aqi-num');
  const aqiCity = document.querySelector('.aqi-card .city');
  const aqiStatus = document.querySelector('.aqi-card .aqi-status');
  if (aqiNum) aqiNum.textContent = forecastData.current_aqi;
  if (aqiCity) aqiCity.textContent = forecastData.city;
  if (aqiStatus) aqiStatus.innerHTML = `⚠ ${forecastData.category}`;

  // Update floating pollutant metric bubbles for the new region
  updateMetricBubbles(reg);

  // Pan Map
  if (map && reg) {
    map.flyTo([reg.lat, reg.lng], 11, { duration: 1.2 });
  }

  // Re-render Air Maps markers with the new region's data
  if (document.getElementById('fullMap')) {
    renderAirMapLayers();
  }

  // Re-render Forecast Chart with new region's data
  if (charts.dashChart) {
    charts.dashChart.data.labels = HOURLY.map(d => d.t);
    charts.dashChart.data.datasets[0].data = HOURLY.map(d => d.aqi);
    charts.dashChart.update();
  }
  if (charts.fullChart) {
    charts.fullChart.data.labels = HOURLY.map(d => d.t);
    charts.fullChart.data.datasets[0].data = HOURLY.map(d => d.aqi);
    charts.fullChart.update();
  }

  toast('Region Active', `${CURRENT_CITY}: AQI ${forecastData.current_aqi} (${forecastData.category})`);
}

/* ========== MODAL RENDERERS ========== */
function openNoticeModal(notice) {
  // Remove existing modal if any
  document.getElementById('noticeModalBackdrop')?.remove();

  const backdrop = document.createElement('div');
  backdrop.id = 'noticeModalBackdrop';
  backdrop.className = 'modal-backdrop';

  const hindiText = notice.hindi_document || `कार्यालय: ${notice.issuing_authority}
संदर्भ संख्या: ${notice.reference_no}
स्थान: ${notice.event_title} (${notice.coordinates})

सर्वसंबंधित को वैधानिक आदेश:
वायुनेत्र स्वायत्त वायु गुणवत्ता ग्रिड द्वारा आपके परिसर/कार्यक्षेत्र से अत्यधिक मात्रा में ${notice.peak_pollutant} का गैर-कानूनी उत्सर्जन दर्ज किया गया है।

आदेश निर्देश:
1. उपरोक्त स्थल पर सभी प्रकार के खुले दहन व अनियंत्रित उत्सर्जन को तत्काल प्रभाव से बंद किया जाए।
2. 500 मीटर के दायरे में एंटी-स्मॉग गन व जल छिड़काव दल तत्काल तैनात किया जाए।
3. अगले 24 घंटे के भीतर लिखित अनुपालन रिपोर्ट सक्षम मजिस्ट्रेट के समक्ष प्रस्तुत की जाए।

उल्लंघन की स्थिति में वायु अधिनियम, 1981 की धारा 37 के तहत कानूनी कार्यवाही की जाएगी।`;

  backdrop.innerHTML = `
    <div class="modal-card" style="max-width:820px;">
      <div class="modal-header">
        <div style="display:flex; align-items:center; gap:8px;">
          <h3>📄 Statutory Regulatory Notice — ${notice.reference_no}</h3>
          <span style="background:linear-gradient(135deg,#3b82f6,#8b5cf6); color:white; font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px;">✨ Google Gemini AI</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <div style="display:flex; background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:2px;">
            <button class="btn btn-sm btn-primary" id="btnNoticeLangEn" style="padding:4px 10px; font-size:11px;">English</button>
            <button class="btn btn-sm btn-ghost" id="btnNoticeLangHi" style="padding:4px 10px; font-size:11px; border:none;">हिंदी (Hindi)</button>
          </div>
          <button class="btn btn-ghost btn-sm" id="closeNoticeModalBtn">✕</button>
        </div>
      </div>
      <div class="modal-body" id="noticePrintArea">
        <div id="noticeEnContainer">
          <div style="text-align:center; border-bottom:2px solid #333; padding-bottom:10px; margin-bottom:14px;">
            <div style="font-size:14px; font-weight:800; text-transform:uppercase;">Government Environmental Protection Directorate</div>
            <div style="font-size:13px; font-weight:700; color:#0d9488;">${notice.issuing_authority}</div>
            <div style="font-size:11px; color:#64748b;">Autonomous Enforcement & Environmental Incident Command</div>
          </div>

          <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:12px;">
            <div><strong>Ref:</strong> ${notice.reference_no}</div>
            <div><strong>Date:</strong> ${notice.issued_at}</div>
          </div>

          <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 12px; margin-bottom:12px; font-size:12px;">
            <div><strong>TO:</strong> ${notice.recipient}</div>
            <div><strong>COORDINATES:</strong> ${notice.coordinates} · <strong>SEVERITY:</strong> <span class="pill pill-${notice.severity.toLowerCase()}">${notice.severity}</span></div>
            <div><strong>POLLUTANT:</strong> ${notice.peak_pollutant} (Baseline: ${notice.baseline}, Anomaly: ${notice.anomaly})</div>
          </div>

          ${notice.gemini_reasoning ? `
          <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:8px 12px; margin-bottom:12px; font-size:12px; color:#1e40af;">
            <strong>✨ Google Gemini Statutory Analysis:</strong> ${notice.gemini_reasoning}
          </div>` : ''}

          <div style="font-weight:700; font-size:13px; margin-bottom:6px; text-decoration:underline;">${notice.subject}</div>

          <div style="font-size:12px; font-weight:700; margin:10px 0 4px;">CORROBORATED EVIDENCE DOSSIER:</div>
          <table style="font-size:11px; width:100%; margin-bottom:12px;">
            <thead>
              <tr><th>Source Instrument</th><th>Telemetry & Finding</th></tr>
            </thead>
            <tbody>
              ${notice.evidence_summary.map(e => `<tr><td><strong>${e.source}</strong></td><td>${e.details}</td></tr>`).join('')}
            </tbody>
          </table>

          <div style="font-size:12px; font-weight:700; margin-bottom:4px;">MANDATORY STATUTORY DIRECTIVES:</div>
          <ol style="font-size:12px; padding-left:18px; line-height:1.6; margin-bottom:12px;">
            ${notice.directives.map(d => `<li>${d}</li>`).join('')}
          </ol>

          <div style="border:1px dashed #ef4444; background:#fef2f2; padding:10px; border-radius:8px; font-size:11px; color:#991b1b; margin-bottom:10px;">
            <strong>PENAL CLAUSE:</strong> ${notice.penal_provisions}. Failure to abate violation within ${notice.compliance_deadline_hours} hours will initiate criminal prosecution and environmental compensation penalty.
          </div>
        </div>

        <div id="noticeHiContainer" style="display:none; font-family:'Segoe UI', Tahoma, sans-serif;">
          <div style="text-align:center; border-bottom:2px solid #333; padding-bottom:10px; margin-bottom:14px;">
            <div style="font-size:16px; font-weight:bold; color:#0f172a;">दिल्ली राष्ट्रीय राजधानी क्षेत्र सरकार / राज्य पर्यावरण प्राधिकरण</div>
            <div style="font-size:13px; font-weight:600; color:#0284c7; margin-top:4px;">वायुनेत्र स्वायत्त प्रवर्तन एवं वैधानिक प्रकोष्ठ</div>
            <div style="font-size:11px; color:#64748b;">(वायु (प्रदूषण निवारण एवं नियंत्रण) अधिनियम, 1981 की धारा 31ए के अंतर्गत वैधानिक निर्देश)</div>
          </div>
          <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:16px; font-size:13px; white-space:pre-wrap; line-height:1.8;">${hindiText}</div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-ghost" id="downloadNoticeDocBtn">⬇️ Download HTML Dossier</button>
        <button class="btn btn-primary" id="printNoticeBtn">🖨️ Print / Save PDF</button>
      </div>
    </div>
  `;

  document.body.appendChild(backdrop);

  // Language switchers
  const btnEn = document.getElementById('btnNoticeLangEn');
  const btnHi = document.getElementById('btnNoticeLangHi');
  const cEn = document.getElementById('noticeEnContainer');
  const cHi = document.getElementById('noticeHiContainer');

  btnEn.onclick = () => {
    btnEn.className = 'btn btn-sm btn-primary';
    btnHi.className = 'btn btn-sm btn-ghost';
    btnHi.style.border = 'none';
    cEn.style.display = 'block';
    cHi.style.display = 'none';
  };

  btnHi.onclick = () => {
    btnHi.className = 'btn btn-sm btn-primary';
    btnEn.className = 'btn btn-sm btn-ghost';
    btnEn.style.border = 'none';
    cHi.style.display = 'block';
    cEn.style.display = 'none';
  };

  // If authority officer selected Hindi globally, open Hindi notice directly
  if (CURRENT_LANG === 'hi') {
    btnHi.click();
  }

  // Close handler
  document.getElementById('closeNoticeModalBtn').onclick = () => backdrop.remove();
  backdrop.onclick = (e) => { if (e.target === backdrop) backdrop.remove(); };

  // Print handler
  document.getElementById('printNoticeBtn').onclick = () => {
    const printContent = document.getElementById('noticePrintArea').innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
      <head><title>${notice.reference_no}</title>
      <style>body{font-family:'Times New Roman',serif;padding:30px;line-height:1.5;} table{width:100%;border-collapse:collapse;} th,td{border:1px solid #333;padding:6px;text-align:left;font-size:12px;}</style>
      </head>
      <body>${printContent}</body></html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => { printWindow.print(); printWindow.close(); }, 250);
  };

  // Download handler
  document.getElementById('downloadNoticeDocBtn').onclick = () => {
    const blob = new Blob([notice.html_document], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Statutory_Notice_${notice.event_id}.html`;
    a.click();
    URL.revokeObjectURL(url);
    toast('Downloaded', `Notice saved as Statutory_Notice_${notice.event_id}.html`);
  };
}

function toggleAlertsDropdown() {
  const existing = document.getElementById('alertDropdown');
  if (existing) {
    existing.remove();
    return;
  }

  const notifBtn = document.getElementById('notifBtn');
  if (!notifBtn) return;

  const drop = document.createElement('div');
  drop.id = 'alertDropdown';
  drop.className = 'alert-dropdown';
  drop.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid var(--border); padding-bottom:8px;">
      <strong style="font-size:14px;">Operational Alerts (${ALERTS.length})</strong>
      <span style="font-size:11px; color:#0d9488; font-weight:600;">Control Room</span>
    </div>
    <div style="display:flex; flex-direction:column; gap:8px;">
      ${ALERTS.map(a => `
        <div class="alert-item ${a.acknowledged ? '' : 'unread'}">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
            <span class="pill ${a.severity==='CRITICAL'?'pill-critical':'pill-high'}">${a.severity}</span>
            <span style="font-size:10px; color:var(--text-3);">${formatTime(a.created_at)}</span>
          </div>
          <div style="font-size:12.5px; font-weight:600; margin-bottom:3px;">${a.title}</div>
          <div style="font-size:11.5px; color:var(--text-2); margin-bottom:6px;">${a.message}</div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:10px; color:var(--text-3);">${a.authority}</span>
            ${a.acknowledged ? '<span style="font-size:11px; color:#16a34a;">✓ Acked</span>' : `<button class="btn btn-ghost btn-sm" style="padding:2px 8px; font-size:10.5px;" onclick="handleAckAlert('${a.id}')">Acknowledge</button>`}
          </div>
        </div>
      `).join('')}
    </div>
  `;

  notifBtn.parentElement.appendChild(drop);

  // Close on outside click
  const closeHandler = (e) => {
    if (!drop.contains(e.target) && e.target !== notifBtn && !notifBtn.contains(e.target)) {
      drop.remove();
      document.removeEventListener('click', closeHandler);
    }
  };
  setTimeout(() => document.addEventListener('click', closeHandler), 10);
}

async function handleAckAlert(alertId) {
  await VaayuAPI.acknowledgeAlert(alertId);
  toast('Acknowledged', `Alert ${alertId} logged in control room`);
  const drop = document.getElementById('alertDropdown');
  if (drop) {
    drop.remove();
    toggleAlertsDropdown();
  }
}

/* ========== EVENT ACTIONS BINDINGS ========== */
function bindActions() {
  document.querySelectorAll('[data-act]').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.preventDefault();
      const act = btn.dataset.act;
      const tgt = btn.dataset.target || '';

      if (act === 'dispatch') {
        if (tgt === 'form') {
          const eventSelect = document.getElementById('dispatchLinkedEvent');
          const typeSelect = document.getElementById('dispatchActionType');
          const assigneeInput = document.getElementById('dispatchAssignee');
          const notesInput = document.getElementById('dispatchNotes');

          const payload = {
            eventId: eventSelect?.value || 'EVT-2026-0847',
            type: typeSelect?.value || 'FIELD_INSPECTION',
            assignee: assigneeInput?.value.trim() || 'SDM South-East Patrol',
            notes: notesInput?.value.trim() || 'Rapid field inspection and mitigation directive',
          };

          const action = await VaayuAPI.dispatchAction(payload);
          toast('Action dispatched', `${action.type} assigned to ${action.assignee}`);
          router();
        } else {
          const action = await VaayuAPI.dispatchAction({
            eventId: tgt || 'EVT-2026-0847',
            type: 'FIELD_INSPECTION',
            assignee: 'SDM South-East Rapid Unit',
            notes: `Field team dispatch for ${tgt}`,
          });
          toast('Action dispatched', `Field team notified for ${tgt || 'event'}`);
          if (window.location.hash.startsWith('#/event/')) {
            router();
          }
        }
      } else if (act === 'notice') {
        // GENERATE OFFICIAL LEGAL DOCUMENT
        toast('Generating...', `Compiling legal enforcement dossier for ${tgt}...`);
        const notice = await VaayuAPI.generateNotice(tgt || 'EVT-2026-0847');
        if (notice) {
          openNoticeModal(notice);
          toast('Dossier Ready', `Statutory Notice ${notice.reference_no} generated`);
        } else {
          toast('Notice Error', `Could not generate notice for ${tgt}`);
        }
      } else if (act === 'advisory') {
        if (tgt === 'compose') {
          const eventSelect = document.getElementById('advLinkedEvent');
          const audienceInput = document.getElementById('advAudience');
          const msgInput = document.getElementById('advMessage');
          const enCheck = document.getElementById('advLangEn');
          const hiCheck = document.getElementById('advLangHi');
          const smsCheck = document.getElementById('advChanSms');
          const ivrCheck = document.getElementById('advChanIvr');
          const appCheck = document.getElementById('advChanApp');

          const langs = [];
          if (enCheck?.checked) langs.push('EN');
          if (hiCheck?.checked) langs.push('HI');

          const channels = [];
          if (smsCheck?.checked) channels.push('SMS');
          if (ivrCheck?.checked) channels.push('IVR');
          if (appCheck?.checked) channels.push('App');

          const payload = {
            eventId: eventSelect?.value || 'EVT-2026-0847',
            title: `Public health notice — ${eventSelect?.value || CURRENT_CITY}`,
            audience: audienceInput?.value.trim() || 'Residents within 2 km',
            languages: langs.length ? langs : ['EN', 'HI'],
            channels: channels.length ? channels : ['SMS', 'IVR', 'App'],
            message: msgInput?.value.trim() || 'Air quality is poor. Wear protective mask.',
          };

          const adv = await VaayuAPI.createAdvisory(payload);
          toast('Advisory broadcast', `Sent across ${adv.channels.join(', ')} (${adv.languages.join(' + ')})`);
          router();
        } else if (tgt.startsWith('ADV-')) {
          await VaayuAPI.sendAdvisory(tgt);
          toast('Advisory sent', `Broadcast confirmed for ${tgt}`);
          router();
        }
      } else if (act === 'apply') {
        // APPLY FILTERS AND RE-RENDER
        applyActiveFilters();
      } else if (act === 'refresh') {
        toast('Refreshing...', 'Syncing with FastAPI environmental engine');
        await VaayuAPI.syncWithBackend();
        toast('Synced', 'Latest events, actions, and forecasts loaded');
        router();
      }
    });
  });
}

/* ========== FILTER APPLICATION ENGINE ========== */
function applyActiveFilters() {
  // 1. If on Dashboard view: read view-options panel
  const dashPm25 = document.getElementById('dashOptPm25');
  const dashPm10 = document.getElementById('dashOptPm10');
  const dashO3 = document.getElementById('dashOptO3');
  const dashNo2 = document.getElementById('dashOptNo2');
  const dashAqiColor = document.getElementById('dashOptAqiColor');

  if (dashPm25 && dashPm10) {
    ACTIVE_FILTERS.pollutants['PM2.5'] = dashPm25.checked;
    ACTIVE_FILTERS.pollutants['PM10'] = dashPm10.checked;
    ACTIVE_FILTERS.pollutants['O3'] = dashO3.checked;
    ACTIVE_FILTERS.pollutants['NO2'] = dashNo2.checked;
    ACTIVE_FILTERS.aqiColorArea = dashAqiColor.checked;

    // Toggle map bubbles visibility
    const bO3 = document.getElementById('bubbleO3');
    const bNo2 = document.getElementById('bubbleNo2');
    const bPm10 = document.getElementById('bubblePm10');
    const bPm25 = document.getElementById('bubblePm25');

    if (bO3) bO3.style.display = dashO3.checked ? 'flex' : 'none';
    if (bNo2) bNo2.style.display = dashNo2.checked ? 'flex' : 'none';
    if (bPm10) bPm10.style.display = dashPm10.checked ? 'flex' : 'none';
    if (bPm25) bPm25.style.display = dashPm25.checked ? 'flex' : 'none';

    // Toggle AQI glow circle
    if (layerGroups.glow) {
      if (dashAqiColor.checked) {
        if (!map.hasLayer(layerGroups.glow)) layerGroups.glow.addTo(map);
      } else {
        if (map.hasLayer(layerGroups.glow)) map.removeLayer(layerGroups.glow);
      }
    }

    toast('View Options Applied', `Active: ${Object.keys(ACTIVE_FILTERS.pollutants).filter(k => ACTIVE_FILTERS.pollutants[k]).join(', ')}`);
    return;
  }

  // 2. If on Air Maps view: read side-filters panel
  const filterChecks = {
    'PM2.5': document.getElementById('filtPm25')?.checked ?? true,
    'PM10': document.getElementById('filtPm10')?.checked ?? true,
    'O3': document.getElementById('filtO3')?.checked ?? false,
    'NO2': document.getElementById('filtNo2')?.checked ?? false,
    'SO2': document.getElementById('filtSo2')?.checked ?? false,
  };
  ACTIVE_FILTERS.pollutants = filterChecks;

  ACTIVE_FILTERS.statuses = {
    'ACTIVE': document.getElementById('filtActive')?.checked ?? true,
    'CANDIDATE': document.getElementById('filtCandidate')?.checked ?? true,
    'RESOLVED': document.getElementById('filtResolved')?.checked ?? false,
  };

  ACTIVE_FILTERS.layers = {
    'footprints': document.getElementById('layerFootprints')?.checked ?? true,
    'sensors': document.getElementById('layerSensors')?.checked ?? true,
    'plumes': document.getElementById('layerPlumes')?.checked ?? true,
    'hotspots': document.getElementById('layerHotspots')?.checked ?? false,
    'receptors': document.getElementById('layerReceptors')?.checked ?? true,
  };

  // Visibly re-render air map layers
  renderAirMapLayers();
  toast('Map Layers Updated', 'Active filter rules applied to Leaflet canvas');
}

/* ========== DASHBOARD VIEW ========== */
function viewDashboard() {
  const reg = getRegion(CURRENT_CITY);
  const bd = _bubbleData(reg);
  return `
  <div class="page" style="height:calc(100vh - 64px); display:flex; flex-direction:column; padding-bottom:16px;">
    <!-- Regional Quick Switch Bar -->
    <div class="region-bar">
      <span class="region-label">${t('region_label')}</span>
      ${REGIONS.map(r => `
        <button class="region-pill ${r.name === CURRENT_CITY ? 'active' : ''}" data-city="${r.name}" onclick="switchRegion('${r.name}')">
          ${r.name}
        </button>
      `).join('')}
    </div>

    <div class="dash-layout" style="flex:1;">
      <!-- MAP with floating metric bubbles -->
      <div class="map-section">
        <div id="mainMap" class="map-el"></div>

        <!-- Mobile Filter Toggle Button -->
        <button class="mobile-filter-fab btn btn-sm btn-primary" id="mobileFilterFab" onclick="toggleMobileViewOptions()">
          ${t('layers_filters_btn')}
        </button>

        <!-- View Options panel -->
        <div class="view-options" id="dashViewOptions">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h4 style="margin:0;">${t('view_options')}</h4>
            <button class="view-options-close" onclick="toggleMobileViewOptions()" title="Close layers">✕</button>
          </div>
          <div class="opt"><span>${t('pollutant')}</span></div>
          <div class="opt"><span>PM2.5</span><input type="checkbox" id="dashOptPm25" checked></div>
          <div class="opt"><span>PM10</span><input type="checkbox" id="dashOptPm10" checked></div>
          <div class="opt"><span>O₃</span><input type="checkbox" id="dashOptO3"></div>
          <div class="opt"><span>NO₂</span><input type="checkbox" id="dashOptNo2"></div>
          <div class="opt"><span>${t('aqi_color_area')}</span><input type="checkbox" id="dashOptAqiColor" checked></div>
          <div class="actions">
            <button class="btn btn-ghost btn-sm" onclick="toggleMobileViewOptions()">${t('close')}</button>
            <button class="btn btn-primary btn-sm" data-act="apply">${t('apply')}</button>
          </div>
        </div>

        <!-- Metric bubbles positioned over map -->
        <div class="bubble" id="bubbleO3" style="top:18%; left:22%; display:${ACTIVE_FILTERS.pollutants['O3'] ? 'flex' : 'none'};">
          <div class="pct">${bd['O3'].label} ${bd['O3'].pct}%</div>
          <div class="val">${bd['O3'].val}</div>
          <div class="unit">µg/m³</div>
        </div>
        <div class="bubble" id="bubbleNo2" style="top:12%; left:48%; display:${ACTIVE_FILTERS.pollutants['NO2'] ? 'flex' : 'none'};">
          <div class="pct">${bd['NO2'].label} ${bd['NO2'].pct}%</div>
          <div class="val">${bd['NO2'].val}</div>
          <div class="unit">µg/m³</div>
        </div>
        <div class="bubble" id="bubblePm10" style="top:42%; left:38%; display:${ACTIVE_FILTERS.pollutants['PM10'] ? 'flex' : 'none'};">
          <div class="pct">${bd['PM10'].label} ${bd['PM10'].pct}%</div>
          <div class="val">${bd['PM10'].val}</div>
          <div class="unit">µg/m³</div>
        </div>
        <div class="bubble" id="bubblePm25" style="top:28%; left:62%; display:${ACTIVE_FILTERS.pollutants['PM2.5'] ? 'flex' : 'none'};">
          <div class="pct" style="color:#ef4444">${bd['PM2.5'].label} ${bd['PM2.5'].pct}%</div>
          <div class="val" style="color:#ef4444">${bd['PM2.5'].val}</div>
          <div class="unit">µg/m³</div>
        </div>
      </div>

      <!-- Bottom panel: AQI gauge + Forecast chart -->
      <div class="bottom-panel">
        <div class="aqi-card">
          <div class="city">${reg.name}</div>
          <div class="country">🇮🇳 India · <span style="color:#0d9488">${reg.state}</span></div>
          <div class="aqi-ring">
            <div class="aqi-inner">
              <div class="aqi-num">${reg.current_aqi}</div>
              <div class="aqi-lbl">AQI</div>
            </div>
          </div>
          <div class="aqi-status">⚠ ${reg.status}</div>
          <div style="font-size:11px; color:var(--text-3); margin-top:6px;">${reg.weather_desc}</div>
        </div>

        <div class="forecast-card">
          <div class="head">
            <h3>Air Quality Forecast — ${CURRENT_CITY}</h3>
            <div class="tabs">
              <button class="tab active">Hourly</button>
              <button class="tab" onclick="toast('Forecast', 'Daily trend active')">Daily</button>
              <button class="tab" onclick="toast('Forecast', 'Monthly trend active')">Monthly</button>
            </div>
          </div>
          <div class="chart-box"><canvas id="dashChart"></canvas></div>
        </div>
      </div>
    </div>
  </div>`;
}

function initMainMap(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  const reg = getRegion(CURRENT_CITY);
  map = L.map(elId, { zoomControl: true }).setView([reg.lat, reg.lng], 11);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);

  // Soft green glow layer
  layerGroups.glow = L.layerGroup([
    L.circle([reg.lat, reg.lng], { radius: 12000, color: 'transparent', fillColor: '#14b8a6', fillOpacity: 0.12 }),
    L.circle([reg.lat, reg.lng], { radius: 7000, color: 'transparent', fillColor: '#14b8a6', fillOpacity: 0.15 }),
    L.circle([reg.lat - 0.05, reg.lng + 0.06], { radius: 4000, color: 'transparent', fillColor: '#f97316', fillOpacity: 0.18 }),
  ]).addTo(map);

  // Render events matching region
  EVENTS.forEach(e => {
    const color = e.severity === 'critical' ? '#ef4444' : e.severity === 'high' ? '#f97316' : '#eab308';
    L.circle([e.lat, e.lng], {
      radius: e.severity === 'critical' ? 1600 : 1000,
      color,
      fillColor: color,
      fillOpacity: 0.25,
      weight: 2
    }).addTo(map).bindPopup(`
      <strong>${e.id}</strong><br>${e.title}<br>
      <div style="margin-top:4px;"><a href="#/event/${e.id}" style="color:#0d9488;font-weight:700;">Open event dossier →</a></div>
    `);
    L.circleMarker([e.lat, e.lng], { radius: 7, color: '#fff', fillColor: color, fillOpacity: 1, weight: 2 }).addTo(map);
  });

  // Center pin
  L.circleMarker([reg.lat, reg.lng], { radius: 8, color: '#fff', fillColor: '#14b8a6', fillOpacity: 1, weight: 3 }).addTo(map);
}

function initForecastChart(id) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  charts[id] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: HOURLY.map(d => d.t),
      datasets: [{
        label: 'AQI',
        data: HOURLY.map(d => d.aqi),
        borderColor: '#14b8a6',
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return 'rgba(20,184,166,0.15)';
          const g = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          g.addColorStop(0, 'rgba(20,184,166,0.25)');
          g.addColorStop(1, 'rgba(20,184,166,0)');
          return g;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        borderWidth: 2.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
      scales: {
        x: { grid: { color: 'rgba(148,163,184,0.12)', drawBorder: false }, ticks: { color: '#94a3b8', font: { size: 11 }, maxTicksLimit: 8 } },
        y: { grid: { color: 'rgba(148,163,184,0.12)', drawBorder: false }, ticks: { color: '#94a3b8', font: { size: 11 } } }
      }
    }
  });
}

/* ========== AIR MAPS VIEW ========== */
function viewMap() {
  return `
  <div class="page" style="height:calc(100vh - 64px); display:flex; flex-direction:column;">
    <div class="page-header" style="margin-bottom:10px;">
      <div>
        <h1 class="page-title">Air Maps — Multi-Source Environmental GIS</h1>
        <p class="page-sub">Interactive spatial alignment · active plumes · sensors · FIRMS hotspots · receptors</p>
      </div>
      <div class="flex gap-2">
        <span id="mapLayersBadge" class="pill pill-active" style="align-self:center; font-size:12px; padding:4px 12px;">Active Filters Applied</span>
        <button class="btn btn-primary" data-act="refresh">Live refresh</button>
      </div>
    </div>

    <!-- Region selector bar inside Air Maps -->
    <div class="region-bar" style="margin-bottom:10px;">
      <span class="region-label">📍 REGION:</span>
      ${REGIONS.map(r => `
        <button class="region-pill ${r.name === CURRENT_CITY ? 'active' : ''}" data-city="${r.name}" onclick="switchRegion('${r.name}')">
          ${r.name}
        </button>
      `).join('')}
    </div>

    <div class="split" style="flex:1; min-height:0;">
      <div class="side-filters">
        <div class="filter-title">Pollutants</div>
        <label class="filter-check"><input type="checkbox" id="filtPm25" ${ACTIVE_FILTERS.pollutants['PM2.5'] ? 'checked' : ''}> PM2.5</label>
        <label class="filter-check"><input type="checkbox" id="filtPm10" ${ACTIVE_FILTERS.pollutants['PM10'] ? 'checked' : ''}> PM10</label>
        <label class="filter-check"><input type="checkbox" id="filtO3" ${ACTIVE_FILTERS.pollutants['O3'] ? 'checked' : ''}> O₃</label>
        <label class="filter-check"><input type="checkbox" id="filtNo2" ${ACTIVE_FILTERS.pollutants['NO2'] ? 'checked' : ''}> NO₂</label>
        <label class="filter-check"><input type="checkbox" id="filtSo2" ${ACTIVE_FILTERS.pollutants['SO2'] ? 'checked' : ''}> SO₂</label>

        <div class="filter-title">Event Status</div>
        <label class="filter-check"><input type="checkbox" id="filtActive" ${ACTIVE_FILTERS.statuses['ACTIVE'] ? 'checked' : ''}> Active</label>
        <label class="filter-check"><input type="checkbox" id="filtCandidate" ${ACTIVE_FILTERS.statuses['CANDIDATE'] ? 'checked' : ''}> Candidate</label>
        <label class="filter-check"><input type="checkbox" id="filtResolved" ${ACTIVE_FILTERS.statuses['RESOLVED'] ? 'checked' : ''}> Resolved</label>

        <div class="filter-title">GIS Layers</div>
        <label class="filter-check"><input type="checkbox" id="layerFootprints" ${ACTIVE_FILTERS.layers['footprints'] ? 'checked' : ''}> Event Footprints</label>
        <label class="filter-check"><input type="checkbox" id="layerSensors" ${ACTIVE_FILTERS.layers['sensors'] ? 'checked' : ''}> CAAQMS Sensors</label>
        <label class="filter-check"><input type="checkbox" id="layerPlumes" ${ACTIVE_FILTERS.layers['plumes'] ? 'checked' : ''}> Wind Plumes</label>
        <label class="filter-check"><input type="checkbox" id="layerHotspots" ${ACTIVE_FILTERS.layers['hotspots'] ? 'checked' : ''}> FIRMS Hotspots</label>
        <label class="filter-check"><input type="checkbox" id="layerReceptors" ${ACTIVE_FILTERS.layers['receptors'] ? 'checked' : ''}> Sensitive Receptors</label>

        <button class="btn btn-primary" style="width:100%; margin-top:16px;" data-act="apply">Apply Filters</button>
      </div>

      <div class="map-section" style="min-height:0; height:100%;">
        <div id="fullMap" class="map-el" style="height:100%; min-height:400px;"></div>
      </div>
    </div>
  </div>`;
}

function initAirMap(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  const reg = getRegion(CURRENT_CITY);
  map = L.map(elId, { zoomControl: true }).setView([reg.lat, reg.lng], 11);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);

  renderAirMapLayers();
}

function renderAirMapLayers() {
  if (!map) return;

  // Clear existing layer groups
  Object.values(layerGroups).forEach(lg => {
    if (lg && map.hasLayer(lg)) map.removeLayer(lg);
  });

  const reg = getRegion(CURRENT_CITY);
  let eventCount = 0;
  let sensorCount = 0;
  let receptorCount = 0;

  // 1. Event Footprints Layer
  if (ACTIVE_FILTERS.layers.footprints) {
    const footprintMarkers = [];
    EVENTS.forEach(e => {
      // Filter by status & pollutant (CORROBORATED events count as active-filtered)
      const statusKey = ACTIVE_FILTERS.statuses[e.status] !== undefined
        ? e.status
        : (e.status === 'CORROBORATED' ? 'ACTIVE' : 'CANDIDATE');
      if (!ACTIVE_FILTERS.statuses[statusKey]) return;
      if (!ACTIVE_FILTERS.pollutants[e.pollutant]) return;

      eventCount++;
      const color = e.severity === 'critical' ? '#ef4444' : e.severity === 'high' ? '#f97316' : '#eab308';
      const c = L.circle([e.lat, e.lng], {
        radius: e.severity === 'critical' ? 1800 : 1200,
        color,
        fillColor: color,
        fillOpacity: 0.28,
        weight: 2
      }).bindPopup(`
        <strong>${e.id}</strong> — <span class="pill pill-${e.severity}">${e.severity}</span><br>
        <b>${e.title}</b><br>
        Peak: ${e.pollutant} ${e.peakValue} ${e.unit}<br>
        Priority: <b>${e.priority}</b><br>
        <div style="margin-top:6px;"><a href="#/event/${e.id}" style="color:#0d9488;font-weight:700;">Open Event Dossier →</a></div>
      `);
      const pt = L.circleMarker([e.lat, e.lng], { radius: 7, color: '#fff', fillColor: color, fillOpacity: 1, weight: 2 });
      footprintMarkers.push(c, pt);
    });
    layerGroups.footprints = L.layerGroup(footprintMarkers).addTo(map);
  }

  // 2. Sensors Layer (readings derived from live region metrics)
  if (ACTIVE_FILTERS.layers.sensors) {
    const m = (reg && reg.metrics && Object.keys(reg.metrics).length) ? reg.metrics : { 'PM2.5': 108 };
    const basePm = m['PM2.5'] || 108;
    const baseAqi = reg.current_aqi || 186;
    const sensorList = [
      { name: `${reg.name} Central CAAQMS`, lat: reg.lat, lon: reg.lng, pm25: basePm, aqi: baseAqi },
      { name: `${reg.name} North IoT Node`, lat: reg.lat + 0.04, lon: reg.lng + 0.02, pm25: Math.round(basePm * 1.25), aqi: Math.round(baseAqi * 1.18) },
      { name: `${reg.name} South Industrial CAAQMS`, lat: reg.lat - 0.05, lon: reg.lng - 0.03, pm25: Math.round(basePm * 1.38), aqi: Math.round(baseAqi * 1.32) },
      { name: `${reg.name} Corridor Transit Node`, lat: reg.lat + 0.02, lon: reg.lng - 0.04, pm25: Math.round(basePm * 0.77), aqi: Math.round(baseAqi * 0.86) },
    ];
    sensorCount = sensorList.length;
    const sensorMarkers = sensorList.map(s => {
      return L.circleMarker([s.lat, s.lon], {
        radius: 6,
        color: '#0d9488',
        fillColor: '#2dd4bf',
        fillOpacity: 0.9,
        weight: 2
      }).bindPopup(`
        <strong>📡 ${s.name}</strong><br>
        PM2.5: <b>${s.pm25} µg/m³</b> · AQI: <b>${s.aqi}</b><br>
        <span style="font-size:10.5px; color:#64748b;">Quality: Verified Good</span>
      `);
    });
    layerGroups.sensors = L.layerGroup(sensorMarkers).addTo(map);
  }

  // 3. Plumes Layer (Downwind Dispersion Polygons)
  if (ACTIVE_FILTERS.layers.plumes) {
    const plumePolygons = [];
    EVENTS.filter(e => e.status !== 'RESOLVED').forEach(e => {
      // Create downwind plume polygon
      const coords = [
        [e.lat, e.lng],
        [e.lat - 0.015, e.lng + 0.03],
        [e.lat - 0.02, e.lng + 0.05],
        [e.lat - 0.035, e.lng + 0.035],
        [e.lat, e.lng]
      ];
      const poly = L.polygon(coords, {
        color: '#ef4444',
        fillColor: '#ef4444',
        fillOpacity: 0.22,
        weight: 1.5,
        dashArray: '4, 4'
      }).bindPopup(`
        <strong>Downwind Plume Horizon (+3h)</strong><br>
        Incident: ${e.id}<br>
        Wind Advection: WNW 4.2 m/s<br>
        Population in Plume: <b>${e.exposure?.population?.toLocaleString() || '35,000'}</b>
      `);
      plumePolygons.push(poly);
    });
    layerGroups.plumes = L.layerGroup(plumePolygons).addTo(map);
  }

  // 4. FIRMS Hotspots Layer
  if (ACTIVE_FILTERS.layers.hotspots) {
    const hotspotMarkers = [
      L.marker([reg.lat + 0.03, reg.lng + 0.05], {
        title: 'NASA FIRMS Hotspot'
      }).bindPopup('<strong>🔥 NASA FIRMS VIIRS Hotspot</strong><br>Brightness Temp: 341.2 K<br>FRP: 24.8 MW'),
    ];
    layerGroups.hotspots = L.layerGroup(hotspotMarkers).addTo(map);
  }

  // 5. Sensitive Receptors Layer
  if (ACTIVE_FILTERS.layers.receptors) {
    const receptorList = [
      { name: 'St. Xavier Senior Secondary School', type: 'school', lat: reg.lat + 0.015, lng: reg.lng + 0.02 },
      { name: 'Max Super Speciality Hospital', type: 'hospital', lat: reg.lat - 0.02, lng: reg.lng + 0.03 },
      { name: 'Bal Bhavan Primary School', type: 'school', lat: reg.lat - 0.01, lng: reg.lng - 0.02 },
      { name: 'Community Child Care Welfare Centre', type: 'care_home', lat: reg.lat + 0.025, lng: reg.lng - 0.015 },
    ];
    receptorCount = receptorList.length;
    const receptorMarkers = receptorList.map(r => {
      const color = r.type === 'hospital' ? '#dc2626' : '#2563eb';
      return L.circleMarker([r.lat, r.lng], {
        radius: 6,
        color: '#fff',
        fillColor: color,
        fillOpacity: 1,
        weight: 2
      }).bindPopup(`
        <strong>${r.type === 'hospital' ? '🏥' : '🏫'} ${r.name}</strong><br>
        Type: ${r.type.toUpperCase()}<br>
        Plume Arrival ETA: <b>~25 minutes</b>
      `);
    });
    layerGroups.receptors = L.layerGroup(receptorMarkers).addTo(map);
  }

  // Update badge
  const badge = document.getElementById('mapLayersBadge');
  if (badge) {
    badge.textContent = `Showing ${eventCount} Events · ${sensorCount} Sensors · ${receptorCount} Receptors`;
  }
}

/* ========== EVENTS LIST VIEW ========== */
function viewEvents() {
  const activeCount = EVENTS.filter(e => e.status === 'ACTIVE').length;
  const criticalCount = EVENTS.filter(e => e.severity === 'critical' && e.status !== 'RESOLVED').length;
  const totalPop = EVENTS.reduce((acc, e) => acc + (e.exposure?.population || 0), 0);

  return `
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Environmental Events</h1>
        <p class="page-sub">Event-centric priority queue · multi-source evidence corroboration</p>
      </div>
      <button class="btn btn-ghost" data-act="refresh">Refresh</button>
    </div>

    <!-- Region selector bar inside Events view -->
    <div class="region-bar">
      <span class="region-label">📍 REGION:</span>
      ${REGIONS.map(r => `
        <button class="region-pill ${r.name === CURRENT_CITY ? 'active' : ''}" data-city="${r.name}" onclick="switchRegion('${r.name}'); router();">
          ${r.name}
        </button>
      `).join('')}
    </div>

    <div class="kpi-row">
      <div class="kpi"><div class="label">Active Events</div><div class="value" style="color:#0d9488">${activeCount}</div></div>
      <div class="kpi"><div class="label">Critical</div><div class="value" style="color:#ef4444">${criticalCount}</div></div>
      <div class="kpi"><div class="label">Population at risk</div><div class="value" style="color:#f97316">${(totalPop / 1000).toFixed(1)}k</div></div>
      <div class="kpi"><div class="label">Avg response</div><div class="value">18 min</div></div>
    </div>
    <div class="event-list">
      ${EVENTS.map(e => `
        <a href="#/event/${e.id}" class="event-row">
          <div class="sev-bar sev-${e.severity}"></div>
          <div class="event-info">
            <h4>${e.title}</h4>
            <div class="event-meta">
              <span class="pill ${sevPill(e.severity)}">${e.severity}</span>
              <span class="pill ${statusPill(e.status)}">${e.status}</span>
              <span>📍 ${e.city || 'Delhi NCR'}</span>
              <span>${e.pollutant} ${e.peakValue} ${e.unit}</span>
              <span>Priority <b>${e.priority}</b></span>
              <span>${formatTime(e.detectedAt)}</span>
            </div>
          </div>
          <span style="color:var(--primary);font-weight:600;font-size:13px">Open Dossier →</span>
        </a>
      `).join('')}
    </div>
  </div>`;
}

/* ========== EVENT DETAIL VIEW ========== */
function viewEvent(id) {
  const e = getEvent(id);
  if (!e) return `<div class="page"><p>Event not found.</p><a href="#/events" class="btn btn-primary">Back</a></div>`;

  return `
  <div class="page">
    <div class="page-header">
      <div>
        <div class="flex gap-2" style="margin-bottom:8px">
          <a href="#/events" class="btn btn-ghost btn-sm">← Events</a>
          <span class="pill ${statusPill(e.status)}">${e.status}</span>
          <span class="pill ${sevPill(e.severity)}">${e.severity}</span>
          <span class="pill pill-candidate">📍 ${e.city || 'Delhi NCR'}</span>
        </div>
        <h1 class="page-title">${e.title}</h1>
        <p class="page-sub">${e.id} · Detected ${formatTime(e.detectedAt)} · Confidence ${Math.round(e.confidence*100)}%</p>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-ghost" data-act="notice" data-target="${e.id}">📄 Draft notice</button>
        <button class="btn btn-primary" data-act="dispatch" data-target="${e.id}">🚀 Dispatch</button>
      </div>
    </div>

    <div class="kpi-row">
      <div class="kpi"><div class="label">Priority</div><div class="value" style="color:#ef4444">${e.priority}</div></div>
      <div class="kpi"><div class="label">Peak ${e.pollutant}</div><div class="value" style="color:#f97316">${e.peakValue}</div><div class="meta">baseline ${e.baseline}</div></div>
      <div class="kpi"><div class="label">Anomaly</div><div class="value">${e.anomalyScore}σ</div></div>
      <div class="kpi"><div class="label">Population</div><div class="value">${((e.exposure?.population || 0)/1000).toFixed(1)}k</div></div>
      <div class="kpi"><div class="label">Schools / Hospitals</div><div class="value">${e.exposure?.schools || 0} / ${e.exposure?.hospitals || 0}</div></div>
    </div>

    <div class="detail-grid">
      <div>
        <div class="card mb-3">
          <div class="card-title">Evidence lineage</div>
          ${(e.evidence || []).map(ev => `
            <div class="evidence-item">
              <div class="evidence-icon">${ev.type==='sensor'?'📡':ev.type==='citizen'?'📷':ev.type==='cv'?'👁️':ev.type==='firms'?'🔥':'🌬️'}</div>
              <div>
                <div class="text-sm" style="font-weight:600">${ev.label}</div>
                <div class="text-sm text-muted">${ev.detail}</div>
                <div class="text-sm text-muted" style="font-size:11px;margin-top:2px">${ev.time}</div>
              </div>
            </div>
          `).join('')}
        </div>

        <div class="card mb-3">
          <div class="card-title">Source hypothesis</div>
          ${(e.sourceHypotheses || []).map(s => `
            <div class="source-row">
              <span>${s.category.replace(/_/g,' ')}</span>
              <div class="bar-bg"><div class="bar-fill" style="width:${s.prob*100}%"></div></div>
              <strong>${Math.round(s.prob*100)}%</strong>
            </div>
          `).join('')}
          <p class="text-sm text-muted mt-2">Probabilistic & evidence-backed. Not definitive attribution.</p>
        </div>

        <div class="card">
          <div class="card-title">Recommended action & Regulatory Directives</div>
          <p class="text-sm" style="line-height:1.55;margin-bottom:12px">${e.recommendedAction}</p>
          <div class="flex gap-2">
            <button class="btn btn-primary btn-sm" data-act="dispatch" data-target="${e.id}">Accept & dispatch</button>
            <button class="btn btn-ghost btn-sm" data-act="notice" data-target="${e.id}">Generate notice PDF</button>
          </div>
        </div>
      </div>

      <div>
        <div class="card mb-3" style="padding:0;overflow:hidden">
          <div id="eventMap" style="height:200px"></div>
        </div>
        ${(e.forecast && e.forecast.length) ? `
        <div class="card mb-3">
          <div class="card-title">Propagation forecast (+1–6 h)</div>
          <div style="height:160px"><canvas id="eventChart"></canvas></div>
        </div>` : ''}
        <div class="card">
          <div class="card-title">Timeline</div>
          <div class="timeline">
            ${(e.timeline || []).map(t => `
              <div class="tl-item">
                <div class="tl-time">${t.time}</div>
                <div class="tl-text">${t.text}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

function initEventMap(id) {
  const e = getEvent(id);
  if (!e) return;
  map = L.map('eventMap', { zoomControl: false, attributionControl: false }).setView([e.lat, e.lng], 13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors', maxZoom: 19 }).addTo(map);
  const color = e.severity === 'critical' ? '#ef4444' : e.severity === 'high' ? '#f97316' : '#eab308';
  L.circle([e.lat, e.lng], { radius: 1400, color, fillColor: color, fillOpacity: 0.28, weight: 2 }).addTo(map);
  L.circleMarker([e.lat, e.lng], { radius: 8, color: '#fff', fillColor: color, fillOpacity: 1, weight: 2 }).addTo(map);
}

function initEventChart(id) {
  const e = getEvent(id);
  if (!e || !e.forecast || !e.forecast.length) return;
  const ctx = document.getElementById('eventChart');
  if (!ctx) return;
  charts.event = new Chart(ctx, {
    type: 'line',
    data: {
      labels: e.forecast.map(f => `+${f.hour}h`),
      datasets: [{
        data: e.forecast.map(f => f.pm25),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.1)',
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(148,163,184,0.1)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(148,163,184,0.1)' }, ticks: { color: '#94a3b8' } }
      }
    }
  });
}

/* ========== FORECAST VIEW ========== */
function viewForecast() {
  return `
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Air Quality Forecast — All India Coverage</h1>
        <p class="page-sub">Diurnal meteorological modeling · multi-region India trajectories · event propagation</p>
      </div>
    </div>

    <!-- Region selector pills inside Forecast -->
    <div class="region-bar">
      <span class="region-label">SELECT CITY:</span>
      ${REGIONS.map(r => `
        <button class="region-pill ${r.name === CURRENT_CITY ? 'active' : ''}" data-city="${r.name}" onclick="switchRegion('${r.name}')">
          ${r.name} (${r.current_aqi})
        </button>
      `).join('')}
    </div>

    <div class="card mb-3">
      <div class="head" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <h3 style="font-size:15px;font-weight:600">${CURRENT_CITY} AQI Trajectory (24-Hour Forecast)</h3>
        <div class="tabs">
          <button class="tab active">Hourly</button>
          <button class="tab" onclick="toast('Forecast', 'Daily aggregate forecast')">Daily</button>
        </div>
      </div>
      <div style="height:240px"><canvas id="fullChart"></canvas></div>
    </div>

    <div class="card">
      <div class="card-title">Active event propagation across India</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Event</th><th>City / Region</th><th>+1h</th><th>+3h</th><th>+6h</th><th></th></tr></thead>
          <tbody>
            ${EVENTS.filter(e => e.forecast && e.forecast.length).map(e => `
              <tr>
                <td><code style="color:#0d9488">${e.id}</code><br><span class="text-sm text-muted">${e.title.slice(0,38)}…</span></td>
                <td><span class="pill pill-candidate">${e.city || 'Delhi NCR'}</span></td>
                <td><b>${e.forecast[0]?.pm25 ?? '—'}</b> µg/m³</td>
                <td><b>${e.forecast[2]?.pm25 ?? '—'}</b> µg/m³</td>
                <td><b>${e.forecast[5]?.pm25 ?? e.forecast.at(-1)?.pm25 ?? '—'}</b> µg/m³</td>
                <td><a href="#/event/${e.id}" class="btn btn-ghost btn-sm">Detail</a></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  </div>`;
}

/* ========== ACTIONS VIEW ========== */
function viewActions() {
  return `
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Authority Actions</h1>
        <p class="page-sub">Dispatch, notices, field inspections, anti-smog deployments</p>
      </div>
      <button class="btn btn-primary" data-act="dispatch" data-target="new" onclick="document.getElementById('dispatchAssignee')?.focus()">+ New action</button>
    </div>
    <div class="table-wrap mb-3">
      <table>
        <thead>
          <tr><th>ID</th><th>Event</th><th>Type</th><th>Assignee</th><th>Status</th><th>Created</th><th>ETA</th></tr>
        </thead>
        <tbody>
          ${ACTIONS.map(a => `
            <tr>
              <td><code style="color:#0d9488">${a.id}</code></td>
              <td><a href="#/event/${a.eventId}" style="color:#0d9488">${a.eventId}</a></td>
              <td>${a.type.replace(/_/g,' ')}</td>
              <td>${a.assignee}</td>
              <td><span class="pill ${a.status==='DISPATCHED'?'pill-active':a.status==='IN_PROGRESS'?'pill-high':'pill-candidate'}">${a.status}</span></td>
              <td class="text-sm text-muted">${formatTime(a.createdAt)}</td>
              <td>${a.eta || '—'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Quick dispatch</div>
        <label class="form-label">Linked event</label>
        <select class="form-select" id="dispatchLinkedEvent">
          ${EVENTS.filter(e => e.status !== 'RESOLVED').map(e => `<option value="${e.id}">${e.id} — ${e.title.slice(0,36)}</option>`).join('')}
        </select>
        <label class="form-label">Action type</label>
        <select class="form-select" id="dispatchActionType">
          <option value="FIELD_INSPECTION">FIELD_INSPECTION</option>
          <option value="NOTICE_DRAFT">NOTICE_DRAFT</option>
          <option value="DUST_SUPPRESSION">DUST_SUPPRESSION</option>
          <option value="FIRE_SERVICE_ALERT">FIRE_SERVICE_ALERT</option>
          <option value="PUBLIC_ADVISORY">PUBLIC_ADVISORY</option>
        </select>
        <label class="form-label">Assignee</label>
        <input class="form-input" id="dispatchAssignee" placeholder="e.g. SDM South-East Patrol" />
        <label class="form-label">Notes</label>
        <textarea class="form-textarea" id="dispatchNotes" placeholder="Mitigation instructions, vehicle unit numbers…"></textarea>
        <button class="btn btn-primary" data-act="dispatch" data-target="form">Dispatch</button>
      </div>
      <div class="card">
        <div class="card-title">Routing rules</div>
        <ul class="text-sm text-muted" style="line-height:1.9;padding-left:18px">
          <li><strong style="color:var(--text)">Open burning / Fire</strong> → Fire service + SDM + DPCC</li>
          <li><strong style="color:var(--text)">Construction dust</strong> → MCD + Traffic Police</li>
          <li><strong style="color:var(--text)">Industrial</strong> → DPCC / SPCB Industrial Vigilance</li>
          <li><strong style="color:var(--text)">Road traffic</strong> → Traffic Police + Pollution Cell</li>
          <li><strong style="color:var(--text)">Agricultural burning</strong> → State PCB Rapid Taskforce</li>
        </ul>
      </div>
    </div>
  </div>`;
}

/* ========== ADVISORIES VIEW ========== */
function viewAdvisories() {
  return `
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Public Advisories</h1>
        <p class="page-sub">Multi-language · SMS · IVR · App push broadcasting</p>
      </div>
      <button class="btn btn-primary" data-act="advisory" data-target="new" onclick="document.getElementById('advAudience')?.focus()">+ Compose</button>
    </div>
    <div class="table-wrap mb-3">
      <table>
        <thead>
          <tr><th>ID</th><th>Title</th><th>Event</th><th>Audience</th><th>Lang</th><th>Channels</th><th>Status</th><th></th></tr>
        </thead>
        <tbody>
          ${ADVISORIES.map(a => `
            <tr>
              <td><code style="color:#0d9488">${a.id}</code></td>
              <td>${a.title}</td>
              <td><a href="#/event/${a.eventId}" style="color:#0d9488">${a.eventId}</a></td>
              <td class="text-sm">${a.audience}</td>
              <td>${a.languages.join(', ')}</td>
              <td class="text-sm">${a.channels.join(', ') || '—'}</td>
              <td><span class="pill ${a.status==='SENT'?'pill-active':'pill-candidate'}">${a.status}</span></td>
              <td>
                ${a.status==='DRAFT'
                  ? `<button class="btn btn-primary btn-sm" data-act="advisory" data-target="${a.id}">Send</button>`
                  : `<span class="text-sm text-muted">${formatTime(a.sentAt)}</span>`}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    <div class="card">
      <div class="card-title">Compose advisory</div>
      <div class="grid-2">
        <div>
          <label class="form-label">Linked event</label>
          <select class="form-select" id="advLinkedEvent">
            ${EVENTS.filter(e => e.status !== 'RESOLVED').map(e => `<option value="${e.id}">${e.id}</option>`).join('')}
          </select>
          <label class="form-label">Audience</label>
          <input class="form-input" id="advAudience" value="Residents within 2 km of event" />
          <label class="form-label">Languages</label>
          <div class="flex gap-3">
            <label class="filter-check"><input type="checkbox" id="advLangEn" checked> English</label>
            <label class="filter-check"><input type="checkbox" id="advLangHi" checked> Hindi</label>
          </div>
        </div>
        <div>
          <label class="form-label">Message</label>
          <textarea class="form-textarea" id="advMessage">Air quality in your area is currently poor due to a local pollution event. Sensitive groups should limit outdoor activity.</textarea>
          <label class="form-label">Channels</label>
          <div class="flex gap-3 mb-3">
            <label class="filter-check"><input type="checkbox" id="advChanSms" checked> SMS</label>
            <label class="filter-check"><input type="checkbox" id="advChanIvr" checked> IVR</label>
            <label class="filter-check"><input type="checkbox" id="advChanApp" checked> App push</label>
          </div>
          <button class="btn btn-primary" data-act="advisory" data-target="compose">Send advisory</button>
        </div>
      </div>
    </div>
  </div>`;
}

/* ========== BOOT ========== */
window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', async () => {
  // Global Language Switcher
  document.getElementById('langBtnEn')?.addEventListener('click', () => setLanguage('en'));
  document.getElementById('langBtnHi')?.addEventListener('click', () => setLanguage('hi'));
  setLanguage(CURRENT_LANG, false);

  router();

  // Notification Bell Click -> Open Alerts Dropdown
  document.getElementById('notifBtn')?.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleAlertsDropdown();
  });

  // Search input handler
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.placeholder = 'Search Indian cities (e.g. Mumbai, Bengaluru, Kolkata, Delhi)...';
    const executeSearch = () => {
      const q = searchInput.value.trim();
      if (!q) return;
      const matched = getRegion(q);
      if (matched) {
        switchRegion(matched.name);
      } else {
        toast('Search', `Locating sensor grid & corridors around "${q}"`);
      }
    };

    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') executeSearch();
    });

    document.querySelector('.search-btn')?.addEventListener('click', executeSearch);
  }

  // Background sync with live FastAPI backend
  await VaayuAPI.syncWithBackend();

  // Re-render view with backend state
  const hash = window.location.hash;
  if (!hash || hash === '#/' || hash === '#/dashboard' || hash === '#/events' || hash === '#/map') {
    router();
  }
});
