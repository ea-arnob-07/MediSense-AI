'use strict';

const state = {
  metadata: null,
  symptoms: [],
  selectedSymptoms: {},
  selectedCategory: 'All',
  symptomQuery: '',
  symptomView: 'compact',
  profile: null,
  result: null,
  unlocked: new Set(['welcome']),
  translations: { symptoms: {}, diseases: {}, categories: {}, risk_levels: {}, urgency: {} },
  demoMode: false,
};

const popularNames = ['Fever', 'Cough', 'Fatigue', 'Headache', 'Chest_Pain', 'Shortness_of_Breath', 'Nausea', 'Body_Ache'];
const categoryIcons = ['✦', '◈', '⌁', '◉', '✧', '◇', '⊹', '☼', '⬡', '❖', '△', '○'];
const severityLabels = {
  1: 'Very mild (খুব সামান্য)',
  2: 'Mild (সামান্য)',
  3: 'Moderate (মাঝারি)',
  4: 'Severe (তীব্র)',
  5: 'Critical (অতি তীব্র)',
};
const profileRequiredIds = [
  'age', 'sex', 'smoking_status', 'onset_type',
  'height_feet', 'height_inches', 'weight_kg',
];
const optionalVitalDefaults = {
  temperature_f: 98.6,
  heart_rate_bpm: 80,
  respiratory_rate_bpm: 16,
  spo2_percent: 98,
  systolic_bp: 120,
  diastolic_bp: 80,
  random_glucose_mg_dl: 100,
  pain_score_0_10: 0,
};
const sexBn = { Female: 'নারী', Male: 'পুরুষ', Other: 'অন্যান্য' };
const onsetBn = { Gradual: 'ধীরে ধীরে', Sudden: 'হঠাৎ', Intermittent: 'মাঝে মাঝে' };
const comorbidityBn = {
  Anemia: 'রক্তস্বল্পতা', Asthma: 'হাঁপানি', COPD: 'সিওপিডি', Chronic_Kidney_Disease: 'দীর্ঘমেয়াদি কিডনি রোগ',
  Heart_Disease: 'হৃদরোগ', Hypertension: 'উচ্চ রক্তচাপ', Obesity: 'স্থূলতা', Type_2_Diabetes: 'টাইপ ২ ডায়াবেটিস',
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
const formatName = value => String(value || '').replaceAll('_', ' ');
const escapeHTML = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
const percent = value => `${(Number(value || 0) * 100).toFixed(Number(value || 0) >= .1 ? 1 : 2)}%`;
const bilingual = (english, bangla) => bangla ? `${english} (${bangla})` : english;
const bnSymptom = name => state.translations.symptoms?.[name] || '';
const bnDisease = name => state.translations.diseases?.[name] || '';
const bnCategory = name => state.translations.categories?.[name] || '';
const diseaseLabel = item => bilingual(item?.disease_display || formatName(item?.disease), item?.disease_display_bn || bnDisease(item?.disease));
const symptomLabel = item => bilingual(item?.display || formatName(item?.name || item?.symptom), item?.display_bn || bnSymptom(item?.name || item?.symptom));
const categoryLabel = value => bilingual(formatName(value || 'Other'), bnCategory(value));
const riskLabel = value => bilingual(value || 'Unknown', state.translations.risk_levels?.[value] || 'অজানা');
const urgencyLabel = value => bilingual(value || 'Review required', state.translations.urgency?.[value] || 'চিকিৎসকের পরামর্শ নিন');
const fahrenheitToCelsius = value => Number((((Number(value) - 32) * 5) / 9).toFixed(2));
const feetInchesToCm = (feet, inches) => Number(((Number(feet) * 30.48) + (Number(inches) * 2.54)).toFixed(2));
const numericValue = id => Number($(`#${id}`)?.value || 0);
const optionalNumber = (id, fallback) => {
  const input = $(`#${id}`);
  const raw = input?.value.trim() || '';
  return raw === '' ? fallback : Number(raw);
};

function toast(title, message, type = '') {
  const element = document.createElement('div');
  element.className = `toast ${type}`.trim();
  element.innerHTML = `<strong>${escapeHTML(title)}</strong>${escapeHTML(message)}`;
  $('#toastRegion')?.appendChild(element);
  setTimeout(() => element.remove(), 4200);
}

function goTo(screen) {
  if (!state.unlocked.has(screen) && screen !== 'welcome') return;
  const current = $('.screen.active');
  const next = $(`[data-screen="${screen}"]`);
  if (!next || next === current) return;
  current?.classList.remove('active');
  next.classList.add('active');
  $$('.step').forEach(step => {
    const target = step.dataset.stepTarget;
    const order = ['welcome', 'profile', 'symptoms', 'results'];
    step.classList.toggle('active', target === screen);
    step.classList.toggle('complete', order.indexOf(target) < order.indexOf(screen));
    step.disabled = !state.unlocked.has(target);
  });
  window.scrollTo({ top: 0, behavior: document.body.classList.contains('reduced-motion') ? 'auto' : 'smooth' });
}

function unlock(screen) {
  state.unlocked.add(screen);
  const step = $(`[data-step-target="${screen}"]`);
  if (step) step.disabled = false;
}

async function loadApplicationData() {
  try {
    const [metadataResponse, symptomsResponse, translationResponse] = await Promise.all([
      fetch('/metadata'),
      fetch('/symptoms?limit=250'),
      fetch('/translations'),
    ]);
    if (!metadataResponse.ok || !symptomsResponse.ok || !translationResponse.ok) {
      throw new Error('Application data could not be loaded.');
    }
    state.metadata = await metadataResponse.json();
    const symptomPayload = await symptomsResponse.json();
    state.symptoms = symptomPayload.items || [];
    state.translations = await translationResponse.json();
    populateMetadata();
    populateComorbidities();
    renderCategories();
    renderPopularSymptoms();
    renderSymptoms();
  } catch (error) {
    toast('Connection problem (সংযোগ সমস্যা)', `${error.message} Start the FastAPI server and refresh this page.`, 'error');
    const grid = $('#symptomGrid');
    if (grid) grid.innerHTML = '<div class="empty-state"><span>!</span><h3>Cannot load symptoms (লক্ষণ লোড হয়নি)</h3><p>Please verify that the API is running.</p></div>';
  }
}

function populateMetadata() {
  if (!state.metadata) return;
  $('#diseaseCount').textContent = state.metadata.disease_count ?? 179;
  $('#symptomCount').textContent = state.metadata.symptom_count ?? 208;
  const accuracy = state.metadata.metrics?.accuracy ?? state.metadata.metrics?.test_metrics?.accuracy;
  if (typeof accuracy === 'number') $('#modelAccuracy').textContent = `${(accuracy * 100).toFixed(1)}%`;
}

function populateComorbidities() {
  const options = state.metadata?.input_options?.Comorbidity_1 || [
    'Anemia', 'Asthma', 'COPD', 'Chronic_Kidney_Disease', 'Heart_Disease', 'Hypertension', 'Obesity', 'Type_2_Diabetes',
  ];
  ['comorbidity_1', 'comorbidity_2'].forEach(id => {
    const select = $(`#${id}`);
    if (!select) return;
    select.querySelectorAll('option:not(:first-child)').forEach(option => option.remove());
    options.forEach(option => {
      const label = bilingual(formatName(option), comorbidityBn[option]);
      select.insertAdjacentHTML('beforeend', `<option value="${escapeHTML(option)}">${escapeHTML(label)}</option>`);
    });
  });
}

function getCategoryCounts() {
  return state.symptoms.reduce((counts, symptom) => {
    const category = symptom.Category || 'Other';
    counts[category] = (counts[category] || 0) + 1;
    return counts;
  }, {});
}

function renderCategories() {
  const container = $('#categoryList');
  if (!container) return;
  const counts = getCategoryCounts();
  const categories = Object.keys(counts).sort();
  const all = `<button class="category ${state.selectedCategory === 'All' ? 'active' : ''}" type="button" data-category="All"><span>✦</span><b>All symptoms (সব লক্ষণ)</b><em>${state.symptoms.length}</em></button>`;
  const categoryHTML = categories.map((category, index) => `
    <button class="category ${state.selectedCategory === category ? 'active' : ''}" type="button" data-category="${escapeHTML(category)}">
      <span>${categoryIcons[index % categoryIcons.length]}</span><b>${escapeHTML(categoryLabel(category))}</b><em>${counts[category]}</em>
    </button>`).join('');
  container.innerHTML = all + categoryHTML;
  $$('.category', container).forEach(button => button.addEventListener('click', () => {
    state.selectedCategory = button.dataset.category;
    renderCategories();
    renderSymptoms();
  }));
}

function renderPopularSymptoms() {
  const container = $('#popularSymptoms');
  if (!container) return;
  const found = popularNames.map(name => state.symptoms.find(symptom => symptom.name === name)).filter(Boolean);
  container.innerHTML = '<span style="font-size:8px;color:var(--dim);margin-right:3px">Popular (জনপ্রিয়)</span>' + found.map(symptom => `
    <button class="popular-chip ${state.selectedSymptoms[symptom.name] ? 'selected' : ''}" type="button" data-popular="${escapeHTML(symptom.name)}">${escapeHTML(symptomLabel(symptom))}</button>
  `).join('');
  $$('[data-popular]', container).forEach(button => button.addEventListener('click', () => toggleSymptom(button.dataset.popular)));
}

function filteredSymptoms() {
  const query = state.symptomQuery.trim().toLowerCase();
  return state.symptoms.filter(symptom => {
    const categoryMatch = state.selectedCategory === 'All' || symptom.Category === state.selectedCategory;
    const searchable = [symptom.display, symptom.display_bn, symptom.name, bnSymptom(symptom.name), formatName(symptom.Category), bnCategory(symptom.Category)]
      .filter(Boolean).join(' ').toLowerCase();
    return categoryMatch && (!query || searchable.includes(query));
  });
}

function renderSymptoms() {
  const symptoms = filteredSymptoms();
  const grid = $('#symptomGrid');
  if (!grid) return;
  grid.classList.toggle('compact', state.symptomView === 'compact');
  $('#emptySymptoms')?.classList.toggle('hidden', symptoms.length > 0);
  grid.classList.toggle('hidden', symptoms.length === 0);
  grid.innerHTML = symptoms.map(symptom => {
    const severity = state.selectedSymptoms[symptom.name] || 0;
    const label = symptomLabel(symptom);
    return `<article class="symptom-card ${severity ? 'selected' : ''}" data-symptom-card="${escapeHTML(symptom.name)}" data-severity-level="${severity}" tabindex="0" role="button" aria-pressed="${Boolean(severity)}">
      <div class="symptom-card-header">
        <div><h4>${escapeHTML(label)}</h4><small>${escapeHTML(categoryLabel(symptom.Category || 'Other'))}</small></div>
        <span class="symptom-check">✓</span>
      </div>
      <div class="severity-buttons" aria-label="Severity for ${escapeHTML(label)}">
        ${[1, 2, 3, 4, 5].map(level => `<button class="${severity === level ? 'active' : ''}" type="button" data-severity="${level}" title="${escapeHTML(severityLabels[level])}">${level}</button>`).join('')}
      </div>
    </article>`;
  }).join('');

  $$('[data-symptom-card]', grid).forEach(card => {
    card.addEventListener('click', event => {
      const severityButton = event.target.closest('[data-severity]');
      if (severityButton) setSymptomSeverity(card.dataset.symptomCard, Number(severityButton.dataset.severity));
      else toggleSymptom(card.dataset.symptomCard);
    });
    card.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleSymptom(card.dataset.symptomCard);
      }
    });
  });
}

