const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const html = fs.readFileSync('app/static/index.html', 'utf8');
const dom = new JSDOM(html);
const window = dom.window;
global.window = window;
global.document = window.document;
global.setTimeout = setTimeout;
global.innerWidth = 1000;
global.innerHeight = 1000;
global.requestAnimationFrame = (cb) => setTimeout(cb, 16);
global.devicePixelRatio = 1;

window.fetch = async (url) => {
    if (url === '/metadata') return { ok: true, json: async () => ({ disease_count: 179, symptom_count: 208 }) };
    if (url === '/symptoms?limit=250') return { ok: true, json: async () => ({ items: [{ name: 'Fever', Category: 'General', display: 'Fever', display_bn: 'Fever' }, { name: 'Cough', Category: 'General', display: 'Cough', display_bn: 'Cough' }] }) };
    if (url === '/translations') return { ok: true, json: async () => ({ symptoms: {}, categories: {}, risk_levels: {}, urgency: {} }) };
    return { ok: false };
};

document.addEventListener = (event, callback) => {
    if (event === 'DOMContentLoaded') {
        setTimeout(callback, 50);
    }
};

const code = fs.readFileSync('app/static/app.js', 'utf8');
try {
    eval(code);
    setTimeout(() => {
        const gridHTML = document.getElementById('symptomGrid').innerHTML;
        const popHTML = document.getElementById('popularSymptoms').innerHTML;
        const catHTML = document.getElementById('categoryList').innerHTML;
        console.log('Symptom Grid HTML contains symptom-card?', gridHTML.includes('symptom-card'));
        console.log('Popular Symptoms HTML contains Fever?', popHTML.includes('Fever'));
        console.log('Category List HTML contains General?', catHTML.includes('General'));
    }, 500);
} catch (e) {
    console.error('ERROR:', e);
}
