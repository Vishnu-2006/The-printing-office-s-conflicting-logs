const sample = {
  departments: [
    { code: "A", jobs: [{ id: "A2", time: 2 }, { id: "A7", time: 7 }, { id: "A9", time: 9 }] },
    { code: "B", jobs: [{ id: "B1", time: 1 }, { id: "B7", time: 7 }] },
    { code: "C", jobs: [{ id: "C3", time: 3 }, { id: "C10", time: 10 }] }
  ]
};
const editor = document.getElementById("input-json");
const mergeBtn = document.getElementById("merge-btn");
let latestTimeline = [];

function setSample(){ editor.value = JSON.stringify(sample, null, 2); updateInputCount(); }
function updateInputCount(){
  try {
    const data=JSON.parse(editor.value), depts=data.departments||[];
    const jobs=depts.reduce((n,d)=>n+(d.jobs||[]).length,0);
    document.getElementById("input-count").textContent=`${depts.length} departments · ${jobs} jobs`;
  } catch { document.getElementById("input-count").textContent="Invalid JSON"; }
}
function showError(message){
  const box=document.getElementById("error-box"); box.textContent=message; box.classList.remove("hidden");
}
function clearError(){document.getElementById("error-box").classList.add("hidden");}
function renderTimeline(jobs){
  const target=document.getElementById("timeline"); target.className="timeline";
  target.innerHTML=jobs.length ? jobs.map((j,i)=>`
    <div class="job-row"><span class="job-index">${String(i+1).padStart(2,"0")}</span>
    <div class="job-main"><span class="dept-chip">${escapeHtml(j.department)}</span><span class="job-id">${escapeHtml(j.job_id)}</span></div>
    <span class="job-time">t = ${j.timestamp}</span></div>`).join("")
    : `<div class="empty-state"><div class="empty-icon">∅</div><b>No jobs in the queues</b><span>All input queues are empty.</span></div>`;
}
function renderBreakdown(queues){
  const target=document.getElementById("queue-breakdown");
  const max=Math.max(1,...queues.map(q=>q.jobs.length));
  target.innerHTML=queues.length ? queues.map(q=>`
    <div class="queue-line"><span class="queue-code">${escapeHtml(q.code)}</span>
    <div class="bar-track"><div class="bar-fill" style="width:${q.jobs.length/max*100}%"></div></div>
    <span class="queue-count">${q.jobs.length}</span></div>`).join("")
    : `<div class="empty-note">No department queues supplied.</div>`;
}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function merge(){
  clearError(); mergeBtn.disabled=true; mergeBtn.textContent="Merging…";
  try{
    const payload=JSON.parse(editor.value);
    const response=await fetch("/api/merge",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await response.json();
    if(!response.ok) throw new Error(data.error||"Merge failed.");
    latestTimeline=data.timeline; renderTimeline(data.timeline); renderBreakdown(data.input_queues);
    const r=data.report;
    document.getElementById("metric-depts").textContent=r.departments_received;
    document.getElementById("metric-received").textContent=r.jobs_received.toLocaleString();
    document.getElementById("metric-produced").textContent=r.jobs_produced.toLocaleString();
    document.getElementById("metric-missing").textContent=r.jobs_missing;
    const status=document.getElementById("result-status"); status.textContent="MERGE SUCCESSFUL"; status.classList.remove("waiting");
    document.getElementById("complexity-label").textContent=`${r.complexity} · ${r.empty_departments} empty queues`;
    document.getElementById("download-btn").disabled=false;
    await loadHistory();
  }catch(err){showError(err instanceof SyntaxError?"Please enter valid JSON.":err.message);}
  finally{mergeBtn.disabled=false;mergeBtn.innerHTML='Merge queues <span>→</span>';}
}
async function loadHistory(){
  const target=document.getElementById("history-list");
  try{
    const response=await fetch("/api/history"), data=await response.json();
    target.innerHTML=data.history.length?data.history.map(h=>`
      <div class="history-row"><div><b>Merge #${h.id}</b><br><span>${escapeHtml(h.created_at)}</span></div>
      <span>${h.departments} depts · ${h.jobs} jobs</span></div>`).join(""):`<div class="empty-note">No saved merges yet.</div>`;
  }catch{target.innerHTML='<div class="empty-note">Could not load history.</div>';}
}
document.getElementById("format-btn").addEventListener("click",()=>{try{editor.value=JSON.stringify(JSON.parse(editor.value),null,2);updateInputCount();clearError();}catch{showError("Cannot format invalid JSON.");}});
document.getElementById("reset-btn").addEventListener("click",setSample);
document.getElementById("merge-btn").addEventListener("click",merge);
document.getElementById("refresh-history").addEventListener("click",loadHistory);
editor.addEventListener("input",updateInputCount);
document.getElementById("download-btn").addEventListener("click",()=>{
  const header="position,department,job_id,timestamp";
  const rows=latestTimeline.map((j,i)=>[i+1,j.department,j.job_id,j.timestamp].join(","));
  const blob=new Blob([[header,...rows].join("\n")],{type:"text/csv"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="merged-print-timeline.csv";a.click();URL.revokeObjectURL(url);
});
setSample();loadHistory();