function toggleSymptom(name) {
  if (state.selectedSymptoms[name]) delete state.selectedSymptoms[name];
  else state.selectedSymptoms[name] = 3;
  syncSymptomUI();
}

function setSymptomSeverity(name, severity) {
  state.selectedSymptoms[name] = severity;
  syncSymptomUI();
}

function syncSymptomUI() {
  renderSymptoms();
  renderPopularSymptoms();
  renderSelectedSymptoms();
}

function renderSelectedSymptoms() {
  const entries = Object.entries(state.selectedSymptoms).sort((a, b) => b[1] - a[1]);
  const count = entries.length;
  const severities = entries.map(([, severity]) => severity);
  const average = count ? severities.reduce((sum, value) => sum + value, 0) / count : 0;
  const maximum = count ? Math.max(...severities) : 0;
  $('#selectedCount').textContent = count;
  $('#selectionBadge').textContent = count;
  $('#averageSeverity').textContent = average.toFixed(1);
  $('#maximumSeverity').textContent = maximum;
  $('#severitySummary').textContent = count
    ? `Average severity ${average.toFixed(1)} of 5 (গড় তীব্রতা ${average.toFixed(1)})`
    : 'No severity added yet (এখনও তীব্রতা দেওয়া হয়নি)';
  $('#symptomValidation').classList.toggle('ready', count >= 2);
  $('#symptomValidation span').textContent = count >= 2
    ? 'Symptom pattern is ready for analysis. (বিশ্লেষণের জন্য লক্ষণ প্রস্তুত)'
    : 'Select at least 2 symptoms. (অন্তত ২টি লক্ষণ নির্বাচন করুন)';
  $('#analyzeButton').disabled = count < 2;

  if (!count) {
    $('#selectedList').innerHTML = '<div class="selection-empty"><span>✦</span><p>Selected symptoms will appear here. (নির্বাচিত লক্ষণ এখানে দেখা যাবে)</p></div>';
    $('#miniSeverityChart').innerHTML = '';
    return;
  }

  $('#selectedList').innerHTML = entries.map(([name, severity]) => {
    const symptom = state.symptoms.find(item => item.name === name) || { name, display: formatName(name) };
    const label = symptomLabel(symptom);
    return `<div class="selected-item" data-severity-level="${severity}">
      <div><b>${escapeHTML(label)}</b><small>${escapeHTML(severityLabels[severity])}</small></div>
      <select class="severity-select" data-update="${escapeHTML(name)}" aria-label="Change severity">
        ${[1, 2, 3, 4, 5].map(level => `<option value="${level}" ${severity === level ? 'selected' : ''}>${level}</option>`).join('')}
      </select>
      <button class="remove-symptom" type="button" data-remove="${escapeHTML(name)}" aria-label="Remove ${escapeHTML(label)}">×</button>
    </div>`;
  }).join('');
  $$('[data-remove]', $('#selectedList')).forEach(button => button.addEventListener('click', () => {
    delete state.selectedSymptoms[button.dataset.remove];
    syncSymptomUI();
  }));
  $$('[data-update]', $('#selectedList')).forEach(select => select.addEventListener('change', (e) => {
    setSymptomSeverity(select.dataset.update, Number(e.target.value));
  }));
  $('#miniSeverityChart').innerHTML = entries.slice(0, 18).map(([, severity]) => `<i data-severity-level="${severity}" style="--height:${severity * 18}%" title="Severity ${severity}"></i>`).join('');
}

