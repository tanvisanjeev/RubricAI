const API = 'http://127.0.0.1:8000';
let studentData = {};
let currentStudentId = null;

const pageMeta = {
    dashboard:   { title: 'Dashboard',          meta: 'Overview of RubricAI evaluation system' },
    upload:      { title: 'Upload and Evaluate', meta: 'Upload student interview transcripts for AI evaluation' },
    students:    { title: 'Students',            meta: 'AI-generated evaluations with scoring hierarchy' },
    profile:     { title: 'Student Profile',     meta: 'Individual evaluation with evidence and scoring breakdown' },
    rubric:      { title: 'Rubric Framework',    meta: '34 research-backed behavioral indicators across 3 domains' },
    responsible: { title: 'Responsible AI',      meta: 'Ethical AI use, transparency, and human oversight' },
    about:       { title: 'About RubricAI',      meta: 'Technology, methodology, and development roadmap' },
};

const navOrder = ['dashboard', 'upload', 'students', 'rubric', 'responsible', 'about'];

async function loadPage(page, studentId) {
    if (studentId) currentStudentId = studentId;

    const meta = pageMeta[page] || pageMeta.upload;
    document.getElementById('topbarTitle').textContent = meta.title;
    document.getElementById('topbarMeta').textContent  = meta.meta;

    // Sidebar active state
    document.querySelectorAll('.nav-item').forEach((el, i) => {
        el.classList.toggle('active', navOrder[i] === page);
    });

    // Export All button
    document.getElementById('exportAllBtn').style.display =
        page === 'students' ? 'inline-flex' : 'none';

    // Load page HTML
    try {
        const res  = await fetch(`pages/${page}.html`);
        const html = await res.text();
        document.getElementById('pageContent').innerHTML = html;

        // Init page logic
        if (page === 'dashboard')    initDashboard();
        if (page === 'upload')       initUpload();
        if (page === 'students')     initStudents();
        if (page === 'profile')      initProfile(currentStudentId);
        if (page === 'rubric')       initRubric();

    } catch(e) {
        document.getElementById('pageContent').innerHTML = `
            <div style="text-align:center;padding:80px;color:#475569;">
                <div style="font-size:40px;margin-bottom:16px;">&#9888;</div>
                <div style="font-size:16px;">Could not load page. Make sure frontend server is running.</div>
            </div>`;
    }
}

function updateStudentCount() {
    const el = document.getElementById('studentCount');
    if (el) el.textContent = Object.keys(studentData).length;
}

function processAPIResponse(data) {
    studentData = {};
    (data.students || []).forEach(s => {
        studentData[s.student_id] = {
            id:          s.student_id,
            name:        `Student ${s.student_id}`,
            evaluations: s.results || [],
            scores:      s.scores  || {}
        };
    });
    updateStudentCount();
}

function loadDemoData() {
    const demo = {
        students: [
            {
                student_id: '1',
                results: [
                    {
                        student_id: '1', simulation: 'A',
                        indicator: 'Asks clear, open-ended questions',
                        level: 3, confidence: 0.92,
                        open_ended_count: 24, closed_count: 5,
                        total_questions: 29, strategic_phrasing_count: 2,
                        open_ended_examples: [
                            'Can you walk me through your typical morning routine?',
                            'What specifically has been frustrating about the new system?',
                            'How did you approach solving that problem?'
                        ],
                        closed_examples: ['Is that correct?'],
                        justification: 'Student asked 24 open-ended questions exceeding the Level 3 threshold of 4-5 per 10-minute segment. Questions were clearly phrased with minimal clarification needed. Two instances of strategic phrasing detected.',
                        strengths: 'Excellent question volume and clarity. Good use of experience-based questions.',
                        improvements: 'Incorporate more strategic phrasing and invite storytelling more frequently to reach Level 4.'
                    },
                    {
                        student_id: '1', simulation: 'B',
                        indicator: 'Asks clear, open-ended questions',
                        level: 2, confidence: 0.88,
                        open_ended_count: 3, closed_count: 0,
                        total_questions: 3, strategic_phrasing_count: 0,
                        open_ended_examples: ['What are your main concerns?', 'How can we improve this?'],
                        closed_examples: [],
                        justification: 'Student asked 3 open-ended questions meeting the Level 2 threshold.',
                        strengths: 'Questions were relevant and clearly phrased.',
                        improvements: 'Increase question volume to 4-5 per segment to reach Level 3.'
                    }
                ],
                scores: {
                    overall: 2.5,
                    domains: {
                        'Communication':        { score: 2.5, clusters: { 'Interview Communication': 2.5, 'Communicating Ideas Clearly': null } },
                        'Critical Thinking':    { score: null, clusters: {} },
                        'Professional Agency':  { score: null, clusters: {} }
                    }
                }
            },
            {
                student_id: '2',
                results: [
                    {
                        student_id: '2', simulation: 'A',
                        indicator: 'Asks clear, open-ended questions',
                        level: 2, confidence: 0.85,
                        open_ended_count: 3, closed_count: 1,
                        total_questions: 4, strategic_phrasing_count: 0,
                        open_ended_examples: ['What do you think about this?', 'How does that work?'],
                        closed_examples: ['Is that right?'],
                        justification: 'Student asked 3 open-ended questions meeting Level 2. Questions lacked strategic phrasing.',
                        strengths: 'Basic questioning competence demonstrated.',
                        improvements: 'Increase volume and use strategic phrasing.'
                    },
                    {
                        student_id: '2', simulation: 'B',
                        indicator: 'Asks clear, open-ended questions',
                        level: 1, confidence: 0.95,
                        open_ended_count: 0, closed_count: 0,
                        total_questions: 0, strategic_phrasing_count: 0,
                        open_ended_examples: [],
                        closed_examples: [],
                        justification: 'Student asked 0 questions during the interview. Student did not engage with the questioning task.',
                        strengths: 'None identified in this performance.',
                        improvements: 'Student must actively ask questions throughout the interview.'
                    }
                ],
                scores: {
                    overall: 1.5,
                    domains: {
                        'Communication':        { score: 1.5, clusters: { 'Interview Communication': 1.5, 'Communicating Ideas Clearly': null } },
                        'Critical Thinking':    { score: null, clusters: {} },
                        'Professional Agency':  { score: null, clusters: {} }
                    }
                }
            }
        ]
    };
    processAPIResponse(demo);
    loadPage('students');
}

function getLvlClass(score) {
    if (score >= 3.5) return 4;
    if (score >= 2.5) return 3;
    if (score >= 1.5) return 2;
    return 1;
}

function levelBar(level) {
    let html = '<div class="level-bar">';
    for (let i = 1; i <= 4; i++) {
        html += `<div class="level-segment ${i <= level ? 'filled-' + level : ''}"></div>`;
    }
    html += '</div>';
    return html;
}

const levelDefinitions = {
    1: 'Asks 0-1 open-ended questions per 10-min segment. Questions are vague or confusing. Phrasing may be unclear or leading. Does not invite storytelling.',
    2: 'Asks 2-3 open-ended questions per 10-min segment. Sometimes vague. Clear phrasing, no leading phrases. Does not invite storytelling.',
    3: 'Asks 4-5 open-ended questions per 10-min segment. Clearly phrased, minimal clarification needed. Questions focus on one topic at a time.',
    4: 'Asks 6+ open-ended questions per 10-min segment. Strategic phrasing 3-5 times. Invites storytelling 2-4 times.',
};

function getLevelDefinition(level) {
    return levelDefinitions[level] || '';
}

window.onload = () => loadPage('upload');
