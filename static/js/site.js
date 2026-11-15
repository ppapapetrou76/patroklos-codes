(function(){
  var root=document.documentElement, btn=document.getElementById('theme');
  try{var saved=localStorage.getItem('theme'); if(saved==='light'||saved==='dark'){root.setAttribute('data-theme',saved);}}catch(e){}
  btn.addEventListener('click',function(){
    var cur=root.getAttribute('data-theme');
    if(!cur){cur=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
    var next=cur==='dark'?'light':'dark';
    root.setAttribute('data-theme',next);
    try{localStorage.setItem('theme',next);}catch(e){}
  });
  var all=document.getElementById('toggle-all'), nodes=document.querySelectorAll('details.node');
  function label(){var allOpen=true; nodes.forEach(function(n){if(!n.open){allOpen=false;}}); all.textContent=allOpen?'Collapse all':'Expand all';}
  all.addEventListener('click',function(){var open=all.textContent==='Expand all'; nodes.forEach(function(n){n.open=open;}); label();});
  nodes.forEach(function(n){n.addEventListener('toggle',label);});
  function openTarget(){var id=location.hash.slice(1); if(!id){return;} var el=document.getElementById(id); if(el){var d=el.querySelector('details'); if(d){d.open=true;}}}
  window.addEventListener('hashchange',openTarget);
  document.querySelectorAll('.nav a[href^="#"]').forEach(function(a){a.addEventListener('click',function(){var el=document.getElementById(a.getAttribute('href').slice(1)); if(el){var d=el.querySelector('details'); if(d){d.open=true;}}});});
  openTarget();
})();