function updateProfileCompletion() {
  const fields = Array.from(document.querySelectorAll('#patientForm input:not([type="hidden"]):not([readonly]):not(:disabled), #patientForm select:not(:disabled)'));
  let complete = 0;
  fields.forEach(element => {
    if (element.value.trim() !== '' && element.checkValidity()) complete++;
  });
  const pct = fields.length > 0 ? Math.round((complete / fields.length) * 100) : 0;
  
  const hue = Math.round(pct * 1.3);
  const ringColor = `hsl(${hue}, 95%, 55%)`;
  
  const ring = $('#profileRing');
  if (ring) {
    ring.style.setProperty('--progress', `${pct * 3.6}deg`);
    ring.style.setProperty('--ring-color', ringColor);
    ring.querySelector('span').textContent = `${pct}%`;
  }
}

function validateField(element) {
  const field = element.closest('.field');
  if (!field) return element.checkValidity();
  const optional = !element.required;
  const empty = element.value.trim() === '';
  const valid = (optional && empty) || element.checkValidity();
  field.classList.toggle('invalid', !valid);
  const error = $('.field-error', field);
  if (error) error.textContent = valid ? '' : element.validationMessage || 'Please enter a valid value. (সঠিক মান দিন)';
  return valid;
}

function validateProfile() {
  let valid = true;
  profileRequiredIds.forEach(id => {
    const element = $(`#${id}`);
    if (!element || !validateField(element)) valid = false;
  });
  if ($('#sex').value === 'Female' && !$('#pregnancy_status').value) valid = false;
  if (!valid) {
    toast('Complete required fields (প্রয়োজনীয় তথ্য পূরণ করুন)', 'Review the highlighted patient information before continuing.', 'error');
    document.querySelector('.field.invalid')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  return valid;
}

function collectProfile() {
  const sex = $('#sex').value;
  const temperatureF = optionalNumber('temperature_f', optionalVitalDefaults.temperature_f);
  const temperatureC = fahrenheitToCelsius(temperatureF);
  const heightFeet = numericValue('height_feet');
  const heightInches = numericValue('height_inches');
  const heightCm = feetInchesToCm(heightFeet, heightInches);
  const weight = numericValue('weight_kg');
  const bmi = Number((weight / ((heightCm / 100) ** 2)).toFixed(1));
  const providedMeasurements = Object.keys(optionalVitalDefaults).filter(id => $(`#${id}`).value.trim() !== '');

  return {
    patient_name: $('#patient_name').value.trim() || null,
    age: numericValue('age'),
    sex,
    pregnancy_status: sex === 'Female' ? $('#pregnancy_status').value : 'Not_Applicable',
    smoking_status: $('#smoking_status').value,
    comorbidity_1: $('#comorbidity_1').value || null,
    comorbidity_2: $('#comorbidity_2').value || null,
    symptom_duration_days: optionalNumber('symptom_duration_days', 1),
    onset_type: $('#onset_type').value,
    temperature_f: temperatureF,
    temperature_c: temperatureC,
    heart_rate_bpm: optionalNumber('heart_rate_bpm', optionalVitalDefaults.heart_rate_bpm),
    respiratory_rate_bpm: optionalNumber('respiratory_rate_bpm', optionalVitalDefaults.respiratory_rate_bpm),
    spo2_percent: optionalNumber('spo2_percent', optionalVitalDefaults.spo2_percent),
    systolic_bp: optionalNumber('systolic_bp', optionalVitalDefaults.systolic_bp),
    diastolic_bp: optionalNumber('diastolic_bp', optionalVitalDefaults.diastolic_bp),
    height_feet: heightFeet,
    height_inches: heightInches,
    height_cm: heightCm,
    weight_kg: weight,
    bmi,
    random_glucose_mg_dl: optionalNumber('random_glucose_mg_dl', optionalVitalDefaults.random_glucose_mg_dl),
    pain_score_0_10: optionalNumber('pain_score_0_10', optionalVitalDefaults.pain_score_0_10),
    provided_measurements: providedMeasurements,
  };
}

function apiPayload() {
  if (!state.profile) state.profile = collectProfile();
  return { ...state.profile, symptoms: { ...state.selectedSymptoms } };
}

function updateTemperatureConversion() {
  const input = $('#temperature_f');
  if (!input?.value) return;
  const c = fahrenheitToCelsius(input.value);
  const preview = $('#temperatureCPreview');
  if (preview) preview.textContent = `${c.toFixed(2)} °C`;
}

function updateBMI() {
  const feet = numericValue('height_feet');
  const inches = numericValue('height_inches');
  const weight = numericValue('weight_kg');
  const height = feetInchesToCm(feet, inches);
  $('#height_cm').value = Number.isFinite(height) ? height : '';
  const heightPreview = $('#heightCmPreview');
  if (heightPreview) heightPreview.textContent = Number.isFinite(height) ? `${height.toFixed(2)} cm` : '—';
  const bmiInput = $('#bmi');
  if (height > 0 && weight > 0) bmiInput.value = (weight / ((height / 100) ** 2)).toFixed(1);
  const bmi = Number(bmiInput.value || 0);
  let label = 'Enter measurements (পরিমাপ দিন)', color = 'var(--muted)', position = 0;
  if (bmi > 0) {
    position = clamp(((bmi - 12) / 33) * 100, 1, 99);
    if (bmi < 18.5) { label = 'Below common range (স্বাভাবিকের নিচে)'; color = 'var(--cyan)'; }
    else if (bmi < 25) { label = 'Healthy range (স্বাভাবিক সীমা)'; color = 'var(--green)'; }
    else if (bmi < 30) { label = 'Above common range (স্বাভাবিকের উপরে)'; color = 'var(--amber)'; }
    else { label = 'High range (উচ্চ সীমা)'; color = 'var(--red)'; }
  }
  $('#bmiLabel').textContent = label;
  $('#bmiLabel').style.color = color;
  $('#bmiIndicator').style.left = `${position}%`;
  updateProfileCompletion();
}

function updateMetricTracks() {
  const specs = {
    temperature_f: [86, 113], heart_rate_bpm: [20, 250], respiratory_rate_bpm: [4, 80],
    spo2_percent: [50, 100], systolic_bp: [40, 280], diastolic_bp: [20, 180],
    random_glucose_mg_dl: [20, 800], pain_score_0_10: [0, 10],
  };
  Object.entries(specs).forEach(([id, [min, max]]) => {
    const input = $(`#${id}`);
    if (!input) return;
    const fallback = optionalVitalDefaults[id];
    const value = input.value.trim() === '' && fallback !== undefined ? fallback : Number(input.value);
    const track = input.closest('.metric-field')?.querySelector('.range-track i');
    if (track) track.style.setProperty('--value', `${clamp(((value - min) / (max - min)) * 100, 0, 100)}%`);
  });
}

async function analyze() {
  if (!state.profile || Object.keys(state.selectedSymptoms).length < 2) return;
  const overlay = $('#analysisOverlay');
  overlay.classList.add('active');
  const stages = [
    ['Validating submitted measurements... (পরিমাপ যাচাই হচ্ছে...)', 16, 0],
    ['Mapping symptom severity signatures... (লক্ষণ মিলানো হচ্ছে...)', 38, 1],
    ['Calculating calibrated probabilities... (সম্ভাবনা হিসাব হচ্ছে...)', 63, 1],
    ['Running safety screen... (ঝুঁকি যাচাই হচ্ছে...)', 82, 2],
    ['Building visual report... (রিপোর্ট তৈরি হচ্ছে...)', 96, 3],
  ];
  let stageIndex = 0;
  const interval = setInterval(() => {
    const [text, progress, activeStep] = stages[Math.min(stageIndex, stages.length - 1)];
    $('#analysisStage').textContent = text;
    $('#analysisProgress').style.width = `${progress}%`;
    $$('.analysis-steps span').forEach((step, index) => step.classList.toggle('active', index <= activeStep));
    stageIndex += 1;
  }, 560);

  try {
    const response = await fetch('/predict?top_k=5', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(apiPayload()),
    });
    if (!response.ok) {
      let message = `Prediction failed with status ${response.status}.`;
      try {
        const payload = await response.json();
        message = payload.detail ? JSON.stringify(payload.detail) : message;
      } catch (_) { /* no-op */ }
      throw new Error(message);
    }
    state.result = await response.json();
    await new Promise(resolve => setTimeout(resolve, 2100));
    $('#analysisProgress').style.width = '100%';
    renderResult();
    unlock('results');
    setTimeout(() => {
      overlay.classList.remove('active');
      goTo('results');
    }, 420);
  } catch (error) {
    overlay.classList.remove('active');
    toast('Analysis failed (বিশ্লেষণ ব্যর্থ)', error.message, 'error');
  } finally {
    clearInterval(interval);
  }
}

