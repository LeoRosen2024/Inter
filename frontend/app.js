const sidebar=document.querySelector('#sidebar'),menu=document.querySelector('#menuButton'),backdrop=document.querySelector('#backdrop'),modal=document.querySelector('#modal'),toast=document.querySelector('#toast');let timer;
const api=window.interApi,apiStatus=document.querySelector('#apiStatus');
let apiConnected=false,activeReelRecord=null,activeScriptRecord=null;
const reelRecordCache=new Map();
const demoReelEdits=new Map(),demoScriptBlocks={};
let settingsState={display_name:'Leo Rosen',email:'leo@beispiel.de',locale:'de',trend_notifications:true,autosave:true};
function setApiMode(connected){apiConnected=connected;apiStatus.textContent=connected?'Datenbank verbunden':'Demo-Modus · API offline';apiStatus.classList.toggle('api-online',connected);apiStatus.classList.toggle('api-offline',!connected)}
function formatCount(value){const number=Number(value)||0;if(number>=1000000)return`${(number/1000000).toLocaleString('de-DE',{maximumFractionDigits:1})}M`;if(number>=1000)return`${(number/1000).toLocaleString('de-DE',{maximumFractionDigits:1})}K`;return number.toLocaleString('de-DE')}
function formatDuration(value){const seconds=Math.max(0,Number(value)||0);return`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`}
function formatDate(value,index=0){if(!value)return`${index+1}. Aug.`;try{return new Intl.DateTimeFormat('de-DE',{day:'2-digit',month:'short'}).format(new Date(value))}catch{return`${index+1}. Aug.`}}
function statusLabel(value){return({online:'Online',draft:'Entwurf',planned:'Geplant'})[value]||value||'Entwurf'}
function notify(message){clearTimeout(timer);toast.querySelector('p').textContent=message;toast.classList.add('visible');timer=setTimeout(()=>toast.classList.remove('visible'),2600)}
function toggleMenu(force){const open=typeof force==='boolean'?force:!sidebar.classList.contains('open');sidebar.classList.toggle('open',open);backdrop.classList.toggle('visible',open);menu.setAttribute('aria-expanded',String(open));document.body.style.overflow=open?'hidden':''}
menu.addEventListener('click',()=>toggleMenu());backdrop.addEventListener('click',()=>toggleMenu(false));
const reels=[
  ['Hook in 3 Sekunden','@creatorlab','00:24','42,8K',98],['Storytelling-Formel','@socialtips','00:31','37,2K',91],['Content ohne Stress','@reelstudio','00:18','29,4K',86],['Die perfekte Caption','@marketingde','00:27','24,9K',79],['Mehr Reichweite','@growdaily','00:22','18,7K',72],
  ['5 Fehler bei Reels','@contentcoach','00:34','17,3K',70],['Der perfekte Einstieg','@hookmaster','00:19','16,8K',68],['Algorithmus einfach erklärt','@digitalwissen','00:42','15,1K',65],['Mehr Kommentare erhalten','@communitypro','00:25','13,9K',63],['Reels richtig planen','@planstudio','00:29','12,6K',61],
  ['Licht für dein Video','@filmtipps','00:21','11,8K',59],['Schneller Videoschnitt','@editacademy','00:37','10,9K',57],['Ideen für jeden Tag','@ideenwerk','00:26','9,7K',54],['Call-to-Action Vorlage','@conversionlab','00:20','8,8K',52],['Trend-Audio finden','@soundscout','00:23','7,9K',49],
  ['Kamera richtig einstellen','@videosetup','00:32','7,1K',47],['Bessere Untertitel','@captionpro','00:28','6,4K',44],['Authentisch vor der Kamera','@creatorlife','00:39','5,8K',41],['Reels mehrfach verwenden','@contentflow','00:30','5,2K',38],['Deine Wochenstrategie','@socialplan','00:45','4,7K',35]
];
const reelList=document.querySelector('#reelList'),reelSearch=document.querySelector('#reelSearch'),emptyState=document.querySelector('#emptyState');
let selectedReelId='';
function renderReels(query=''){const normalized=query.trim().toLowerCase();const visible=reels.filter(reel=>`${reel[0]} ${reel[1]}`.toLowerCase().includes(normalized));reelList.innerHTML=visible.map((reel,index)=>`<button class="reel-row ${(selectedReelId&&reel[5]===selectedReelId)||(!selectedReelId&&index===0)?'selected':''}" data-reel-id="${escapeHtml(reel[5]||'')}" data-reel="${escapeHtml(reel[0])}" data-views="${escapeHtml(reel[3])}"><span class="thumb t${index%5+1}"><i></i></span><span><strong>${escapeHtml(reel[0])}</strong><small>${escapeHtml(reel[1])} · ${reel[2]}</small></span><button class="reel-open" type="button" data-open-selected aria-label="Reel öffnen">↗</button><em><b>${Math.round(reel[4])}%</b><i style="background:linear-gradient(90deg,#3e3d48 0 ${Math.round(reel[4])}%,#e1e1e5 ${Math.round(reel[4])}%)"></i></em></button>`).join('');emptyState.classList.toggle('visible',visible.length===0)}
renderReels();
reelSearch.addEventListener('input',()=>renderReels(reelSearch.value));
reelList.addEventListener('click',event=>{const row=event.target.closest('.reel-row');if(!row)return;const titleClick=event.target.closest('.reel-row strong');if(titleClick){event.preventDefault();openScriptForReel(row.dataset.reelId,row.dataset.reel);return}const openButton=event.target.closest('[data-open-selected]');if(openButton){event.preventDefault();openReel(row.dataset.reelId,row.dataset.reel,row.dataset.views,overviewContext);return}selectedReelId=row.dataset.reelId;reelList.querySelectorAll('.reel-row').forEach(item=>item.classList.toggle('selected',item===row));const title=document.querySelector('#selectedTitle'),views=document.querySelector('#selectedViews');if(title)title.textContent=row.dataset.reel||'';if(views)views.textContent=row.dataset.views||''});
async function openScriptForReel(reelId,title){
  detailReturnView=overviewContext;
  activeReelRecord=reelId?reelRecordCache.get(reelId)||null:null;
  if(apiConnected&&reelId){try{activeReelRecord=await api.getReel(reelId);reelRecordCache.set(reelId,activeReelRecord)}catch{notify('Reel konnte nicht geladen werden');return}}
  activeScriptRecord=activeReelRecord?.script||null;
  dashboardView.hidden=true;viewRoot.hidden=false;viewRoot.innerHTML=scriptWorkspaceTemplate();
  const scriptTitle=viewRoot.querySelector('.script-workspace-head h1');if(scriptTitle)scriptTitle.textContent=activeReelRecord?.title||title;const hookCopy=viewRoot.querySelector('[data-script-block=hook] .saved-copy');if(hookCopy)hookCopy.textContent=activeReelRecord?.transcript||activeReelRecord?.description||'Transcript wird über die Schaltfläche im Reel-Detail geladen.';
  document.querySelectorAll('.nav-item').forEach(link=>link.classList.toggle('active',link.dataset.view==='scripts'));
  history.replaceState(null,'','#scripts');toggleMenu(false);
}
const dashboardView=document.querySelector('#dashboardView'),viewRoot=document.querySelector('#viewRoot');
const myReels=[['5 Content-Ideen für diese Woche','Heute, 10:24','Entwurf','draft','—','—'],['Warum dein Hook nicht funktioniert','Gestern, 18:42','Online','online','18,2K','1.309'],['Behind the Scenes: Mein Setup','27. Aug., 14:10','Online','online','31,7K','2.408'],['Die perfekte Caption schreiben','26. Aug., 09:35','Geplant','planned','—','—'],['Meine Wochenroutine','25. Aug., 17:20','Online','online','24,1K','1.862'],['3 Schnitt-Tricks für Anfänger','24. Aug., 12:05','Online','online','46,8K','3.711'],['Reichweite ohne Werbung','23. Aug., 08:48','Entwurf','draft','—','—'],['Content-Plan für September','22. Aug., 16:30','Geplant','planned','—','—'],['Hook in 3 Sekunden','21. Aug., 11:18','Online','online','42,8K','3.214'],['Mein kompaktes Licht-Setup','20. Aug., 18:06','Online','online','35,4K','2.761'],['Vorher und nachher: Videoschnitt','19. Aug., 13:44','Online','online','29,9K','2.118'],['So finde ich Trend-Audios','18. Aug., 09:12','Online','online','27,3K','1.984'],['Mehr Kommentare mit einer Frage','17. Aug., 17:55','Entwurf','draft','—','—'],['Untertitel, die gelesen werden','16. Aug., 12:20','Online','online','23,6K','1.742'],['Meine Kamera-Einstellungen','15. Aug., 08:36','Online','online','21,8K','1.559'],['Storytelling in 30 Sekunden','14. Aug., 19:08','Geplant','planned','—','—'],['Reels mehrfach verwenden','13. Aug., 14:28','Online','online','18,9K','1.306'],['Call to Action ohne Druck','12. Aug., 10:42','Online','online','17,4K','1.141'],['Drei Ideen gegen Content-Stress','11. Aug., 16:14','Entwurf','draft','—','—'],['Meine Wochenstrategie','10. Aug., 09:05','Online','online','14,7K','986']];
function reelRows(){return myReels.map(r=>`<div class="table-row" data-open-reel data-reel-id="${escapeHtml(r[6]||'')}" data-title="${escapeHtml(r[0])}" data-views="${escapeHtml(r[4])}"><div class="item-main"><span class="item-thumb">▶</span><span><strong>${escapeHtml(r[0])}</strong><small>${escapeHtml(r[1])}</small></span></div><span class="status ${r[3]}">${escapeHtml(r[2])}</span><span>${escapeHtml(r[4])}</span><span>${escapeHtml(r[5])}</span><button class="row-action" data-action="options">•••</button></div>`).join('')}
const scripts=[['Hook-Bibliothek für Trends','Heute, 11:05','86 Wörter','Entwurf'],['Warum dein Reel nicht wächst','Gestern, 17:30','124 Wörter','Fertig'],['Behind the Scenes','25. Aug.','98 Wörter','Fertig'],['Content-Ideen im September','22. Aug.','142 Wörter','Entwurf'],['Storytelling in 30 Sekunden','18. Aug.','105 Wörter','Fertig']];
const scriptRows=scripts.map((s,i)=>`<div class="table-row"><div class="item-main"><span class="item-thumb">▤</span><span><strong>${s[0]}</strong><small>${s[1]}</small></span></div><span class="status ${s[3]==='Fertig'?'online':'draft'}">${s[3]}</span><span>${s[2]}</span><span>${i%2?'00:35':'00:28'}</span><button class="row-action" data-action="options">•••</button></div>`).join('');
const competitorItems=[['CL','Creator Lab','@creatorlab','284K','4,8M','8,7%'],['ST','Social Tipps','@socialtipps','196K','3,1M','7,9%'],['RS','Reel Studio','@reelstudio','142K','2,4M','9,2%'],['MD','Marketing DE','@marketingde','98K','1,7M','6,8%'],['GD','Grow Daily','@growdaily','76K','1,2M','8,1%'],['CC','Content Coach','@contentcoach','64K','980K','7,4%'],['HM','Hook Master','@hookmaster','58K','902K','8,4%'],['EA','Edit Academy','@editacademy','53K','844K','7,8%'],['CW','Caption Werk','@captionwerk','49K','791K','8,0%'],['SP','Social Plan','@socialplan','46K','738K','7,6%'],['VS','Video Setup','@videosetup','43K','694K','7,2%'],['SW','Story Werk','@storywerk','39K','641K','8,9%'],['TS','Trend Scout','@trendscout','36K','598K','9,1%'],['CM','Creator Mind','@creatormind','34K','552K','7,7%'],['RL','Reels Lab','@reelslab','31K','514K','8,3%'],['DA','Digital Alltag','@digitalalltag','29K','477K','7,5%'],['MF','Marketing Flow','@marketingflow','27K','438K','8,2%'],['VP','Video Praxis','@videopraxis','24K','392K','7,1%'],['IG','Ideen Garage','@ideengarage','22K','351K','8,6%'],['MP','Media Pro','@mediapro','19K','306K','7,3%']];
function competitorCards(){return competitorItems.map(c=>`<article class="competitor"><div class="competitor-top"><span class="competitor-avatar">${escapeHtml(c[0])}</span><div><strong>${escapeHtml(c[1])}</strong><small>${escapeHtml(c[2])}</small></div><span class="trend-up">↗ aktiv</span></div><div class="competitor-stats"><div><span>Follower</span><strong>${escapeHtml(c[3])}</strong></div><div><span>Aufrufe</span><strong>${escapeHtml(c[4])}</strong></div><div><span>Engagement</span><strong>${escapeHtml(c[5])}</strong></div></div></article>`).join('')}

