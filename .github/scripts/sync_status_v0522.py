from pathlib import Path
p=Path("index.html")
s=p.read_text(encoding="utf-8")

s=s.replace('content="0.5.2.1"','content="0.5.2.2"',1)
s=s.replace('UI Tiles · v0.5.2.1','Sync Status · v0.5.2.2',1)

css_add='.balance-positive{color:#55d98a!important}.balance-negative{color:#ff6b7f!important}.balance-zero{color:#eef2ff!important}.sync-panel{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}.sync-detail{padding:11px 12px;border:1px solid rgba(255,255,255,.08);border-radius:12px;background:rgba(255,255,255,.025)}.sync-detail span{display:block;color:#8f9ab8;font-size:10px;margin-bottom:5px}.sync-detail b{font-size:12px}.sync-state-good{color:#66dda0}.sync-state-warn{color:#ffd166}.sync-state-bad{color:#ff6b7f}@media(max-width:760px){.sync-panel{grid-template-columns:1fr}}'
s=s.replace('</style>',css_add+'</style>',1)

old='<div class="file-status" id="fileStatus">Google Drive niepołączony.</div><div class="rowbtns"><button class="ghost" id="connectDriveBtn">Połącz Google Drive</button><button class="ghost" id="syncNowBtn">Synchronizuj teraz</button></div>'
new='<div class="file-status" id="fileStatus">Google Drive niepołączony.</div><div class="sync-panel"><div class="sync-detail"><span>Stan synchronizacji</span><b id="syncStateLabel">Niepołączony</b></div><div class="sync-detail"><span>Ostatnia synchronizacja</span><b id="lastSyncLabel">—</b></div><div class="sync-detail"><span>Lokalny sejf</span><b id="localSyncLabel">—</b></div><div class="sync-detail"><span>Google Drive</span><b id="cloudSyncLabel">—</b></div></div><div class="rowbtns" style="margin-top:12px"><button class="ghost" id="connectDriveBtn">Połącz Google Drive</button><button class="ghost" id="syncNowBtn">Synchronizuj teraz</button></div>'
if old not in s: raise SystemExit("settings block not found")
s=s.replace(old,new,1)

old='$("incomeStat").textContent=money(inc);$("expenseStat").textContent=money(exp);$("balanceStat").textContent=money(bal);$("fixedStat").textContent=money(fixed);'
new='$("incomeStat").textContent=money(inc);$("expenseStat").textContent=money(exp);$("balanceStat").textContent=money(bal);$("balanceStat").classList.remove("balance-positive","balance-negative","balance-zero");$("balanceStat").classList.add(bal>0?"balance-positive":bal<0?"balance-negative":"balance-zero");$("fixedStat").textContent=money(fixed);'
if old not in s: raise SystemExit("render balance block not found")
s=s.replace(old,new,1)

old='function getSyncState(){try{return JSON.parse(localStorage.getItem(LS_SYNC_STATE)||"null")}catch{return null}}function saveSyncState(s){localStorage.setItem(LS_SYNC_STATE,JSON.stringify(s))}'
new='function getSyncState(){try{return JSON.parse(localStorage.getItem(LS_SYNC_STATE)||"null")}catch{return null}}function fmtSyncTime(v){if(!v)return "—";const d=new Date(v);return Number.isNaN(d.getTime())?"—":d.toLocaleString("pl-PL")}function updateSyncPanel(stateText=null,stateClass=""){const st=getSyncState();const lv=JSON.parse(localStorage.getItem(LS_VAULT)||"null");if($("lastSyncLabel"))$("lastSyncLabel").textContent=fmtSyncTime(st?.syncedAt);if($("localSyncLabel"))$("localSyncLabel").textContent=fmtSyncTime(lv?.updatedAt);if($("cloudSyncLabel"))$("cloudSyncLabel").textContent=fmtSyncTime(st?.cloudUpdatedAt||driveFileMeta?.modifiedTime);if($("syncStateLabel")){const el=$("syncStateLabel");el.textContent=stateText||(driveConnected?"Połączony":"Niepołączony");el.className=stateClass}}function saveSyncState(st){localStorage.setItem(LS_SYNC_STATE,JSON.stringify(st));updateSyncPanel()}'
if old not in s: raise SystemExit("sync helper block not found")
s=s.replace(old,new,1)

old='function setDriveStatus(t,c=false){$("fileStatus").textContent=t;$("storagePill").textContent=c?"☁ Google Drive Sync":"Sejf lokalny";$("googleBtn").textContent=c?"☁ Google Drive: połączony":"☁ Połącz Google Drive"}'
new='function setDriveStatus(t,c=false){$("fileStatus").textContent=t;$("storagePill").textContent=c?"☁ Google Drive Sync":"Sejf lokalny";$("googleBtn").textContent=c?"☁ Google Drive: połączony":"☁ Połącz Google Drive";updateSyncPanel(c?"Połączony":"Niepołączony",c?"sync-state-good":"")}'
if old not in s: raise SystemExit("setDriveStatus block not found")
s=s.replace(old,new,1)