function riskConfig(risk) {
  const level = String(risk?.risk_level || '').toLowerCase();
  if (risk?.emergency || level.includes('critical')) return { angle: 68, progress: 1, color: 'var(--red)', className: 'critical' };
  if (level.includes('high')) return { angle: 48, progress: .87, color: 'var(--red)', className: 'high' };
  if (level.includes('moderate')) return { angle: 0, progress: .52, color: 'var(--amber)', className: 'moderate' };
  return { angle: -60, progress: .14, color: 'var(--green)', className: 'low' };
}

function renderResult() {
  const result = state.result;
  if (!result?.predictions?.length) return;
  const top = result.predictions[0];
  const risk = result.risk_assessment || {};
  const uncertainty = result.uncertainty || {};
  const confidence = Number(top.probability || 0);
  const clarity = Math.round(clamp((confidence * .62 + Number(uncertainty.top_two_margin || 0) * .28 + (1 - Number(uncertainty.normalized_entropy || 0)) * .1) * 100, 0, 100));
  const riskUI = riskConfig(risk);

  $('#resultTimestamp').textContent = `Generated ${new Date(result.generated_at).toLocaleString('en-BD')} · Model ${result.model_version}`;
  $('#confidenceOrb').style.setProperty('--confidence', (confidence * 100).toFixed(2));
  animateNumber($('#confidenceValue'), 0, confidence * 100, value => `${value.toFixed(1)}%`);
  $('#topDisease').textContent = diseaseLabel(top);
  $('#topCategory').textContent = categoryLabel(top.category || 'Uncategorized');
  $('#topDiseaseMeta').textContent = `${urgencyLabel(formatName(top.base_urgency || 'Routine'))} · Typical duration (সাধারণ সময়কাল): ${top.typical_duration_days || 'varies'} days`;
  $('#diagnosisTags').innerHTML = [
    `${result.input_summary?.active_symptom_count || 0} symptoms (লক্ষণ)`,
    `${Math.round((top.explanation?.signature_match_ratio || 0) * 100)}% signature match (মিল)`,
    categoryLabel(top.category || 'Other'),
  ].map(tag => `<span>${escapeHTML(tag)}</span>`).join('');
  $('#confidenceMessage').textContent = `${uncertainty.message || 'Probability is not the same as a confirmed diagnosis.'} (এই সম্ভাবনা নিশ্চিত রোগ নির্ণয় নয়।)`;

  const gauge = $('#riskGauge');
  gauge.dataset.level = riskUI.className;
  gauge.style.setProperty('--risk-angle', `${riskUI.angle}deg`);
  const arcLength = 298.5;
  const arc = $('#riskArc');
  arc.style.strokeDasharray = `${arcLength}`;
  arc.style.strokeDashoffset = `${arcLength * (1 - riskUI.progress)}`;
  $('#riskScore').textContent = risk.risk_score ?? '—';
  $('#riskPill').textContent = riskLabel(risk.risk_level);
  $('#riskPill').style.color = riskUI.color;
  $('#riskUrgency').textContent = urgencyLabel(risk.urgency || 'Review the assessment carefully');
  $('#riskRationale').textContent = [...(risk.rationale || []), ...(risk.abnormal_vitals || [])].slice(0, 2).join(' · ') || 'No specific triage concern was returned. (নির্দিষ্ট ঝুঁকি পাওয়া যায়নি)';

  $('#uncertaintyPill').textContent = `${formatName(uncertainty.status || 'unknown')} uncertainty (অনিশ্চয়তা)`;
  $('#certaintyScore').textContent = clarity;
  $('#marginValue').textContent = percent(uncertainty.top_two_margin);
  $('#entropyValue').textContent = percent(uncertainty.normalized_entropy);
  $('#unknownCount').textContent = uncertainty.unknown_symptoms?.length || 0;
  $('#uncertaintyMessage').textContent = `${uncertainty.message || 'No uncertainty message returned.'} (মডেলের ফলাফল সতর্কতার সঙ্গে ব্যবহার করুন।)`;

  renderEmergencyBanner(risk);
  renderVitalChart();
  renderProbabilityChart(result.predictions);
  renderSeverityLineChart(result.input_summary?.active_symptoms || []);
  renderExplanations(result.predictions.slice(0, 3));
  renderCareTab('actions');
  renderSnapshot(result);
  $('#resultDisclaimer').textContent = `${result.disclaimer} এই ফলাফল চিকিৎসকের রোগ নির্ণয়ের বিকল্প নয়।`;
  $('#predictionId').textContent = `ID ${String(result.prediction_id).slice(0, 8).toUpperCase()}`;
  setupResultCardTilt();
}

