import re

path = '/Users/tanvikadam/rubricai/frontend/demo.html'

# Read current file
with open(path, 'r') as f:
    content = f.read()

# 1. Add AI Assistant nav item if missing
if 'assistantView' not in content:
    content = content.replace(
        "<div class=\"nav-item\" onclick=\"showView('rubric')\"><span class=\"nav-dot\"></span>Rubric Framework</div>",
        "<div class=\"nav-item\" onclick=\"showView('rubric')\"><span class=\"nav-dot\"></span>Rubric Framework</div>\n    <div class=\"nav-item\" onclick=\"showView('assistant')\"><span class=\"nav-dot\"></span>AI Assistant <span class=\"nav-badge\" style=\"background:#f0fdf4;color:#059669;\">New</span></div>"
    )

# 2. Fix navOrder
content = content.replace(
    "const navOrder=['about','upload','students','rubric'];",
    "const navOrder=['about','upload','students','rubric','assistant'];"
)

# 3. Fix viewMeta
content = content.replace(
    "rubric:['Rubric Framework','34 research-backed behavioral indicators across 3 domains'],\n};",
    "rubric:['Rubric Framework','34 research-backed behavioral indicators across 3 domains'],\n  assistant:['AI Assistant','Ask anything about your students, scores, and evaluations'],\n};"
)

# 4. Add bounce animation to CSS
if '@keyframes bounce' not in content:
    content = content.replace(
        '::-webkit-scrollbar-thumb:hover{background:#cbd5e1;}',
        '::-webkit-scrollbar-thumb:hover{background:#cbd5e1;}\n@keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-4px);}}'
    )

# 5. Add AI Assistant HTML view before closing content div
assistant_html = '''
<!-- AI ASSISTANT VIEW -->
<div id="assistantView" class="view">
  <div class="page-title">AI Assistant</div>
  <div class="page-sub">Ask anything about your students, scores, evaluations, or rubric</div>
  <div id="suggestedPrompts" style="margin-bottom:20px;">
    <div style="font-size:12px;font-weight:600;color:#94a3b8;margin-bottom:10px;text-transform:uppercase;letter-spacing:.5px;">Suggested questions</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px;">
      <button class="btn btn-secondary btn-sm" onclick="askSuggested('Which students need the most attention?')">Which students need the most attention?</button>
      <button class="btn btn-secondary btn-sm" onclick="askSuggested('Summarize the class performance')">Summarize class performance</button>
      <button class="btn btn-secondary btn-sm" onclick="askSuggested('Compare Student 1 and Student 2')">Compare Student 1 and Student 2</button>
      <button class="btn btn-secondary btn-sm" onclick="askSuggested('Why was Student 2 Sim B flagged?')">Why was Student 2 Sim B flagged?</button>
      <button class="btn btn-secondary btn-sm" onclick="askSuggested('Which students are closest to reaching Level 3?')">Who is closest to Level 3?</button>
      <button class="btn btn-secondary btn-sm" onclick="askSuggested('What are the most common strengths across all students?')">Most common strengths?</button>
    </div>
  </div>
  <div class="card" style="padding:0;overflow:hidden;display:flex;flex-direction:column;height:520px;">
    <div id="chatMessages" style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:14px;">
      <div style="display:flex;gap:10px;align-items:flex-start;">
        <div style="width:32px;height:32px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:14px;font-weight:700;color:#6366f1;">AI</div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:0 10px 10px 10px;padding:12px 16px;max-width:80%;">
          <div style="font-size:13px;color:#334155;line-height:1.7;">Hello! I am your RubricAI assistant. I have full access to your student evaluations, scores, and rubric data. Ask me anything about your class.<br><br>Load demo data first, then ask away.</div>
        </div>
      </div>
    </div>
    <div style="border-top:1px solid #e2e8f0;padding:14px 16px;display:flex;gap:10px;background:#f8fafc;">
      <input id="chatInput" type="text" placeholder="Ask about your students, scores, or evaluations..."
        style="flex:1;background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;font-size:13px;color:#0f172a;outline:none;"
        onkeydown="if(event.key==='Enter')sendChat()"
        onfocus="this.style.borderColor='#6366f1'" onblur="this.style.borderColor='#e2e8f0'">
      <button class="btn" onclick="sendChat()" id="sendBtn">Send</button>
    </div>
  </div>
</div>
'''