start=s.find('async function smartSyncAfterConnect(){')
end=s.find('async function restoreFromCloud()', start)
if start<0 or end<0: raise SystemExit("smartSync function markers not found")
smart='async function smartSyncAfterConnect(){await discoverDriveVault();const lv=JSON.parse(localStorage.getItem(LS_VAULT)||"null");if(!driveFileId){if(lv){await saveVaultToDrive(lv);setDriveStatus("Google Drive połączony · wysłano lokalny sejf",true);updateSyncPanel("Zsynchronizowano","sync-state-good");return "uploaded"}setDriveStatus("Google Drive połączony · brak sejfu do synchronizacji",true);updateSyncPanel("Brak danych","sync-state-warn");return "empty"}const cv=await downloadVaultFromDrive();if(!lv){setDriveStatus("Google Drive połączony · brak lokalnego sejfu",true);updateSyncPanel("Brak lokalnego sejfu","sync-state-warn");return "no-local"}const last=getSyncState(),lu=lv.updatedAt,cu=cv.updatedAt;if(last){const lc=lu!==last.localUpdatedAt,cc=cu!==last.cloudUpdatedAt;if(lc&&cc){$("conflictModal").classList.add("show");setDriveStatus("Konflikt synchronizacji — wymagana decyzja",true);updateSyncPanel("Konflikt","sync-state-warn");return "conflict"}if(cc&&!lc){await applyCloudVault(cv);saveSyncState({localUpdatedAt:cu,cloudUpdatedAt:cu,syncedAt:new Date().toISOString()});setDriveStatus("Pobrano nowszy sejf z Google Drive",true);updateSyncPanel("Zsynchronizowano","sync-state-good");return "downloaded"}if(lc&&!cc){await saveVaultToDrive(lv);setDriveStatus("Wysłano nowszy sejf na Google Drive",true);updateSyncPanel("Zsynchronizowano","sync-state-good");return "uploaded"}}if(Date.parse(cu||0)>Date.parse(lu||0)){await applyCloudVault(cv);saveSyncState({localUpdatedAt:cu,cloudUpdatedAt:cu,syncedAt:new Date().toISOString()});setDriveStatus("Pobrano nowszy sejf z Google Drive",true);updateSyncPanel("Zsynchronizowano","sync-state-good");return "downloaded"}if(Date.parse(lu||0)>Date.parse(cu||0)){await saveVaultToDrive(lv);setDriveStatus("Wysłano nowszy sejf na Google Drive",true);updateSyncPanel("Zsynchronizowano","sync-state-good");return "uploaded"}saveSyncState({localUpdatedAt:lu,cloudUpdatedAt:cu,syncedAt:new Date().toISOString()});setDriveStatus("Dane są aktualne · lokalny sejf i Google Drive są zsynchronizowane",true);updateSyncPanel("Dane aktualne","sync-state-good");return "current"}'
s=s[:start]+smart+s[end:]

old='$("syncNowBtn").onclick=smartSyncAfterConnect;'
new='$("syncNowBtn").onclick=async()=>{if(!driveConnected||!googleAccessToken){toast("Najpierw połącz Google Drive");return}const b=$("syncNowBtn"),oldText=b.textContent;b.disabled=true;b.textContent="Synchronizowanie…";updateSyncPanel("Synchronizowanie…","sync-state-warn");try{const result=await smartSyncAfterConnect();if(result!=="conflict")toast(result==="current"?"Dane są już zsynchronizowane":"Synchronizacja zakończona")}catch(e){console.error("Manual sync",e);setDriveStatus("Błąd synchronizacji: "+(e.message||e),true);updateSyncPanel("Błąd synchronizacji","sync-state-bad");toast("Błąd synchronizacji")}finally{b.disabled=false;b.textContent=oldText}};'
if old not in s: raise SystemExit("syncNow handler not found")
s=s.replace(old,new,1)

old='$("settingsBtn").onclick=()=>{$("dashboard").classList.add("hidden");$("settingsView").classList.remove("hidden")};'
new='$("settingsBtn").onclick=()=>{$("dashboard").classList.add("hidden");$("settingsView").classList.remove("hidden");updateSyncPanel()};'
if old not in s: raise SystemExit("settings handler not found")
s=s.replace(old,new,1)

p.write_text(s,encoding="utf-8")
print("patched", len(s))