const views={
reels:()=>`<div class="page-view reels-page"><header class="page-top"><div><small>DEINE INHALTE</small><h1>Meine Reels</h1><p>Plane, bearbeite und analysiere alle deine Kurzvideos.</p></div><div class="page-actions"><button class="ui-button" data-action="import">Importieren</button><button class="ui-button primary-action" data-action="new">＋ Neues Reel</button></div></header><div class="filter-bar"><label>⌕<input data-filter="rows" placeholder="Reels durchsuchen ..."></label><button class="filter-chip active">Alle 20</button><button class="filter-chip">Online</button><button class="filter-chip">Entwürfe</button></div><section class="table-panel"><div class="table-head"><span>REEL</span><span>STATUS</span><span>AUFRUFE</span><span>LIKES</span><span></span></div>${reelRows()}</section></div>`,
scripts:`<div class="page-view"><header class="page-top"><div><small>TEXTWERKSTATT</small><h1>Skripte</h1><p>Entwickle Hooks, Geschichten und klare Handlungsaufforderungen.</p></div><div class="page-actions"><button class="ui-button">Vorlagen</button><button class="ui-button primary-action" data-action="new-script">＋ Neues Skript</button></div></header><div class="editor-layout"><section class="editor-panel"><header><h2>Aktueller Entwurf</h2><div class="editor-tools"><button>B</button><button><i>I</i></button><button>☷</button></div></header><div class="editor-text" contenteditable="true"><h3>Warum dein Reel nicht wächst</h3><p><strong>HOOK</strong><br>Du machst diesen einen Fehler bei deinen Reels – und merkst es nicht einmal.</p><p><strong>HAUPTTEIL</strong><br>Viele Creator starten direkt mit der Erklärung. Beginne stattdessen mit dem Ergebnis, das dein Publikum erreichen möchte.</p><p><strong>CALL TO ACTION</strong><br>Speichere dieses Reel und teste den Hook bei deinem nächsten Video.</p></div><button class="ui-button primary-action" data-action="save">Skript speichern</button></section><aside class="side-stack"><div class="info-panel"><h3>Skript-Details</h3><div class="info-row"><span>Wörter</span><strong>86</strong></div><div class="info-row"><span>Dauer</span><strong>ca. 28 Sek.</strong></div><div class="info-row"><span>Fortschritt</span><strong>72%</strong></div></div><div class="info-panel"><h3>Letzte Skripte</h3>${scripts.slice(0,3).map(s=>`<div class="info-row"><span>${s[0]}</span><strong>→</strong></div>`).join('')}</div></aside></div><section class="table-panel"><div class="table-head"><span>SKRIPT</span><span>STATUS</span><span>UMFANG</span><span>DAUER</span><span></span></div>${scriptRows}</section></div>`,
competitors:()=>`<div class="page-view competitors-page"><header class="page-top"><div><small>MARKTBEOBACHTUNG</small><h1>Wettbewerber</h1><p>Vergleiche Reichweite, Wachstum und erfolgreiche Formate.</p></div><div class="page-actions"><button class="ui-button primary-action" data-action="add-competitor">＋ Wettbewerber</button></div></header><div class="filter-bar"><label>⌕<input data-filter="competitors" placeholder="Wettbewerber suchen ..."></label><button class="filter-chip active">Alle 20</button><button class="filter-chip">Wachsend</button></div><div class="competitor-grid" data-competitor-grid>${competitorCards()}</div></div>`,
settings:()=>`<div class="page-view settings-page"><header class="page-top"><div><small>KONTO & APP</small><h1>Einstellungen</h1><p>Verwalte Profil, Benachrichtigungen und Arbeitsbereich.</p></div><div class="page-actions"><button class="ui-button primary-action" data-action="save">Änderungen speichern</button></div></header><div class="settings-layout"><nav class="settings-menu"><button class="active">Profil</button><button>Benachrichtigungen</button><button>Integrationen</button><button>Sicherheit</button></nav><section class="settings-panel"><h2>Profil</h2><p>Deine persönlichen Informationen und Standardeinstellungen.</p><div class="form-row"><label><strong>Anzeigename</strong><small>Sichtbar in deinem Arbeitsbereich</small></label><input data-setting="display_name" value="${escapeHtml(settingsState.display_name)}"></div><div class="form-row"><label><strong>E-Mail</strong><small>Adresse für Benachrichtigungen</small></label><input data-setting="email" type="email" value="${escapeHtml(settingsState.email)}"></div><div class="form-row"><label><strong>Sprache</strong><small>Sprache der Benutzeroberfläche</small></label><select data-setting="locale"><option value="de" ${settingsState.locale==='de'?'selected':''}>Deutsch</option><option value="en" ${settingsState.locale==='en'?'selected':''}>English</option></select></div><div class="form-row"><label><strong>Trend-Benachrichtigungen</strong><small>Wöchentliche Empfehlungen erhalten</small></label><button class="toggle ${settingsState.trend_notifications?'on':''}" data-toggle data-setting="trend_notifications"><i></i></button></div><div class="form-row"><label><strong>Auto-Speichern</strong><small>Skripte automatisch sichern</small></label><button class="toggle ${settingsState.autosave?'on':''}" data-toggle data-setting="autosave"><i></i></button></div></section></div></div>`
};