function renderEmergencyBanner(risk) {
  const banner = $('#emergencyBanner');
  const flags = [...(risk.red_flags || []), ...(risk.abnormal_vitals || [])];
  if (risk.emergency || flags.length) {
    banner.classList.remove('hidden');
    const title = risk.emergency ? 'Emergency warning detected (জরুরি সতর্কতা)' : 'Measurement or warning sign needs attention (পরিমাপ বা লক্ষণ পর্যালোচনা প্রয়োজন)';
    banner.innerHTML = `<strong>${title}</strong><p>${escapeHTML(flags.join(' · ') || risk.urgency || 'Seek immediate professional help if symptoms are severe or rapidly worsening.')}</p>`;
  } else banner.classList.add('hidden');
}

function classifyVital(type, value) {
  const normal = {
    temperature: value >= 36.1 && value <= 37.2,
    heart: value >= 60 && value <= 100,
    respiratory: value >= 12 && value <= 20,
    spo2: value >= 95,
    systolic: value >= 90 && value < 140,
    diastolic: value >= 60 && value < 90,
    glucose: value >= 70 && value <= 140,
    pain: value <= 3,
  }[type];
  const urgent = {
    temperature: value >= 40 || value < 35,
    heart: value > 130 || value < 45,
    respiratory: value > 30 || value < 8,
    spo2: value < 90,
    systolic: value > 180 || value < 80,
    diastolic: value > 120 || value < 45,
    glucose: value > 300 || value < 50,
    pain: value >= 8,
  }[type];
  if (urgent) return 'urgent';
  return normal ? 'normal' : 'watch';
}

