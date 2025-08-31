// simple frontend to interact with backend
let currentUser = "";

async function doRegister(){
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  if(!username || !password){ alert("Bitte Benutzername und Passwort eingeben"); return; }
  let res = await fetch("http://localhost:8000/register", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({username, password})
  });
  const msg = document.getElementById("loginMsg");
  if(res.ok){ msg.innerText = "Account erstellt. Bitte einloggen."; }
  else { msg.innerText = "Fehler: " + (await res.text()); }
}

async function doLogin(){
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const otp = document.getElementById("otp").value.trim();
  if(!username || !password){ alert("Bitte Daten eingeben"); return; }
  let res = await fetch("http://localhost:8000/login",{
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({username, password, otp})
  });
  const msg = document.getElementById("loginMsg");
  if(res.ok){
    const data = await res.json();
    currentUser = username;
    msg.innerText = data.message;
    document.getElementById("who").innerText = currentUser;
    document.getElementById("loginBox").classList.add("hidden");
    document.getElementById("dashboard").classList.remove("hidden");
    if(data.is_admin) document.getElementById("adminPanel").classList.remove("hidden");
  } else {
    const err = await res.json().catch(()=>({detail:"Fehler"}));
    msg.innerText = err.detail || "Login fehlgeschlagen";
  }
}

function logout(){
  currentUser = "";
  document.getElementById("loginBox").classList.remove("hidden");
  document.getElementById("dashboard").classList.add("hidden");
  document.getElementById("adminPanel").classList.add("hidden");
}

async function loadChart(){
  const sym = document.getElementById("coin").value;
  const dashMsg = document.getElementById("dashMsg");
  dashMsg.innerText = "Lade Daten...";
  let res = await fetch(`http://localhost:8000/ohlc/${encodeURIComponent(sym)}`);
  if(!res.ok){ dashMsg.innerText = "Fehler beim Laden"; return; }
  const body = await res.json();
  // Very simple render: show last 5 closes and indicators
  const data = body.data;
  const idx = data.Date.length - 1;
  let html = "<h3>Letzte Werte</h3><ul>";
  for(let i=0;i<5 && i<data.Date.length;i++){
    const j = data.Date.length-1-i;
    html += `<li>${data.Date[j]} Close: ${data.Close[j].toFixed(2)} RSI: ${data.RSI[j].toFixed(2)}</li>`;
  }
  html += "</ul>";
  html += `<p>SL: ${data.SL[idx].toFixed(2)} TP: ${data.TP[idx].toFixed(2)}</p>`;
  document.getElementById("chartArea").innerHTML = html;
  dashMsg.innerText = "Daten geladen";
}

async function startBacktest(){
  const sym = document.getElementById("coin").value;
  const res = await fetch("http://localhost:8000/backtest", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({symbol: sym, period:"3mo", interval:"1h"})
  });
  if(!res.ok){ alert("Backtest fehlgeschlagen"); return; }
  const body = await res.json();
  alert("Backtest fertig. Letzter Preis: " + body.last_close);
}

async function exportLogs(){
  if(!currentUser){ alert("Bitte einloggen"); return; }
  const res = await fetch(`http://localhost:8000/export_logs/${encodeURIComponent(currentUser)}`);
  if(!res.ok){ alert("Keine Logs"); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${currentUser}_orders.csv`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

async function simulateAbo(){
  if(!currentUser){ alert("Bitte einloggen"); return; }
  const res = await fetch(`http://localhost:8000/pay/subscribe/simulate?username=${encodeURIComponent(currentUser)}&months=1`, {method:"POST"});
  if(res.ok) alert("Abo simuliert (1 Monat)");
  else alert("Fehler Abo");
}

// Admin functions
async function loadUsers(){
  const adminName = currentUser || prompt("Admin Username");
  const res = await fetch(`http://localhost:8000/admin/users?admin_username=${encodeURIComponent(adminName)}`);
  if(!res.ok){ alert("Admin Zugriff nötig"); return; }
  const data = await res.json();
  document.getElementById("userList").innerText = JSON.stringify(data, null, 2);
}

async function loadLogs(){
  const adminName = currentUser || prompt("Admin Username");
  const res = await fetch(`http://localhost:8000/admin/logs?admin_username=${encodeURIComponent(adminName)}`);
  if(!res.ok){ alert("Admin Zugriff nötig"); return; }
  const data = await res.text();
  document.getElementById("logList").innerText = data;
}
