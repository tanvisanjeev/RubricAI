// ── Export All Students CSV ───────────────────────────────────────────────────
function exportAllCSV() {
    const students = Object.values(studentData);
    if (!students.length) { alert('No data to export.'); return; }

    let csv = 'Student ID,Communication,Critical Thinking,Professional Agency,Overall\n';
    students.forEach(s => {
        const d = s.scores.domains || {};
        csv += `${s.id},`;
        csv += `${d['Communication']?.score || 'N/A'},`;
        csv += `${d['Critical Thinking']?.score || 'N/A'},`;
        csv += `${d['Professional Agency']?.score || 'N/A'},`;
        csv += `${s.scores.overall || 'N/A'}\n`;
    });

    downloadBlob(csv, 'rubricai_all_scores.csv', 'text/csv');
}

// ── Export Individual Student CSV ─────────────────────────────────────────────
function exportStudentCSV(sid) {
    const s = studentData[sid];
    if (!s) return;

    let csv = 'Student ID,Simulation,Indicator,Level,Overridden,Confidence,Open-Ended Count,Closed Count,Total Questions,Justification\n';
    s.evaluations.forEach(e => {
        const just = (e.justification || '').replace(/"/g, "'");
        csv += `${e.student_id},`;
        csv += `${e.simulation},`;
        csv += `"${e.indicator}",`;
        csv += `${e.level},`;
        csv += `${e.overridden || false},`;
        csv += `${e.confidence || ''},`;
        csv += `${e.open_ended_count || 0},`;
        csv += `${e.closed_count || 0},`;
        csv += `${e.total_questions || 0},`;
        csv += `"${just}"\n`;
    });

    downloadBlob(csv, `student_${sid}_report.csv`, 'text/csv');
}

// ── Export PDF ────────────────────────────────────────────────────────────────
async function exportPDF() {
    const students = Object.values(studentData);
    if (!students.length) { alert('No data to export.'); return; }

    try {
        const body = {
            students: students.map(s => ({
                student_id: s.id,
                results: s.evaluations,
                scores: s.scores
            }))
        };

        const res = await fetch(`${API}/api/export/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!res.ok) throw new Error('PDF export failed');

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'rubricai_report.pdf';
        a.click();
        URL.revokeObjectURL(url);

    } catch(e) {
        alert('PDF export failed. Make sure backend is running on port 8000.');
    }
}

// ── Download Helper ───────────────────────────────────────────────────────────
function downloadBlob(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