function renderVitalChart() {
  const p = state.profile;
  const vitals = [
    ['Temp (তাপ.)', p.temperature_f, '°F', 'temperature', [86, 113], p.temperature_c],
    ['Heart (হৃদ.)', p.heart_rate_bpm, 'bpm', 'heart', [20, 250]],
    ['Resp. (শ্বাস)', p.respiratory_rate_bpm, '/min', 'respiratory', [4, 80]],
    ['SpO₂', p.spo2_percent, '%', 'spo2', [50, 100]],
    ['Sys BP', p.systolic_bp, 'mmHg', 'systolic', [40, 280]],
    ['Dia BP', p.diastolic_bp, 'mmHg', 'diastolic', [20, 180]],
    ['Glucose', p.random_glucose_mg_dl, 'mg/dL', 'glucose', [20, 800]],
    ['Pain (ব্যথা)', p.pain_score_0_10, '/10', 'pain', [0, 10]],
  ];
  const colors = {
    normal: ['#76efb5', '#2cae78', 'rgba(99,230,165,.25)'],
    watch: ['#ffe18b', '#e5a844', 'rgba(255,205,112,.25)'],
    urgent: ['#ff8ca0', '#d74367', 'rgba(255,113,136,.26)'],
  };
  $('#vitalChart').innerHTML = vitals.map(([label, value, unit, type, range, secondary]) => {
    const statusValue = type === 'temperature' ? Number(secondary) : Number(value);
    const status = classifyVital(type, statusValue);
    const height = clamp(((Number(value) - range[0]) / (range[1] - range[0])) * 100, 8, 100);
    const [top, bottom, glow] = colors[status];
    const secondaryText = secondary !== undefined ? ` / ${Number(secondary).toFixed(1)}°C` : '';
    return `<div class="vital-stat-card">
      <div class="vital-stat-info">
        <b>${escapeHTML(label)}</b>
        <span style="color: ${top}">${escapeHTML(value)}<small>${escapeHTML(unit)}${escapeHTML(secondaryText)}</small></span>
      </div>
      <div class="vital-stat-track">
        <i style="width: ${height}%; background: linear-gradient(90deg, ${bottom}, ${top}); box-shadow: 0 0 10px ${glow}"></i>
      </div>
    </div>`;
  }).join('');
}

function renderProbabilityChart(predictions) {
  const max = Math.max(...predictions.map(item => Number(item.probability || 0)), .0001);
  $('#probabilityChart').innerHTML = predictions.map((item, index) => `
    <div class="probability-row">
      <div class="probability-row-header">
        <div>
          <b>${index + 1}. ${escapeHTML(diseaseLabel(item))}</b>
          <small>${escapeHTML(categoryLabel(item.category || 'Other'))}</small>
        </div>
        <strong>${percent(item.probability)}</strong>
      </div>
      <div class="probability-track">
        <i style="--width:${clamp((Number(item.probability) / max) * 100, .5, 100)}%"></i>
      </div>
    </div>`).join('');
}

function renderSeverityLineChart(symptoms) {
  const data = symptoms.slice(0, 10);
  $('#symptomChartCount').textContent = `${symptoms.length} selected (নির্বাচিত)`;
  if (!data.length) { $('#severityLineChart').innerHTML = ''; return; }
  const width = 420, height = 190, padX = 18, padY = 18;
  const x = index => data.length === 1 ? width / 2 : padX + index * ((width - padX * 2) / (data.length - 1));
  const y = severity => height - padY - ((severity - 1) / 4) * (height - padY * 2);
  const points = data.map((item, index) => `${x(index)},${y(item.severity)}`).join(' ');
  const area = `${padX},${height - padY} ${points} ${x(data.length - 1)},${height - padY}`;
  const labels = data.map((item, index) => {
    const shortLabel = (item.display_bn || item.display || formatName(item.symptom)).split(' ')[0].slice(0, 8);
    return `<text class="chart-label" x="${x(index)}" y="${height - 3}" text-anchor="middle">${escapeHTML(shortLabel)}</text>`;
  }).join('');
  const dots = data.map((item, index) => `<circle class="point" cx="${x(index)}" cy="${y(item.severity)}" r="3.8"><title>${escapeHTML(symptomLabel(item))}: ${item.severity}</title></circle>`).join('');
  $('#severityLineChart').innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Symptom severity line chart"><defs><linearGradient id="severityGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b866ff" stop-opacity=".32"/><stop offset="1" stop-color="#6e42d1" stop-opacity="0"/></linearGradient></defs><polygon class="area" points="${area}"/><polyline class="line" points="${points}"/>${dots}${labels}</svg>`;
  const top = [...symptoms].sort((a, b) => b.severity - a.severity)[0];
  $('#maxSymptomLabel').textContent = `Highest (সর্বোচ্চ): ${symptomLabel(top)} (${top.severity}/5)`;
}

function normalizeMissingSymptom(item) {
  if (typeof item === 'string') return { symptom: item.replaceAll(' ', '_'), display: formatName(item) };
  return item || {};
}

function renderExplanations(predictions) {
  $('#explanationList').innerHTML = predictions.map(item => {
    const explanation = item.explanation || {};
    const ratio = Number(explanation.signature_match_ratio || 0);
    const matched = explanation.matched_signature_symptoms || [];
    const missing = (explanation.missing_signature_symptoms || []).map(normalizeMissingSymptom);
    return `<div class="explanation-item">
      <div class="explanation-head"><b>${escapeHTML(diseaseLabel(item))}</b><span>${Math.round(ratio * 100)}% signature match (লক্ষণ মিল)</span></div>
      <div class="match-meter"><i style="--match:${ratio * 100}%"></i></div>
      <div class="evidence-chips">
        ${matched.slice(0, 5).map(symptom => `<span>✓ ${escapeHTML(symptomLabel(symptom))} · ${symptom.severity}/5</span>`).join('')}
        ${missing.slice(0, 3).map(symptom => `<span class="missing">Not reported (উল্লেখ নেই): ${escapeHTML(symptomLabel(symptom))}</span>`).join('')}
        ${!matched.length && !missing.length ? '<span class="missing">No signature detail available (বিস্তারিত তথ্য নেই)</span>' : ''}
      </div>
    </div>`;
  }).join('');
}