let detailReturnView='dashboard',overviewContext='dashboard';
function getSavedReel(title){return demoReelEdits.get(title)||{}}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[char]))}
function scriptWorkspaceTemplate(){
  const fallback={hook:'Die meisten Reels scheitern an genau diesen drei Fehlern ...',body:'Fehler Nr. 1 — ein langweiliger Hook. Wenn du in den ersten 1–2 Sekunden nicht fesselst, wird weitergescrollt.\n\nFehler Nr. 2 — zu viel Einleitung. Menschen schauen sich lange Erklärungen nicht bis zum Ende an.\n\nFehler Nr. 3 — kein klares CTA. Ohne Handlungsaufforderung gibt es weder Likes noch neue Follower.',call_to_action:'Speichere dieses Reel, damit du diese Fehler nicht wiederholst. Folge uns für weitere praktische Reels-Tipps.'};
  const current=activeScriptRecord||fallback;
  const contentFor=(key)=>demoScriptBlocks[key]||current[key]||fallback[key];
  const block=(key,field,title,comment,author,time)=>`<article class="reference-script-block" data-script-block="${key}" data-script-field="${field}"><header><div><h2>${title}</h2><small>Redaktionsblock</small></div><button data-script-block-edit>✎ Bearbeiten</button></header><div class="reference-block-editor" data-script-block-content><p class="saved-copy">${escapeHtml(contentFor(field)).replace(/\n/g,'<br>')}</p></div><footer><small>⌁ Kommentar</small><p>${comment}</p><span>— ${author}<b>${time}</b></span></footer></article>`;
  const sourceHandle=activeReelRecord?.source_handle||'@reels.master';
  const sourceViews=activeReelRecord?formatCount(activeReelRecord.views_count):'1,2M';
  const sourceLikes=activeReelRecord?formatCount(activeReelRecord.likes_count):'14,2K';
  return `<div class="page-view script-reference-page" data-script-version="${current.version||1}"><header class="script-workspace-head"><div><small>ÜBERSICHT / KI-ANALYSE / ERFOLGREICHE REELS</small><h1>3 Fehler, die deine Reichweite zerstören</h1></div><div><button data-script-action="export">↗ Exportieren⌄</button><button class="remix-button" data-script-action="remix">Remix</button><button data-script-action="more">•••</button></div></header><div class="script-reference-layout"><main class="script-block-list">${block('hook','hook','Hook','Starker Einstieg. Funktioniert gut durch Kontrast und Neugier.','Alex','vor 2 Std.')} ${block('script','body','Skript','Die Struktur ist klar. Beispiele noch etwas konkreter machen.','Maja','vor 1 Std.')} ${block('cta','call_to_action','Call to Action','Kurz, verständlich und handlungsorientiert.','Leo','vor 20 Min.')}</main><aside class="source-panel"><h2>Quelle</h2><p>${escapeHtml(sourceHandle)}<br><span>12. Mai 2026</span></p><div class="source-cover"><strong>3</strong><b>FEHLER,<br>DIE DEINE<br>REICHWEITE<br>ZERSTÖREN</b></div><div class="source-stats"><span>▷ ${sourceViews}</span><span>♡ ${sourceLikes}</span></div><div class="source-meta"><h3>Tags</h3><div><span>Fehler</span><span>Reels</span><span>Reichweite</span></div><h3>Dauer</h3><p>00:28</p></div></aside></div></div>`
}
views.scripts=scriptWorkspaceTemplate();
function reelDetailTemplate(record,title,views){
  const saved=getSavedReel(title),scriptRecord=record?.script;
  const displayTitle=saved.title||record?.title||title;
  const description=saved.description||record?.description||'So fesselst du deine Zuschauer in den ersten drei Sekunden und führst sie sicher durch deine Story.';
  const script=saved.script||scriptRecord?.body||'Hallo! Heute sprechen wir über Trends. Starte mit einem starken Hook, zeige sofort den wichtigsten Nutzen und führe dein Publikum Schritt für Schritt durch die Story ...';
  const viewsText=record?formatCount(record.views_count):(views||'42,8K'),likesText=record?formatCount(record.likes_count):'3,2K',commentsText=record?formatCount(record.comments_count):'1,2K';
  const growth=record?Number(record.growth_percent||0).toLocaleString('de-DE',{maximumFractionDigits:1}):'1,5';
  return `<div class="page-view detail-page" data-reel-id="${escapeHtml(record?.id||'')}" data-version="${record?.version||1}" data-script-version="${scriptRecord?.version||1}" data-original-title="${escapeHtml(displayTitle)}" data-source-title="${escapeHtml(title)}"><div class="detail-toolbar"><button class="back-button" data-detail-back>← Zurück</button><span>REEL-DETAILS</span><button class="detail-edit" data-detail-edit>Bearbeiten</button><div class="detail-save-actions" hidden><button data-detail-cancel>Abbrechen</button><button class="save" data-detail-save>Speichern</button></div></div><section class="detail-grid"><article class="detail-card detail-video"><header><h1>Beliebtes Reel</h1><span class="detail-status">${escapeHtml(statusLabel(record?.status||'online'))}</span></header><div class="detail-video-frame"><div class="detail-person"></div><button class="detail-play" data-detail-play>▶</button><span>${formatDuration(record?.duration_seconds||30)}</span></div><div class="detail-video-copy"><h2 data-edit-field="title">${escapeHtml(displayTitle)}</h2><p data-edit-field="description">${escapeHtml(description)}</p><div><span>Trends</span><span>Tipps</span><strong>◉ ${viewsText}　♡ ${likesText}</strong></div></div></article><article class="detail-card detail-script"><header><h1>Skript</h1><span class="saved"><i></i>Gespeichert</span></header><div class="detail-script-copy"><span>“</span><p data-edit-field="script">${escapeHtml(script)}</p></div><div class="detail-script-bottom"><small>FORTSCHRITT <b>72%</b></small><div><i></i></div><button data-detail-edit>Bearbeiten</button></div></article><article class="detail-card detail-analytics"><header><h1>Analyse</h1><span>30 Tage</span></header><div class="detail-metrics"><div><span>Aufrufe</span><strong>${viewsText}</strong></div><div><span>Likes</span><strong>${likesText}</strong></div><div><span>Kommentare</span><strong>${commentsText}</strong></div><div><span>Wachstum</span><strong>↑ ${growth}%</strong></div></div><div class="detail-chart"><svg viewBox="0 0 500 110" preserveAspectRatio="none"><path d="M0 96L42 90L75 75L108 81L142 64L172 72L215 51L250 60L286 42L320 50L355 31L391 39L430 20L462 25L500 9"/></svg></div></article></section></div>`
}function mountTranscriptControl(){
  const card=viewRoot.querySelector('.detail-video-copy');
  if(!card||card.querySelector('[data-action="transcript"]'))return;
  const transcript=activeReelRecord?.transcript||'';
  card.insertAdjacentHTML('beforeend',`<button class="transcript-button" data-action="transcript">${transcript?'Transcript aktualisieren':'Получить transcript'}</button>${transcript?`<div class="detail-transcript"><strong>Transcript</strong><p>${escapeHtml(transcript)}</p></div>`:''}`);
}
async function openReel(reelId,title,views,returnView='dashboard'){
  detailReturnView=returnView;
  activeReelRecord=reelId?reelRecordCache.get(reelId)||null:null;
  sessionStorage.setItem('inter:lastReel',JSON.stringify({reelId,title,views,returnView}));
  dashboardView.hidden=true;viewRoot.hidden=false;viewRoot.innerHTML=reelDetailTemplate(activeReelRecord,title,views);mountTranscriptControl();
  document.querySelectorAll('.nav-item').forEach(link=>link.classList.remove('active'));history.replaceState(null,'','#reel');toggleMenu(false);
  if(apiConnected&&reelId){
    try{
      const record=await api.getReel(reelId);reelRecordCache.set(record.id,record);activeReelRecord=record;
      if(location.hash==='#reel'&&viewRoot.querySelector('.detail-page')){viewRoot.innerHTML=reelDetailTemplate(record,title,views);mountTranscriptControl()}
    }catch{notify('Reel konnte nicht aus der Datenbank geladen werden')}
  }
}
function setDetailEditing(editing){const page=viewRoot.querySelector('.detail-page');if(!page)return;page.classList.toggle('editing',editing);page.querySelectorAll('[data-edit-field]').forEach(field=>{field.contentEditable=String(editing);field.setAttribute('spellcheck','true')});page.querySelectorAll('[data-detail-edit]').forEach(button=>button.hidden=editing);page.querySelector('.detail-save-actions').hidden=!editing;if(editing){page.dataset.snapshot=JSON.stringify([...page.querySelectorAll('[data-edit-field]')].map(field=>field.innerText));page.querySelector('[data-edit-field="title"]').focus()}}
function showView(name,updateHash=true){const usesOverview=name==='dashboard'||name==='trends';dashboardView.hidden=!usesOverview;viewRoot.hidden=usesOverview;if(usesOverview){overviewContext=name;document.querySelector('[data-overview-title]').textContent=name==='trends'?'Trend-Reels':'Beliebte Reels';dashboardView.setAttribute('aria-label',name==='trends'?'Trend-Reels Dashboard':'Reels Dashboard')}else{const template=views[name]||views.reels;viewRoot.innerHTML=name==='scripts'?scriptWorkspaceTemplate():(typeof template==='function'?template():template)}document.querySelectorAll('.nav-item').forEach(link=>link.classList.toggle('active',link.dataset.view===name));if(updateHash)history.replaceState(null,'',`#${name}`);toggleMenu(false)}
document.querySelectorAll('.nav-item').forEach(item=>item.addEventListener('click',event=>{event.preventDefault();showView(item.dataset.view)}));
document.querySelectorAll('.brand,.mobile-header a').forEach(link=>link.addEventListener('click',event=>{event.preventDefault();showView('dashboard')}));
async function saveSettings(){
  const page=viewRoot.querySelector('.settings-page');if(!page)return;
  const next={
    display_name:page.querySelector('[data-setting="display_name"]').value.trim(),
    email:page.querySelector('[data-setting="email"]').value.trim(),
    locale:page.querySelector('[data-setting="locale"]').value,
    trend_notifications:page.querySelector('[data-setting="trend_notifications"]').classList.contains('on'),
    autosave:page.querySelector('[data-setting="autosave"]').classList.contains('on')
  };
  try{settingsState=apiConnected?await api.updateSettings(next):{...settingsState,...next};notify(apiConnected?'Einstellungen in der Datenbank gespeichert':'Nur für diese Demo-Sitzung gespeichert')}
  catch(error){notify(error.status===409?'Einstellungen wurden parallel geändert':'Einstellungen konnten nicht gespeichert werden')}
}
async function startApifyImport(){
  if(!apiConnected){notify('Apify-Import benötigt den lokalen Backend-Stack');return}
  try{
    const config=await api.getApifyConfiguration();
    if(!config.configured){notify('Apify ist vorbereitet – Token und Actor ID fehlen noch');return}
    const sourceUrl=window.prompt('Instagram-Profil-URL oder Reel-Link (Profil-URL spart einen zusätzlichen Apify-Lauf):');if(!sourceUrl)return;
    const job=await api.createApifyImport({source_url:sourceUrl,limit:20});notify('Import gestartet – die letzten 20 Reels werden geladen …');
    for(let attempt=0;attempt<36;attempt++){
      await new Promise(resolve=>setTimeout(resolve,5000));
      const current=await api.getImport(job.id);
      if(current.status==='succeeded'){await hydrateBackend();showView('trends');notify(`${current.result_count||0} Reels des Wettbewerbers wurden importiert`);return}
      if(current.status==='failed'){notify('Apify-Import fehlgeschlagen – Details stehen im Backend');return}
    }
    notify('Import läuft länger als erwartet – Liste wird nach Abschluss aktualisiert')
  }catch{notify('Apify-Import konnte nicht gestartet werden')}
}async function requestTranscript(){
  if(!apiConnected||!activeReelRecord?.source_url){notify('Für diesen Reel ist keine Quelle hinterlegt');return}
  try{const job=await api.createApifyImport({source_url:activeReelRecord.source_url,limit:1,actor_input:{username:[activeReelRecord.source_url],resultsLimit:1,includeTranscript:true,includeDownloadedVideo:false}});notify('Transcript wird geladen …');for(let i=0;i<36;i++){await new Promise(r=>setTimeout(r,3000));const current=await api.getImport(job.id);if(current.status==='succeeded'){activeReelRecord=await api.getReel(activeReelRecord.id);reelRecordCache.set(activeReelRecord.id,activeReelRecord);viewRoot.innerHTML=reelDetailTemplate(activeReelRecord,activeReelRecord.title,'');mountTranscriptControl();notify('Transcript wurde geladen');return}if(current.status==='failed'){notify('Transcript konnte nicht geladen werden');return}}}catch{notify('Transcript konnte nicht angefordert werden')}}
