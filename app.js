const sidebar=document.querySelector('#sidebar');
const menuButton=document.querySelector('#menuButton');
const backdrop=document.querySelector('#backdrop');
const modal=document.querySelector('#newReelModal');
const toast=document.querySelector('#toast');
let toastTimer;

function showToast(message){clearTimeout(toastTimer);toast.querySelector('p').textContent=message;toast.classList.add('visible');toastTimer=setTimeout(()=>toast.classList.remove('visible'),2600)}
function toggleMenu(force){const open=typeof force==='boolean'?force:!sidebar.classList.contains('open');sidebar.classList.toggle('open',open);backdrop.classList.toggle('visible',open);menuButton.setAttribute('aria-expanded',String(open));document.body.style.overflow=open?'hidden':''}

menuButton.addEventListener('click',()=>toggleMenu());
backdrop.addEventListener('click',()=>toggleMenu(false));

document.querySelectorAll('.nav-item').forEach(item=>item.addEventListener('click',event=>{const target=document.querySelector(item.getAttribute('href'));if(!target){event.preventDefault();showToast(`${item.dataset.placeholder} wird als Nächstes eingerichtet`)}document.querySelectorAll('.nav-item').forEach(link=>link.classList.remove('active'));item.classList.add('active');toggleMenu(false)}));

document.querySelector('[data-play]').addEventListener('click',event=>{const button=event.currentTarget;const playing=button.classList.toggle('playing');button.querySelector('span').textContent=playing?'Ⅱ':'▶';showToast(playing?'Vorschau wird abgespielt':'Vorschau pausiert')});

document.querySelector('[data-edit]').addEventListener('click',()=>{const script=document.querySelector('#scriptText');script.contentEditable='true';script.focus();showToast('Du kannst das Skript jetzt direkt bearbeiten')});

document.querySelector('[data-period-button]').addEventListener('click',event=>{const values=[['7 Tage','38,9K','2,1K','327'],['30 Tage','152K','8,4K','1,2K'],['90 Tage','428K','24K','3,7K']];const current=event.currentTarget.textContent.replace('⌄','');const index=(values.findIndex(item=>item[0]===current)+1)%values.length;const next=values[index];event.currentTarget.textContent=`${next[0]}⌄`;['views','likes','comments'].forEach((key,i)=>document.querySelector(`[data-value="${key}"]`).textContent=next[i+1]);showToast(`Analyse: ${next[0]}`)});

document.querySelectorAll('[data-toast]').forEach(button=>button.addEventListener('click',()=>showToast(button.dataset.toast)));
document.querySelectorAll('[data-new]').forEach(button=>button.addEventListener('click',()=>modal.showModal()));
document.querySelectorAll('[data-choice]').forEach(button=>button.addEventListener('click',()=>{modal.close();showToast(`${button.dataset.choice} wurde ausgewählt`)}));
modal.addEventListener('click',event=>{if(event.target===modal)modal.close()});
document.addEventListener('keydown',event=>{if(event.key==='Escape')toggleMenu(false)});
