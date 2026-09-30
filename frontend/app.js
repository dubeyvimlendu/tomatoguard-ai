const API_BASE = window.API_BASE || ""; // set window.API_BASE if the API runs on another origin
const MAX_BYTES = 8 * 1024 * 1024, OK_TYPES = ["image/jpeg", "image/png", "image/webp"];
const $ = (s) => document.querySelector(s);
let file = null;

/* ---- router ---- */
function route() {
  const id = (location.hash || "#home").slice(1);
  const view = document.getElementById(id) ? id : "home";
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("on", v.id === view));
  document.querySelectorAll("#menu a").forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + view));
  if (view === "history") renderHistory();
  window.scrollTo(0, 0);
}
addEventListener("hashchange", route); route();

/* ---- content per category ---- */
const COPY = {
  HEALTHY: { headline: "Your leaf appears healthy", steps: ["Continue regular monitoring.", "Maintain appropriate irrigation and airflow.", "Inspect leaves periodically for changes."] },
  FUNGAL: { headline: "Fungal disease detected", steps: ["Inspect nearby plants for similar symptoms.", "Improve airflow around plants.", "Remove severely affected plant material where appropriate.", "Consult local agricultural guidance before applying fungicides."] },
  OTHER_DISEASE: { headline: "Non-fungal disease or pest detected", steps: ["Inspect for signs of bacterial disease, viral symptoms, or pest activity.", "Check nearby plants for similar symptoms.", "Consider local agricultural guidance for diagnosis and management."] },
};
const pct = (p) => Math.round(p * 1000) / 10 + "%";

/* ---- file selection ---- */
function showError(msg) { const e = $("#errorBox"); e.textContent = msg; e.hidden = !msg; }
function pick(f) {
  showError(""); $("#result").hidden = true;
  if (!f) return showError("No image selected. Choose a tomato leaf photo to continue.");
  if (!OK_TYPES.includes(f.type)) return showError("Unsupported file type. Please use a JPG, PNG or WebP image.");
  if (f.size > MAX_BYTES) return showError("This image is larger than 8 MB. Please choose a smaller one.");
  const img = new Image(), url = URL.createObjectURL(f);
  img.onload = () => {
    file = f; $("#previewImg").src = url; $("#fileName").textContent = f.name;
    $("#fileDims").textContent = `${img.naturalWidth} × ${img.naturalHeight} px, ${(f.size / 1048576).toFixed(2)} MB`;
    $("#dropEmpty").hidden = true; $("#previewBox").hidden = false;
  };
  img.onerror = () => showError("This image could not be read. It may be corrupted.");
  img.src = url;
}
function reset() { file = null; $("#dropEmpty").hidden = false; $("#previewBox").hidden = true; $("#fileInput").value = ""; $("#cameraInput").value = ""; showError(""); }
$("#btnChoose").onclick = (e) => { e.stopPropagation(); $("#fileInput").click(); };
$("#btnCamera").onclick = (e) => { e.stopPropagation(); $("#cameraInput").click(); };
$("#dropzone").onclick = () => { if (!file) $("#fileInput").click(); };
$("#dropzone").onkeydown = (e) => { if (e.key === "Enter" && !file) $("#fileInput").click(); };
$("#fileInput").onchange = (e) => pick(e.target.files[0]);
$("#cameraInput").onchange = (e) => pick(e.target.files[0]);
$("#btnRemove").onclick = (e) => { e.stopPropagation(); reset(); };
["dragover", "dragenter"].forEach((t) => $("#dropzone").addEventListener(t, (e) => { e.preventDefault(); $("#dropzone").classList.add("over"); }));
["dragleave", "drop"].forEach((t) => $("#dropzone").addEventListener(t, (e) => { e.preventDefault(); $("#dropzone").classList.remove("over"); }));
$("#dropzone").addEventListener("drop", (e) => pick(e.dataTransfer.files[0]));

