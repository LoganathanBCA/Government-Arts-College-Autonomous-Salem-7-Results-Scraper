/**
 * app.js — Frontend logic for GACSLM7 Results Scraper
 */

const API_BASE = window.location.origin;

// ── DOM Elements ─────────────────────────────────────────────────
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const dropzoneUploading = document.getElementById('dropzoneUploading');
const uploadResult = document.getElementById('uploadResult');
const uploadMessage = document.getElementById('uploadMessage');
const scrapeBtn = document.getElementById('scrapeBtn');
const progressPanel = document.getElementById('progressPanel');
const statDone = document.getElementById('statDone');
const statTotal = document.getElementById('statTotal');
const statCurrent = document.getElementById('statCurrent');
const progressPercent = document.getElementById('progressPercent');
const progressBarFill = document.getElementById('progressBarFill');
const studentList = document.getElementById('studentList');
const resultsSection = document.getElementById('resultsSection');
const resultsTableHead = document.getElementById('resultsTableHead');
const resultsTableBody = document.getElementById('resultsTableBody');
const downloadBtn = document.getElementById('downloadBtn');
const cursorGlow = document.getElementById('cursorGlow');

let uploadedStudents = [];
let pollInterval = null;


// ── Cursor Glow Tracking ────────────────────────────────────────
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let glowX = mouseX;
let glowY = mouseY;
let cursorVisible = false;

document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    if (!cursorVisible) {
        cursorVisible = true;
        cursorGlow.style.opacity = '1';
    }
});

// Detect when the mouse leaves the entire browser window
document.addEventListener('mouseout', (e) => {
    if (e.relatedTarget === null) {
        cursorVisible = false;
        cursorGlow.style.opacity = '0';
    }
});

// Detect when it comes back
document.addEventListener('mouseenter', () => {
    cursorVisible = true;
    cursorGlow.style.opacity = '1';
});

function animateCursor() {
    // Smooth interpolation (easing)
    glowX += (mouseX - glowX) * 0.15;
    glowY += (mouseY - glowY) * 0.15;
    
    // Hardware-accelerated movement for buttery smooth 60fps
    cursorGlow.style.transform = `translate3d(${glowX}px, ${glowY}px, 0)`;
    
    requestAnimationFrame(animateCursor);
}
requestAnimationFrame(animateCursor);




// ── Drag & Drop ──────────────────────────────────────────────────
dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});


// ── File Upload ──────────────────────────────────────────────────
async function handleFile(file) {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!['.xlsx', '.csv'].includes(ext)) {
        showError('Please upload a .xlsx or .csv file.');
        return;
    }

    dropzone.querySelector('.dropzone-content').style.display = 'none';
    dropzoneUploading.style.display = 'flex';
    uploadResult.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Upload failed'); }

        const data = await res.json();
        uploadedStudents = data.students;

        dropzone.querySelector('.dropzone-content').style.display = 'block';
        dropzoneUploading.style.display = 'none';
        uploadResult.style.display = 'block';
        uploadMessage.textContent = data.message;

        scrapeBtn.disabled = false;
        progressPanel.style.display = 'none';
        resultsSection.style.display = 'none';
        studentList.innerHTML = '';
    } catch (err) {
        dropzone.querySelector('.dropzone-content').style.display = 'block';
        dropzoneUploading.style.display = 'none';
        showError(err.message);
    }
}


// ── Start Scraping ───────────────────────────────────────────────
scrapeBtn.addEventListener('click', async () => {
    scrapeBtn.disabled = true;
    scrapeBtn.innerHTML = `<div class="spinner" style="width:20px;height:20px;border-width:2px;"></div> Scraping...`;

    progressPanel.style.display = 'block';
    resultsSection.style.display = 'none';
    studentList.innerHTML = '';
    statDone.textContent = '0';
    statTotal.textContent = uploadedStudents.length;
    progressPercent.textContent = '0%';
    progressBarFill.style.width = '0%';

    uploadedStudents.forEach((s) => addStudentItem(s.register_no, 'pending'));

    try {
        const res = await fetch(`${API_BASE}/scrape`, { method: 'POST' });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Failed to start scraping'); }
        startPolling();
    } catch (err) {
        showError(err.message);
        resetScrapeBtn();
    }
});