# 6. Add AI Assistant JS before getLvl
assistant_js = '''
// AI ASSISTANT
let chatHistory=[];
function buildSystemPrompt(){
  const students=Object.values(studentData);
  if(!students.length)return 'You are RubricAI assistant. No student data loaded yet. Ask user to load demo data first.';
  const allLevels=students.flatMap(s=>s.evaluations.map(e=>e.level));
  const avg=allLevels.length?(allLevels.reduce((a,b)=>a+b,0)/allLevels.length).toFixed(1):'N/A';
  const flagged=students.filter(s=>s.evaluations.some(e=>e.level===1||(e.confidence&&e.confidence<0.6)));
  const summaries=students.map(s=>{
    const ev=s.evaluations.map(e=>`Sim ${e.simulation}: Level ${e.level} (${Math.round((e.confidence||0)*100)}% confidence) — ${e.justification} Strengths: ${e.strengths} Improvements: ${e.improvements}`).join(' | ');
    return `${s.name}: Overall ${s.scores.overall} | ${ev}`;
  }).join('\\n');
  return `You are RubricAI assistant helping a faculty member understand student evaluations.
RUBRIC: Indicator 1 active — open-ended questions. Level 1:0-1 Qs, Level 2:2-3, Level 3:4-5, Level 4:6+
Confidence = AI certainty about score, not student performance. Below 60% = flagged.
CLASS: ${students.length} students, avg ${avg}/4.0, ${flagged.length} flagged.
STUDENTS:
${summaries}
Answer concisely and professionally. Reference actual names and scores.`;
}
function appendMessage(role,text){
  const msgs=document.getElementById('chatMessages');
  const isAI=role==='assistant';
  const div=document.createElement('div');
  div.style.cssText='display:flex;gap:10px;align-items:flex-start;';
  div.innerHTML=`<div style="width:32px;height:32px;border-radius:8px;background:${isAI?'#eef2ff':'#f1f5f9'};display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:${isAI?'14':'12'}px;font-weight:700;color:${isAI?'#6366f1':'#64748b'};">${isAI?'AI':'You'}</div><div style="background:${isAI?'#f8fafc':'#eef2ff'};border:1px solid ${isAI?'#e2e8f0':'#c7d2fe'};border-radius:${isAI?'0 10px 10px 10px':'10px 0 10px 10px'};padding:12px 16px;max-width:80%;"><div style="font-size:13px;color:#334155;line-height:1.7;white-space:pre-wrap;">${text}</div></div>`;
  msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight;
}
function appendTyping(){
  const msgs=document.getElementById('chatMessages');
  const div=document.createElement('div');div.id='typingIndicator';
  div.style.cssText='display:flex;gap:10px;align-items:flex-start;';
  div.innerHTML=`<div style="width:32px;height:32px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#6366f1;">AI</div><div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:0 10px 10px 10px;padding:12px 16px;"><div style="display:flex;gap:4px;align-items:center;"><div style="width:6px;height:6px;border-radius:50%;background:#94a3b8;animation:bounce 1s infinite;"></div><div style="width:6px;height:6px;border-radius:50%;background:#94a3b8;animation:bounce 1s infinite .2s;"></div><div style="width:6px;height:6px;border-radius:50%;background:#94a3b8;animation:bounce 1s infinite .4s;"></div></div></div>`;
  msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight;
}
async function sendChat(){
  const input=document.getElementById('chatInput');
  const text=input.value.trim();if(!text)return;
  input.value='';document.getElementById('sendBtn').disabled=true;
  document.getElementById('suggestedPrompts').style.display='none';
  appendMessage('user',text);chatHistory.push({role:'user',content:text});appendTyping();
  try{
    const res=await fetch('https://api.anthropic.com/v1/messages',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:1000,system:buildSystemPrompt(),messages:chatHistory})
    });
    const data=await res.json();
    document.getElementById('typingIndicator')?.remove();
    const reply=data.content?.[0]?.text||'Sorry, could not get a response.';
    chatHistory.push({role:'assistant',content:reply});appendMessage('assistant',reply);
  }catch(e){document.getElementById('typingIndicator')?.remove();appendMessage('assistant','Connection error. Make sure backend is running.');}
  document.getElementById('sendBtn').disabled=false;document.getElementById('chatInput').focus();
}
function askSuggested(q){document.getElementById('chatInput').value=q;sendChat();}
'''

# Insert assistant HTML before closing content divs
if 'assistantView' not in content:
    content = content.replace(
        "  </div><!-- end content -->\n</div><!-- end main -->",
        assistant_html + "\n  </div><!-- end content -->\n</div><!-- end main -->"
    )

# Insert assistant JS before getLvl
if 'sendChat' not in content:
    content = content.replace(
        "function getLvl(s)",
        assistant_js + "\nfunction getLvl(s)"
    )

# Write fixed file
with open(path, 'w') as f:
    f.write(content)

print(f"Done! File has {content.count(chr(10))} lines")
print(f"AI Assistant view: {'YES' if 'assistantView' in content else 'MISSING'}")
print(f"AI Assistant JS: {'YES' if 'sendChat' in content else 'MISSING'}")
print(f"navOrder fixed: {'YES' if 'assistant' in content else 'MISSING'}")