/* ---- analysis ---- */
let stageTimer;
function startStages() {
  const li = [...document.querySelectorAll("#stages li")]; let i = 0;
  const paint = () => li.forEach((x, n) => { x.className = n < i ? "done" : n === i ? "on" : ""; });
  paint(); stageTimer = setInterval(() => { if (i < li.length - 1) { i++; paint(); } }, 1100);
}
$("#btnAnalyze").onclick = async (e) => {
  e.stopPropagation(); if (!file) return showError("Choose an image first.");
  showError(""); $("#result").hidden = true; $("#loading").hidden = false; startStages();
  try {
    const fd = new FormData(); fd.append("image", file);
    const res = await fetch(API_BASE + "/api/predict", { method: "POST", body: fd });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.success) throw new Error(data.error || "Analysis failed. Please try again.");
    showResult(data); saveHistory(data);
  } catch (err) {
    showError(err instanceof TypeError ? "Can't reach the analysis server. Check that the backend is running and try again." : err.message);
  } finally { clearInterval(stageTimer); $("#loading").hidden = true; }
};

function bars(entries) {
  return entries.map(([n, p]) => `<div class="b"><span>${n}</span><div><i style="width:${Math.max(p * 100, 1)}%"></i></div><span>${pct(p)}</span></div>`).join("");
}
function showResult(d) {
  const c = COPY[d.category];
  $("#statusCard").className = "status s-" + d.category;
  $("#rCategory").textContent = d.category.replace("_", " ");
  $("#rHeadline").textContent = c.headline;
  $("#rDisease").textContent = d.category === "HEALTHY" ? "No disease detected" : `Detected condition: ${d.predicted_disease}`;
  $("#rConf").textContent = pct(d.confidence);
  $("#rOrig").textContent = d.original_label; $("#rCat2").textContent = d.category; $("#rConf2").textContent = pct(d.confidence);
  const all = Object.entries(d.probabilities);
  $("#topBars").innerHTML = bars(all.filter(([, p], i) => i === 0 || p >= 0.01).slice(0, 3));
  $("#allBars").innerHTML = bars(all);
  $("#steps").innerHTML = c.steps.map((s) => `<li>${s}</li>`).join("");
  $("#result").hidden = false; $("#result").scrollIntoView({ behavior: "smooth" });
}

/* ---- history (localStorage; swap this object for an API/DB later) ---- */
const HistoryStore = {
  key: "tomatoguard.history.v1",
  all() { try { return JSON.parse(localStorage.getItem(this.key)) || []; } catch { return []; } },
  add(item) { try { localStorage.setItem(this.key, JSON.stringify([item, ...this.all()].slice(0, 30))); } catch {} },
  clear() { localStorage.removeItem(this.key); },
};
function thumb() {
  const c = document.createElement("canvas"); c.width = c.height = 96;
  const img = $("#previewImg"), s = Math.min(img.naturalWidth, img.naturalHeight);
  c.getContext("2d").drawImage(img, (img.naturalWidth - s) / 2, (img.naturalHeight - s) / 2, s, s, 0, 0, 96, 96);
  return c.toDataURL("image/jpeg", 0.7);
}
function saveHistory(d) { HistoryStore.add({ t: Date.now(), thumb: thumb(), disease: d.predicted_disease, category: d.category, confidence: d.confidence }); }
function dayLabel(t) {
  const d = new Date(t), n = new Date();
  if (d.toDateString() === n.toDateString()) return "Today";
  if (d.toDateString() === new Date(n - 864e5).toDateString()) return "Yesterday";
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}
function renderHistory() {
  const items = HistoryStore.all(), box = $("#historyList");
  if (!items.length) { box.innerHTML = `<p class="empty">No analyses yet. <a href="#detect">Analyze a leaf</a> and it will appear here.</p>`; return; }
  let last = "";
  box.innerHTML = items.map((h) => {
    const l = dayLabel(h.t), head = l !== last ? `<div class="hday">${l}</div>` : ""; last = l;
    return `${head}<div class="h"><img src="${h.thumb}" alt=""><div><strong>${h.disease}</strong><small>${new Date(h.t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</small></div><em class="chip ${h.category}">${h.category.replace("_DISEASE", "")}</em><strong>${pct(h.confidence)}</strong></div>`;
  }).join("");
}
$("#btnClear").onclick = () => { HistoryStore.clear(); renderHistory(); };