// ── Status Polling ───────────────────────────────────────────────
function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE}/status`);
            const data = await res.json();
            updateProgress(data);
            if (data.completed) {
                clearInterval(pollInterval);
                pollInterval = null;
                onScrapingComplete(data);
            }
        } catch (err) { console.error('Polling error:', err); }
    }, 1000);
}

function updateProgress(data) {
    const { total, done, current, failed, success } = data;
    const percent = total > 0 ? Math.round((done / total) * 100) : 0;

    statDone.textContent = done;
    statTotal.textContent = total;
    statCurrent.textContent = current || '—';
    progressPercent.textContent = `${percent}%`;
    progressBarFill.style.width = `${percent}%`;

    const successSet = new Set(success);
    const failedRegNos = new Set(failed.map(f => typeof f === 'string' ? f : f.register_no));

    studentList.querySelectorAll('.student-item').forEach((item) => {
        const reg = item.dataset.reg;
        if (successSet.has(reg)) {
            updateStudentItem(item, 'success', null);
        } else if (failedRegNos.has(reg)) {
            const failEntry = failed.find(f => (typeof f === 'string' ? f : f.register_no) === reg);
            updateStudentItem(item, 'failed', failEntry && typeof failEntry === 'object' ? failEntry.error : null);
        } else if (reg === current) {
            updateStudentItem(item, 'current', null);
        }
    });
}

function onScrapingComplete(data) {
    resetScrapeBtn();
    if (data.results && data.results.length > 0) {
        buildResultsTable(data.results);
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function resetScrapeBtn() {
    scrapeBtn.disabled = false;
    scrapeBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M4 10C4 6.68629 6.68629 4 10 4C13.3137 4 16 6.68629 16 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M16 10C16 13.3137 13.3137 16 10 16C6.68629 16 4 13.3137 4 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 3"/>
            <circle cx="10" cy="10" r="2" fill="currentColor"/>
        </svg>
        Start Scraping`;
}


// ── Student List Helpers ─────────────────────────────────────────
function addStudentItem(reg, status) {
    const div = document.createElement('div');
    div.className = `student-item ${status}`;
    div.dataset.reg = reg;
    const icons = { pending: '○', current: '◉', success: '✓', failed: '✗' };
    div.innerHTML = `<span class="student-icon">${icons[status]}</span><span class="student-reg">${reg}</span><span class="student-error"></span>`;
    studentList.appendChild(div);
}

function updateStudentItem(item, status, errorMsg) {
    if (item.classList.contains(status) && !errorMsg) return;
    item.className = `student-item ${status}`;
    const icons = { pending: '○', current: '◉', success: '✓', failed: '✗' };
    item.querySelector('.student-icon').textContent = icons[status];
    const errorSpan = item.querySelector('.student-error');
    errorSpan.textContent = (errorMsg && status === 'failed') ? `— ${errorMsg}` : '';
}


// ── Results Table ────────────────────────────────────────────────
function buildResultsTable(results) {
    const subjectCodes = [];
    const seen = new Set();
    results.forEach((r) => {
        Object.keys(r.subjects || {}).forEach((code) => {
            if (!seen.has(code)) { subjectCodes.push(code); seen.add(code); }
        });
    });

    const columns = ['Name', 'Register No', ...subjectCodes, 'Total'];
    resultsTableHead.innerHTML = '';
    const headerRow = document.createElement('tr');
    columns.forEach((col) => { const th = document.createElement('th'); th.textContent = col; headerRow.appendChild(th); });
    resultsTableHead.appendChild(headerRow);

    resultsTableBody.innerHTML = '';
    results.forEach((r) => {
        const tr = document.createElement('tr');
        const tdName = document.createElement('td'); tdName.textContent = r.name || 'UNKNOWN'; tr.appendChild(tdName);
        const tdReg = document.createElement('td'); tdReg.textContent = r.register_no || 'UNKNOWN'; tdReg.style.fontFamily = "var(--font-mono)"; tdReg.style.fontWeight = '600'; tr.appendChild(tdReg);

        let total = 0;
        subjectCodes.forEach((code) => {
            const td = document.createElement('td'); td.className = 'mark-cell';
            const marks = (r.subjects || {})[code];
            if (marks === undefined || marks === null || marks === '-') { td.textContent = '-'; td.classList.add('dash'); }
            else { td.textContent = marks; const n = parseInt(marks, 10); if (!isNaN(n)) total += n; }
            tr.appendChild(td);
        });

        const tdTotal = document.createElement('td'); tdTotal.className = 'mark-cell total-cell'; tdTotal.textContent = total; tr.appendChild(tdTotal);
        resultsTableBody.appendChild(tr);
    });
}


// ── Download ─────────────────────────────────────────────────────
downloadBtn.addEventListener('click', async () => {
    try {
        const res = await fetch(`${API_BASE}/download`);
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Download failed'); }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = 'student_results.xlsx';
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (err) { showError(err.message); }
});


// ── Error Toast ──────────────────────────────────────────────────
function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = `⚠ ${message}`;
    document.body.appendChild(toast);
    toast.offsetHeight; // force reflow
    toast.classList.add('visible');
    setTimeout(() => { toast.classList.remove('visible'); setTimeout(() => document.body.removeChild(toast), 300); }, 5000);
}
