// Size each dropdown to the option it shows, so the arrow sits right after the text
// in every browser and at every screen width.
(function(){
  var SEL='.fbar select,.tools select,td select,.add select';
  var probe=document.createElement('span');
  probe.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;left:-9999px;top:0';
  function fit(s){
    var o=s.options[s.selectedIndex]; if(!o) return;
    var cs=getComputedStyle(s);
    probe.style.font=cs.font; probe.style.letterSpacing=cs.letterSpacing;
    probe.textContent=o.textContent;
    var w=probe.offsetWidth+parseFloat(cs.paddingLeft)+parseFloat(cs.paddingRight)+parseFloat(cs.borderLeftWidth)+parseFloat(cs.borderRightWidth)+2;
    s.style.width=Math.ceil(w)+'px'; s.style.maxWidth='100%';
  }
  function all(){document.querySelectorAll(SEL).forEach(fit)}
  function start(){
    document.body.appendChild(probe); all();
    document.addEventListener('change',function(e){if(e.target.matches&&e.target.matches(SEL))fit(e.target)});
    var t;new MutationObserver(function(){clearTimeout(t);t=setTimeout(all,30)}).observe(document.body,{childList:true,subtree:true});
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(all);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
