// ── Init Profile Page ─────────────────────────────────────────────────────────
function initProfile(sid) {
    if (!sid || !studentData[sid]) { loadPage('students'); return; }
    // Profile rendering is handled inside pages/profile.html script
    // This file handles any additional profile logic
}

// ── Apply Override ────────────────────────────────────────────────────────────
function applyOverride(sid, idx) {
    const sel = document.getElementById(`ovr-${sid}-${idx}`);
    if (!sel) return;
    const val = parseInt(sel.value);
    if (!val) return;

    studentData[sid].evaluations[idx].level = val;
    studentData[sid].evaluations[idx].overridden = true;

    // Recalc cluster/domain/overall
    const levels = studentData[sid].evaluations.map(e => e.level);
    const avg = Math.round((levels.reduce((a,b) => a+b, 0) / levels.length) * 100) / 100;

    if (studentData[sid].scores.domains?.['Communication']) {
        studentData[sid].scores.domains['Communication'].score = avg;
        studentData[sid].scores.domains['Communication'].clusters['Interview Communication'] = avg;
    }
    studentData[sid].scores.overall = avg;

    // Show confirmation
    const note = document.getElementById(`ovrNote-${sid}-${idx}`);
    if (note) {
        note.style.display = 'inline';
        setTimeout(() => note.style.display = 'none', 2000);
    }

    // Re-render profile after short delay
    setTimeout(() => initProfile(sid), 400);
}