viewRoot.addEventListener('click',async event=>{
  const action=event.target.closest('[data-action]')?.dataset.action;
  if(action){
    if(action==='new')modal.showModal();
    else if(action==='new-script')notify('Neues Skript wurde angelegt');
    else if(action==='save')await saveSettings();
    else if(action==='import')await startApifyImport();
    else if(action==='transcript')await requestTranscript();
    else if(action==='add-competitor')notify('Wettbewerber kann jetzt hinzugefügt werden');
    else if(action==='options')notify('Weitere Optionen geöffnet');
    return;
  }
  const open=event.target.closest('[data-open-reel]');
  if(open){openReel(open.dataset.reelId,open.dataset.title,open.dataset.views,location.hash.replace('#','')||'trends');return}
  if(event.target.closest('[data-detail-back]')){showView(detailReturnView);return}
  if(event.target.closest('[data-detail-edit]')){setDetailEditing(true);return}
  if(event.target.closest('[data-detail-cancel]')){
    const page=viewRoot.querySelector('.detail-page'),snapshot=JSON.parse(page.dataset.snapshot||'[]');
    page.querySelectorAll('[data-edit-field]').forEach((field,index)=>field.innerText=snapshot[index]||'');setDetailEditing(false);notify('Änderungen verworfen');return;
  }
  if(event.target.closest('[data-detail-save]')){
    const page=viewRoot.querySelector('.detail-page'),fields=[...page.querySelectorAll('[data-edit-field]')].map(field=>field.innerText.trim());
    const data={title:fields[0]||page.dataset.originalTitle,description:fields[1],script:fields[2]};
    try{
      if(apiConnected&&activeReelRecord?.id){
        const updated=await api.updateReel(activeReelRecord.id,{title:data.title,description:data.description,version:activeReelRecord.version});
        const scriptPayload={body:data.script};if(activeReelRecord.script?.version)scriptPayload.version=activeReelRecord.script.version;
        const updatedScript=await api.updateScript(activeReelRecord.id,scriptPayload);
        activeReelRecord={...updated,script:updatedScript};reelRecordCache.set(updated.id,activeReelRecord);
        notify('Reel und Skript in der Datenbank gespeichert');
      }else{
        demoReelEdits.set(page.dataset.sourceTitle,data);notify('Nur für diese Demo-Sitzung gespeichert');
      }
      sessionStorage.setItem('inter:lastReel',JSON.stringify({reelId:activeReelRecord?.id||'',title:page.dataset.sourceTitle,views:page.querySelector('.detail-metrics strong').innerText,returnView:detailReturnView}));
      setDetailEditing(false);page.querySelector('.saved').innerHTML='<i></i>Gespeichert';
    }catch(error){notify(error.status===409?'Neuere Version vorhanden – bitte Reel erneut öffnen':'Speichern in der Datenbank fehlgeschlagen')}
    return;
  }
  const play=event.target.closest('[data-detail-play]');
  if(play){play.classList.toggle('playing');play.textContent=play.classList.contains('playing')?'Ⅱ':'▶';notify(play.classList.contains('playing')?'Vorschau wird abgespielt':'Vorschau pausiert');return}
  const toggle=event.target.closest('[data-toggle]');if(toggle)toggle.classList.toggle('on');
  const chip=event.target.closest('.filter-chip');if(chip){chip.parentElement.querySelectorAll('.filter-chip').forEach(item=>item.classList.remove('active'));chip.classList.add('active')}
});
viewRoot.addEventListener('click',async event=>{const editButton=event.target.closest('[data-script-block-edit]');if(editButton){const block=editButton.closest('[data-script-block]'),content=block.querySelector('[data-script-block-content]'),editing=block.classList.toggle('editing');content.contentEditable=String(editing);editButton.textContent=editing?'✓ Speichern':'✎ Bearbeiten';if(editing){content.focus();notify(`${block.querySelector('h2').textContent} kann jetzt bearbeitet werden`)}else{const field=block.dataset.scriptField,value=content.innerText.trim();demoScriptBlocks[field]=value;try{if(apiConnected&&activeReelRecord?.id){const payload={[field]:value};if(activeScriptRecord?.version)payload.version=activeScriptRecord.version;activeScriptRecord=await api.updateScript(activeReelRecord.id,payload);notify(`${block.querySelector('h2').textContent} in der Datenbank gespeichert`)}else notify(`${block.querySelector('h2').textContent} nur für diese Demo-Sitzung gespeichert`)}catch(error){notify(error.status===409?'Neuere Skript-Version vorhanden':'Skript konnte nicht gespeichert werden')}}return}const scriptAction=event.target.closest('[data-script-action]')?.dataset.scriptAction;if(scriptAction==='export')notify('Export wird vorbereitet');else if(scriptAction==='remix')notify('Eine neue Remix-Version wurde erstellt');else if(scriptAction==='more')notify('Weitere Optionen geöffnet')});
viewRoot.addEventListener('input',event=>{const mode=event.target.dataset.filter;if(!mode)return;const query=event.target.value.toLowerCase();const selector=mode==='cards'?'.content-card':mode==='rows'?'.table-row':'.competitor';viewRoot.querySelectorAll(selector).forEach(item=>item.hidden=!item.textContent.toLowerCase().includes(query))});
const initialView=location.hash.replace('#','');if(['trends','reels','scripts','competitors','settings'].includes(initialView))showView(initialView,false);else if(initialView==='reel'){try{const last=JSON.parse(sessionStorage.getItem('inter:lastReel'));if(last)openReel(last.reelId||'',last.title,last.views,last.returnView)}catch{showView('dashboard',false)}}
document.querySelector('[data-edit]').addEventListener('click',()=>{const script=document.querySelector('#scriptContent');script.contentEditable='true';script.focus();notify('Du kannst das Skript jetzt bearbeiten')});
const periods=[{label:'7 Tage',values:['38,9K','2,1K','327','0,4%']},{label:'30 Tage',values:['152K','8,4K','1,2K','1,5%']},{label:'90 Tage',values:['428K','24K','3,7K','4,8%']}];let periodIndex=1;
document.querySelector('[data-period]').addEventListener('click',event=>{periodIndex=(periodIndex+1)%periods.length;const current=periods[periodIndex];event.currentTarget.textContent=`${current.label}⌄`;['views','likes','comments','growth'].forEach((key,index)=>document.querySelector(`[data-metric="${key}"]`).textContent=current.values[index]);notify(`Analyse: ${current.label}`)});
document.querySelectorAll('[data-toast]').forEach(button=>button.addEventListener('click',event=>{event.preventDefault();notify(button.dataset.toast)}));
document.querySelectorAll('[data-new]').forEach(button=>button.addEventListener('click',()=>modal.showModal()));document.querySelectorAll('[data-choice]').forEach(button=>button.addEventListener('click',()=>{modal.close();notify(`${button.dataset.choice} wurde ausgewählt`)}));modal.addEventListener('click',event=>{if(event.target===modal)modal.close()});document.addEventListener('keydown',event=>{if(event.key==='Escape')toggleMenu(false)});

