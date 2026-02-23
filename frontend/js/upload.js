// ── Init Upload Page ──────────────────────────────────────────────────────────
function initUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');

    if (!dropZone) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', e => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });
}

// ── Handle File Selection ─────────────────────────────────────────────────────
function handleFile(file) {
    window._selectedFile = file;
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    dropZone.innerHTML = `
        <div style="font-size:48px;margin-bottom:16px;color:#10b981;">✓</div>
        <div style="font-size:17px;font-weight:600;margin-bottom:8px;color:#10b981;">${file.name}</div>
        <div style="color:#64748b;font-size:13px;">${(file.size/1024).toFixed(1)} KB — Ready to evaluate</div>
    `;

    const btn = document.getElementById('uploadBtn');
    if (btn) btn.disabled = false;
}

// ── Process Upload ────────────────────────────────────────────────────────────
async function processUpload() {
    const file = window._selectedFile;
    if (!file) return;

    const uploadBtn = document.getElementById('uploadBtn');
    const progressSection = document.getElementById('progressSection');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    if (uploadBtn) uploadBtn.disabled = true;
    if (progressSection) progressSection.style.display = 'block';

    let prog = 0;
    const iv = setInterval(() => {
        prog = Math.min(prog + Math.random() * 10, 90);
        if (progressFill) progressFill.style.width = prog + '%';
        if (progressText) progressText.textContent = Math.round(prog) + '%';
    }, 400);

    try {
        const fd = new FormData();
        fd.append('file', file);

        const res = await fetch(`${API}/api/evaluate`, {
            method: 'POST',
            body: fd
        });

        const data = await res.json();
        clearInterval(iv);

        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = '100%';

        if (data.status === 'success') {
            processAPIResponse(data);
            setTimeout(() => loadPage('students'), 600);
        } else {
            showUploadStatus('error', data.message || 'Evaluation failed.');
            if (uploadBtn) uploadBtn.disabled = false;
        }

    } catch(e) {
        clearInterval(iv);
        showUploadStatus('error', 'Cannot connect to backend. Make sure server is running on port 8000.');
        if (uploadBtn) uploadBtn.disabled = false;
    }
}

// ── Show Status Message ───────────────────────────────────────────────────────
function showUploadStatus(type, msg) {
    const el = document.getElementById('statusMsg');
    if (!el) return;
    const styles = {
        success: 'background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;',
        error:   'background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;'
    };
    el.innerHTML = `<div style="padding:12px 16px;border-radius:8px;font-size:13px;${styles[type]}">${msg}</div>`;
}