function renderCareTab(tab) {
  const guidance = state.result?.care_guidance || {};
  const map = {
    actions: guidance.recommended_actions || [],
    monitor: guidance.what_to_monitor || [],
    clinician: guidance.clinician_may_consider || [],
    safety: guidance.medication_safety || [],
  };
  $$('.care-tabs button').forEach(button => button.classList.toggle('active', button.dataset.careTab === tab));
  $('#careContent').innerHTML = (map[tab] || []).map((item, index) => `<div class="care-item"><i>${String(index + 1).padStart(2, '0')}</i><p>${escapeHTML(item)}</p></div>`).join('') || '<div class="care-item"><i>i</i><p>No guidance was returned for this section. (এই অংশে নির্দেশনা পাওয়া যায়নি)</p></div>';
}

function renderSnapshot(result) {
  const p = state.profile;
  $('#snapshotPatient').textContent = p.patient_name || 'Anonymous patient (নামবিহীন রোগী)';
  $('#snapshotDemographics').textContent = `${p.age} years (বছর) · ${bilingual(p.sex, sexBn[p.sex])}`;
  $('#snapshotPattern').textContent = `${p.symptom_duration_days} days (দিন) · ${bilingual(p.onset_type, onsetBn[p.onset_type])}`;
  $('#snapshotSymptoms').textContent = `${result.input_summary?.active_symptom_count || 0} active (সক্রিয়)`;
  $('#snapshotSeverity').textContent = `${result.input_summary?.maximum_symptom_severity || 0} of 5`;
  $('#snapshotModel').textContent = result.model_version;
}

function animateNumber(element, from, to, formatter, duration = 800) {
  if (!element) return;
  const start = performance.now();
  const tick = now => {
    const t = clamp((now - start) / duration, 0, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    element.textContent = formatter(from + (to - from) * eased);
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

async function downloadPdf() {
  if (!state.result) return;
  const button = $('#downloadPdf');
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = 'Building report... (রিপোর্ট তৈরি হচ্ছে)';
  try {
    const response = await fetch('/report/pdf', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(apiPayload()),
    });
    if (!response.ok) throw new Error('The PDF report could not be generated.');
    const blob = await response.blob();
    downloadBlob(blob, `MediSense_Report_${state.result.prediction_id.slice(0, 8)}.pdf`);
    toast('Report ready (রিপোর্ট প্রস্তুত)', 'The PDF assessment report has been generated with safe Bengali-font fallback.');
  } catch (error) {
    toast('Download failed (ডাউনলোড ব্যর্থ)', error.message, 'error');
  } finally {
    button.disabled = false;
    button.innerHTML = original;
  }
}

function downloadBlob(blob, name) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

function resetAssessment() {
  state.selectedSymptoms = {};
  state.profile = null;
  state.result = null;
  state.demoMode = false;
  state.unlocked = new Set(['welcome']);
  $('#patientForm').reset();
  const defaults = {
    age: 35, symptom_duration_days: 2, temperature_f: 98.6, heart_rate_bpm: 80,
    pain_score_0_10: 0, height_feet: 5, height_inches: 7, weight_kg: 66.5,
  };
  Object.entries(defaults).forEach(([id, value]) => { const element = $(`#${id}`); if (element) element.value = value; });
  Object.keys(optionalVitalDefaults).forEach(id => { const element = $(`#${id}`); if (element) element.value = ''; });
  $('#pregnancyField').classList.add('hidden-field');
  renderSelectedSymptoms();
  renderSymptoms();
  renderPopularSymptoms();
  updateBMI();
  updateTemperatureConversion();
  updateMetricTracks();
  updateProfileCompletion();
  goTo('welcome');
  toast('New assessment (নতুন মূল্যায়ন)', 'The previous session data has been cleared.');
}

function loadDemoData() {
  state.demoMode = true;
  const values = {
    patient_name: 'Demo Patient', age: 29, sex: 'Female', pregnancy_status: 'No', smoking_status: 'Never',
    symptom_duration_days: 3, onset_type: 'Sudden', temperature_f: 102.4, heart_rate_bpm: 104,
    respiratory_rate_bpm: 20, spo2_percent: 97, systolic_bp: 112, diastolic_bp: 74,
    random_glucose_mg_dl: 108, pain_score_0_10: 6, height_feet: 5, height_inches: 4, weight_kg: 56.4,
  };
  Object.entries(values).forEach(([id, value]) => { const element = $(`#${id}`); if (element) element.value = value; });
  $('#pregnancyField').classList.remove('hidden-field');
  state.selectedSymptoms = { Fever: 4, Severe_Headache: 3, Body_Ache: 4, Joint_Pain: 3, Rash: 2, Nausea: 2 };
  updateBMI();
  updateTemperatureConversion();
  updateMetricTracks();
  updateProfileCompletion();
  renderSelectedSymptoms();
  state.profile = collectProfile();
  unlock('profile');
  unlock('symptoms');
  goTo('symptoms');
  toast('Demo loaded (ডেমো প্রস্তুত)', 'A sample symptom pattern is ready. Select Generate AI analysis.');
}

function setupTilt(root = document) {
  if (!root || window.matchMedia('(pointer: coarse)').matches || document.body.classList.contains('reduced-motion')) return;
  $$('.tilt-card', root).forEach(card => {
    if (card.dataset.tiltReady) return;
    card.dataset.tiltReady = 'true';
    const strength = Number(card.dataset.tiltStrength || 4);
    let frame = 0;
    card.addEventListener('mousemove', event => {
      if (frame) cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - .5;
        const y = (event.clientY - rect.top) / rect.height - .5;
        card.style.setProperty('--pointer-x', `${(x + .5) * 100}%`);
        card.style.setProperty('--pointer-y', `${(y + .5) * 100}%`);
        card.style.transform = `perspective(1000px) rotateX(${-y * strength}deg) rotateY(${x * strength}deg) translateY(-3px)`;
      });
    }, { passive: true });
    card.addEventListener('mouseleave', () => {
      if (frame) cancelAnimationFrame(frame);
      card.style.transform = '';
    });
  });
}

function setupResultCardTilt() { setupTilt($('#screen-results')); }