async function hydrateBackend(){
  setApiMode(false);
  try{
    await api.health();
    const [trendResponse,mineResponse,competitorResponse,remoteSettings]=await Promise.all([
      api.listReels('trending',20),api.listReels('mine',20),api.listCompetitors(20),api.getSettings()
    ]);
    [...trendResponse.items,...mineResponse.items].forEach(record=>reelRecordCache.set(record.id,record));
    reels.splice(0,reels.length,...trendResponse.items.map(record=>[
      record.title,record.source_handle||'@instagram',formatDuration(record.duration_seconds),formatCount(record.views_count),record.trend_score,record.id,record.version
    ]));
    myReels.splice(0,myReels.length,...mineResponse.items.map((record,index)=>[
      record.title,formatDate(record.published_at,index),statusLabel(record.status),record.status,record.views_count?formatCount(record.views_count):'—',record.likes_count?formatCount(record.likes_count):'—',record.id,record.version
    ]));
    competitorItems.splice(0,competitorItems.length,...competitorResponse.items.map(record=>{
      const initials=record.display_name.split(/\s+/).map(part=>part[0]).join('').slice(0,2).toUpperCase();
      return[initials,record.display_name,`@${record.handle}`,formatCount(record.followers_count),formatCount(record.total_views_count),`${Number(record.engagement_rate).toLocaleString('de-DE',{maximumFractionDigits:1})}%`,record.id]
    }));
    settingsState={...settingsState,...remoteSettings};
    if(trendResponse.items[0]){
      activeReelRecord=await api.getReel(trendResponse.items[0].id);activeScriptRecord=activeReelRecord.script;reelRecordCache.set(activeReelRecord.id,activeReelRecord)
    }
    setApiMode(true);renderReels(reelSearch.value);
    if(reels[0]){document.querySelector('#selectedTitle').textContent=reels[0][0];document.querySelector('#selectedViews').textContent=reels[0][3]}
    const route=location.hash.replace('#','');
    if(['reels','scripts','competitors','settings'].includes(route))showView(route,false);
    else if(route==='reel'){
      const last=JSON.parse(sessionStorage.getItem('inter:lastReel')||'null');if(last)openReel(last.reelId||'',last.title,last.views,last.returnView)
    }
  }catch{setApiMode(false)}
}

hydrateBackend();
