const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const html = fs.readFileSync('app/static/index.html', 'utf8');
const dom = new JSDOM(html);
const window = dom.window;
global.window = window;
global.document = window.document;
global.setTimeout = setTimeout;

// Mock fetch
global.fetch = async (url) => {
    if (url === '/metadata') return { ok: true, json: async () => ({ disease_count: 179, symptom_count: 208 }) };
    if (url === '/symptoms?limit=250') return { ok: true, json: async () => ({ items: [{ name: 'Fever', Category: 'General', display: 'Fever', display_bn: 'Fever' }] }) };
    if (url === '/translations') return { ok: true, json: async () => ({ symptoms: {}, categories: {}, risk_levels: {}, urgency: {} }) };
    return { ok: false };
};

// Mock document.addEventListener
document.addEventListener = (event, callback) => {
    if (event === 'DOMContentLoaded') {
        setTimeout(callback, 50);
    }
};

const code = fs.readFileSync('app/static/app.js', 'utf8');
try {
    eval(code);
    setTimeout(() => {
        console.log('Symptom Grid innerHTML:', document.getElementById('symptomGrid').innerHTML);
        console.log('Popular Symptoms innerHTML:', document.getElementById('popularSymptoms').innerHTML);
        console.log('Category List innerHTML:', document.getElementById('categoryList').innerHTML);
    }, 500);
} catch (e) {
    console.error('ERROR:', e);
}