function setupHeroSpotlight() {
  const stage = $('.orb-stage');
  if (!stage) return;
  let frame = 0;
  stage.addEventListener('pointermove', event => {
    if (frame) cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      const rect = stage.getBoundingClientRect();
      stage.style.setProperty('--spot-x', `${((event.clientX - rect.left) / rect.width) * 100}%`);
      stage.style.setProperty('--spot-y', `${((event.clientY - rect.top) / rect.height) * 100}%`);
    });
  }, { passive: true });
}

function setupAmbientCanvas() {
  const canvas = $('#ambientCanvas');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  let particles = [];
  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = innerWidth * dpr;
    canvas.height = innerHeight * dpr;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    particles = Array.from({ length: Math.min(25, Math.floor(innerWidth / 50)) }, () => ({
      x: Math.random() * innerWidth, y: Math.random() * innerHeight,
      r: Math.random() * 90 + 40,
      vx: (Math.random() - .5) * .6, vy: (Math.random() - .5) * .6,
      a: Math.random() * .12 + .03,
      cIdx: Math.floor(Math.random() * 3)
    }));
  };
  const colors = [ {r:169,g:112,b:255}, {r:88,g:216,b:255}, {r:230,g:104,b:255} ];
  const draw = () => {
    context.clearRect(0, 0, innerWidth, innerHeight);
    if (!document.hidden && !document.body.classList.contains('reduced-motion')) {
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < -150) p.x = innerWidth + 150;
        if (p.x > innerWidth + 150) p.x = -150;
        if (p.y < -150) p.y = innerHeight + 150;
        if (p.y > innerHeight + 150) p.y = -150;
        context.beginPath();
        context.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        const col = colors[p.cIdx];
        const grad = context.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
        grad.addColorStop(0, `rgba(${col.r},${col.g},${col.b},${p.a})`);
        grad.addColorStop(1, `rgba(${col.r},${col.g},${col.b},0)`);
        context.fillStyle = grad;
        context.fill();
      });
    }
    requestAnimationFrame(draw);
  };
  resize();
  window.addEventListener('resize', resize, { passive: true });
  requestAnimationFrame(draw);
}

function wireEvents() {
  $('#year').textContent = new Date().getFullYear();
  $('#beginAssessment').addEventListener('click', () => { unlock('profile'); goTo('profile'); });
  $('#loadDemo').addEventListener('click', loadDemoData);
  $$('[data-go]').forEach(button => button.addEventListener('click', () => goTo(button.dataset.go)));
  $$('.step').forEach(button => button.addEventListener('click', () => goTo(button.dataset.stepTarget)));

  $('#patientForm').addEventListener('submit', event => {
    event.preventDefault();
    if (!validateProfile()) return;
    state.profile = collectProfile();
    unlock('symptoms');
    goTo('symptoms');
    toast('Profile complete (তথ্য সম্পন্ন)', 'Now select and rate the current symptoms.');
  });
  $$('input, select', $('#patientForm')).forEach(element => {
    element.addEventListener('input', () => { validateField(element); updateProfileCompletion(); });
    element.addEventListener('blur', () => validateField(element));
  });
  $('#sex').addEventListener('change', () => {
    $('#pregnancyField').classList.toggle('hidden-field', $('#sex').value !== 'Female');
  });
  ['height_feet', 'height_inches', 'weight_kg'].forEach(id => $(`#${id}`).addEventListener('input', updateBMI));
  $('#temperature_f').addEventListener('input', updateTemperatureConversion);
  $$('.metric-field input').forEach(input => input.addEventListener('input', updateMetricTracks));

  $('#symptomSearch').addEventListener('input', event => { state.symptomQuery = event.target.value; renderSymptoms(); });
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k' && state.unlocked.has('symptoms')) {
      event.preventDefault();
      goTo('symptoms');
      $('#symptomSearch').focus();
    }
  });
  $$('.view-buttons button').forEach(button => button.addEventListener('click', () => {
    state.symptomView = button.dataset.view;
    $$('.view-buttons button').forEach(item => item.classList.toggle('active', item === button));
    renderSymptoms();
  }));
  $('#clearSymptoms').addEventListener('click', () => { state.selectedSymptoms = {}; syncSymptomUI(); });
  $('#analyzeButton').addEventListener('click', analyze);

  $$('.care-tabs button').forEach(button => button.addEventListener('click', () => renderCareTab(button.dataset.careTab)));
  $('#downloadPdf').addEventListener('click', downloadPdf);
  $('#printReport').addEventListener('click', () => window.print());
  $('#newAssessment').addEventListener('click', resetAssessment);
  $('#motionToggle').addEventListener('click', event => {
    document.body.classList.toggle('reduced-motion');
    event.currentTarget.classList.toggle('active', document.body.classList.contains('reduced-motion'));
    toast('Motion setting (অ্যানিমেশন)', document.body.classList.contains('reduced-motion') ? 'Animations have been reduced.' : 'Full interface animation is active.');
  });
}

function setupScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  }, { threshold: 0.15 });
  $$('.feature-card').forEach(el => observer.observe(el));
}

function setupTrustCounter() {
  const animateValue = (id, start, end, duration, isPercent = false) => {
    let obj = document.getElementById(id);
    if (!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const current = (easeProgress * (end - start) + start);
      if (isPercent) {
        obj.innerHTML = current.toFixed(1) + '%';
      } else {
        obj.innerHTML = Math.floor(current);
      }
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }
  
  setTimeout(() => {
    animateValue('diseaseCount', 0, 179, 2500);
    animateValue('symptomCount', 0, 208, 2500);
    animateValue('modelAccuracy', 0, 94.8, 2500, true);
  }, 500);
}

function initialize() {
  wireEvents();
  setupAmbientCanvas();
  setupHeroSpotlight();
  setupTilt();
  setupScrollReveal();
  setupTrustCounter();
  updateBMI();
  updateTemperatureConversion();
  updateMetricTracks();
  updateProfileCompletion();
  renderSelectedSymptoms();
  loadApplicationData();
}

document.addEventListener('DOMContentLoaded', initialize);
