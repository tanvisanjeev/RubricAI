// ── Init Students Page ────────────────────────────────────────────────────────
function initStudents() {
    const students = Object.values(studentData);

    if (!students.length) {
        const noData = document.getElementById('noDataState');
        if (noData) noData.style.display = 'block';
        return;
    }

    const allLevels = students.flatMap(s => s.evaluations.map(e => e.level));
    const avg = allLevels.length
        ? (allLevels.reduce((a,b) => a+b, 0) / allLevels.length).toFixed(1)
        : '—';
    const flagged = students.filter(s =>
        s.evaluations.some(e => e.level === 1 || (e.confidence && e.confidence < 0.6))
    );

    const el = id => document.getElementById(id);
    if (el('sTotal'))  el('sTotal').textContent  = students.length;
    if (el('sEvals'))  el('sEvals').textContent  = allLevels.length;
    if (el('sAvg'))    el('sAvg').textContent    = avg;
    if (el('sReview')) el('sReview').textContent = flagged.length;
}
