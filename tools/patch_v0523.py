from pathlib import Path
import re

p=Path("index.html")
s=p.read_text(encoding="utf-8")

s=s.replace('content="0.5.2.2"','content="0.5.2.3"',1)
s=s.replace('UI Tiles · v0.5.2.2','Auto Resume Sync · v0.5.2.3',1)

old_const='DRIVE_FILE_NAME="BudgetFlow_Data.bfdb",LS_SYNC_STATE="budgetflow.syncstate.v1";'
new_const='DRIVE_FILE_NAME="BudgetFlow_Data.bfdb",LS_SYNC_STATE="budgetflow.syncstate.v1",LS_DRIVE_AUTO_RESUME="budgetflow.driveAutoResume.v1";'
if old_const not in s:
    raise SystemExit("Drive constants marker not found")
s=s.replace(old_const,new_const,1)

old_let='driveConnected=false,driveSyncInProgress=false,pendingCloudRestore=false;'
new_let='driveConnected=false,driveSyncInProgress=false,pendingCloudRestore=false,pendingUnlockResume=false;'
if old_let not in s:
    raise SystemExit("Drive state marker not found")
s=s.replace(old_let,new_let,1)

old_init = 'function setDriveStatus(t,c=false){$("fileStatus").textContent=t;$("storagePill").textContent=c?"☁ Google Drive Sync":"Sejf lokalny";$("googleBtn").textContent=c?"☁ Google Drive: połączony":"☁ Połącz Google Drive"}async function initGoogleTokenClient(){while(!window.google?.accounts?.oauth2)await new Promise(r=>setTimeout(r,100));if(!googleTokenClient)googleTokenClient=google.accounts.oauth2.initTokenClient({client_id:GOOGLE_CLIENT_ID,scope:GOOGLE_SCOPE,callback:async r=>{if(r.error)return toast(r.error);googleAccessToken=r.access_token;driveConnected=true;setDriveStatus("Połączono",true);if(pendingCloudRestore){pendingCloudRestore=false;await restoreFromCloud()}else await smartSyncAfterConnect()}});return googleTokenClient}'
new_init = '''function setDriveStatus(t,c=false){$("fileStatus").textContent=t;$("storagePill").textContent=c?"☁ Google Drive Sync":"Sejf lokalny";$("googleBtn").textContent=c?"☁ Google Drive: połączony":(localStorage.getItem(LS_DRIVE_AUTO_RESUME)==="1"?"☁ Wznów Google Drive":"☁ Połącz Google Drive")}
function rememberDriveConnection(){localStorage.setItem(LS_DRIVE_AUTO_RESUME,"1")}
function driveAutoResumeEnabled(){return localStorage.getItem(LS_DRIVE_AUTO_RESUME)==="1"}
function showRememberedDriveState(){if(driveAutoResumeEnabled()&&!driveConnected){$("storagePill").textContent="☁ Drive zapamiętany";$("googleBtn").textContent="☁ Wznów Google Drive";if($("fileStatus")&&$("fileStatus").textContent==="Google Drive niepołączony.")$("fileStatus").textContent="Google Drive skonfigurowany · zostanie wznowiony przy odblokowaniu sejfu."}}
async function initGoogleTokenClient(){while(!window.google?.accounts?.oauth2)await new Promise(r=>setTimeout(r,100));if(!googleTokenClient)googleTokenClient=google.accounts.oauth2.initTokenClient({client_id:GOOGLE_CLIENT_ID,scope:GOOGLE_SCOPE,callback:async r=>{if(r.error){pendingUnlockResume=false;setDriveStatus("Google Drive: wymagane ręczne wznowienie.",false);return toast(r.error)}googleAccessToken=r.access_token;driveConnected=true;rememberDriveConnection();setDriveStatus("Google Drive wznowiony · sprawdzam synchronizację…",true);if(pendingCloudRestore){pendingCloudRestore=false;await restoreFromCloud();return}if(pendingUnlockResume){pendingUnlockResume=false;if(currentPassword)await smartSyncAfterConnect();return}await smartSyncAfterConnect()}});return googleTokenClient}
function autoResumeDriveFromUnlock(){if(!driveAutoResumeEnabled())return false;if(!window.google?.accounts?.oauth2){showRememberedDriveState();return false}pendingUnlockResume=true;initGoogleTokenClient().then(()=>googleTokenClient.requestAccessToken({prompt:""})).catch(e=>{pendingUnlockResume=false;console.warn("Drive auto resume",e);setDriveStatus("Google Drive: nie udało się wznowić automatycznie.",false)});return true}'''
if old_init not in s:
    raise SystemExit("Google init block not found")
s=s.replace(old_init,new_init,1)

old_unlock = '$("unlockBtn").onclick=async()=>{const p=$("unlockPassword").value;let decoded;try{decoded=await decryptVault(JSON.parse(localStorage.getItem(LS_VAULT)),p)}catch(e){console.warn("Vault decrypt failed",e);toast("Nieprawidłowe hasło");return}data=decoded;currentPassword=p;sessionStorage.setItem(LS_SESSION,p);$("unlockModal").classList.remove("show");try{migrateData();render();fetchCryptoPrices(false)}catch(e){console.error("UI after unlock",e);toast("Hasło poprawne — błąd interfejsu")}};'
new_unlock = '$("unlockBtn").onclick=async()=>{const p=$("unlockPassword").value;const resumeRequested=autoResumeDriveFromUnlock();let decoded;try{decoded=await decryptVault(JSON.parse(localStorage.getItem(LS_VAULT)),p)}catch(e){console.warn("Vault decrypt failed",e);toast("Nieprawidłowe hasło");return}data=decoded;currentPassword=p;sessionStorage.setItem(LS_SESSION,p);$("unlockModal").classList.remove("show");try{migrateData();render();fetchCryptoPrices(false);if(driveConnected&&!pendingUnlockResume)smartSyncAfterConnect().catch(e=>console.warn("Drive sync after unlock",e));else if(resumeRequested)setDriveStatus("Sejf odblokowany · wznawiam Google Drive…",false)}catch(e){console.error("UI after unlock",e);toast("Hasło poprawne — błąd interfejsu")}};'
if old_unlock not in s:
    raise SystemExit("Unlock handler not found")
s=s.replace(old_unlock,new_unlock,1)

old_boot='async function boot(){$("txDate").value=new Date().toISOString().slice(0,10);'
new_boot='async function boot(){showRememberedDriveState();$("txDate").value=new Date().toISOString().slice(0,10);'
if old_boot not in s:
    raise SystemExit("Boot marker not found")
s=s.replace(old_boot,new_boot,1)

p.write_text(s,encoding="utf-8")
print("Patched index.html", len(s))
