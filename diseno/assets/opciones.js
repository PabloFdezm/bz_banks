/* Additional proposals D–G. The shared source, formulas and full-history scales
   remain those in index.html. Only the explicitly labelled detail view is zoomed. */
let additionalReady=false;
let trailSignature='',trailIndex=0,trailTimer=null;
const clockMotionPreference=window.matchMedia('(prefers-reduced-motion: reduce)');

function focusBounds(points){
 const axis=key=>{
  const values=points.map(p=>p[key]),lo=Math.min(...values),hi=Math.max(...values);
  const span=Math.max(.4,hi-lo),pad=span*.22,step=span<=2?.1:span<=6?.5:1;
  return [Math.floor((lo-pad)/step)*step,Math.ceil((hi+pad)/step)*step];
 };
 const x=axis('x'),y=axis('y');
 return {xmin:x[0],xmax:x[1],ymin:y[0],ymax:y[1]};
}
function renderFocus(){
 const count=Number($('zoom-window').value),points=visible(),recent=points.slice(-count),bounds=focusBounds(recent);
 chart($('plot-d-context'),points,'readout-d-context',{mini:true,focusBox:bounds});
 chart($('plot-d-detail'),recent,'readout-d-detail',{mini:true,bounds});
 $('zoom-dates').textContent=recent[0].label+' a '+recent.at(-1).label+' · '+recent.length+' observaciones';
 $('zoom-scales').textContent='Escala propia · X: '+fmt(bounds.xmin)+' a '+fmt(bounds.xmax)+' pp · Y: '+fmt(bounds.ymin)+' a '+fmt(bounds.ymax)+' pp';
 $('focus-note').textContent='El recuadro discontinuo localiza el área ampliada. La lupa usa otra escala; las distancias visuales no se comparan con el resto. X: '+cfg().xTitle.toLowerCase()+'. Y: '+cfg().yTitle.toLowerCase()+'.';
}
function stopClockPlayback(){
 if(trailTimer!==null){clearInterval(trailTimer);trailTimer=null}
 const button=document.getElementById('trail-play');
 if(button){button.innerHTML=icon('M9 5l10 7-10 7Z')+'<span>Reproducir</span>';button.setAttribute('aria-pressed','false')}
}
function renderTrail(){
 const points=all().slice(Math.max(0,trailIndex-3),trailIndex+1),p=all()[trailIndex];
 chart($('plot-e'),points,'readout-e',{currentPoint:p});
 $('trail-date').textContent=p.label;
 $('trail-progress').textContent='Observación '+(trailIndex+1)+' de '+(end+1)+(trailIndex===end?' · cierre seleccionado':'');
 $('trail-range').max=end;$('trail-range').value=trailIndex;$('trail-range').setAttribute('aria-valuetext',p.label);
 $('trail-previous').disabled=trailIndex===0;$('trail-next').disabled=trailIndex===end;
 $('trail-play').disabled=end===0||clockMotionPreference.matches;
 $('trail-play').innerHTML=trailTimer===null?icon('M9 5l10 7-10 7Z')+'<span>Reproducir</span>':icon('M9 5v14M15 5v14')+'<span>Pausar</span>';
 $('trail-play').setAttribute('aria-pressed',String(trailTimer!==null));
 $('trail-note').textContent=clockMotionPreference.matches?'Movimiento reducido activo: recorre las fechas con los botones o el selector.':'Reproducción manual · una observación cada 1,2 segundos · sin interpolar ni suavizar los datos.';
}
function toggleClockPlayback(){
 if(trailTimer!==null){stopClockPlayback();renderTrail();return}
 if(clockMotionPreference.matches||end===0)return;
 if(trailIndex>=end)trailIndex=0;
 trailTimer=setInterval(()=>{
  if(trailIndex>=end){stopClockPlayback();renderTrail();return}
  trailIndex++;
  if(trailIndex===end)stopClockPlayback();
  renderTrail();
 },1200);
 renderTrail();
}
function drawTemporalSeries(host,key,points,onInspect){
 const lim=limits()[key],W=Math.max(240,Math.round(host.clientWidth||600)),H=208,m={l:48,r:24,t:20,b:40};
 const time=p=>Date.parse(p.date+'T00:00:00Z'),first=time(points[0]),last=time(points.at(-1));
 const tmin=first===last?first-86400000*180:first,tmax=first===last?last+86400000*180:last;
 const X=p=>m.l+(time(p)-tmin)/(tmax-tmin)*(W-m.l-m.r),Y=v=>m.t+(lim-v)/(2*lim)*(H-m.t-m.b);
 const unitName=key==='x'?cfg().xTitle:cfg().yTitle;
 let markup='<svg tabindex="0" role="group" aria-label="'+esc(unitName)+' a lo largo del tiempo. Usa las flechas para consultar una observación." aria-describedby="readout-f" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">';
 for(const value of [-lim,0,lim]){
  markup+='<line class="'+(value===0?'temporal-zero':'temporal-grid')+'" x1="'+m.l+'" x2="'+(W-m.r)+'" y1="'+Y(value)+'" y2="'+Y(value)+'"/>';
  markup+='<text x="'+(m.l-10)+'" y="'+(Y(value)+4)+'" text-anchor="end">'+fmt(value)+'</text>';
 }
 const indices=[...new Set(W<420?[0,points.length-1]:[0,Math.floor((points.length-1)/3),Math.floor((points.length-1)*2/3),points.length-1])];
 indices.forEach(i=>{
  const p=points[i],label=dataset==='ipca'?p.label:p.label.replace(' ',' · ');
  markup+='<text x="'+X(p)+'" y="'+(H-12)+'" text-anchor="'+(i===0?'start':i===points.length-1?'end':'middle')+'">'+esc(label)+'</text>';
 });
 markup+='<path class="temporal-path" d="'+points.map((p,i)=>(i?'L':'M')+X(p)+','+Y(p[key])).join(' ')+'"/>';
 points.forEach((p,i)=>{markup+='<circle class="temporal-point" cx="'+X(p)+'" cy="'+Y(p[key])+'" r="'+(i===points.length-1?5:3)+'"><title>'+esc(p.label)+': '+unit(p[key])+'</title></circle>'});
 const p=points.at(-1);
 markup+='<line class="temporal-cursor" x1="'+X(p)+'" x2="'+X(p)+'" y1="'+m.t+'" y2="'+(H-m.b)+'"/><circle class="temporal-halo" cx="'+X(p)+'" cy="'+Y(p[key])+'" r="6"/></svg>';
 host.innerHTML=markup;
 const svg=host.querySelector('svg'),line=svg.querySelector('.temporal-cursor'),dot=svg.querySelector('.temporal-halo');
 let activeIndex=points.length-1;
 const cursorTo=i=>{
  activeIndex=i;const p=points[i],x=X(p);
  line.setAttribute('x1',x);line.setAttribute('x2',x);
  dot.setAttribute('cx',x);dot.setAttribute('cy',Y(p[key]));
 };
 const nearest=ev=>{
  const box=svg.getBoundingClientRect(),x=(ev.clientX-box.left)*W/box.width;
  let n=0,d=Infinity;
  points.forEach((p,i)=>{const gap=Math.abs(X(p)-x);if(gap<d){d=gap;n=i}});
  return n;
 };
 svg.addEventListener('pointermove',ev=>{if(ev.pointerType!=='touch')onInspect(nearest(ev),ev)});
 svg.addEventListener('pointerleave',()=>{hideTooltip();onInspect(points.length-1)});
 svg.addEventListener('click',ev=>{onInspect(nearest(ev));hideTooltip()});
 svg.addEventListener('focus',()=>onInspect(activeIndex));
 svg.addEventListener('blur',hideTooltip);
 svg.addEventListener('keydown',ev=>{
  let i;
  if(ev.key==='ArrowLeft'||ev.key==='ArrowDown')i=Math.max(0,activeIndex-1);
  if(ev.key==='ArrowRight'||ev.key==='ArrowUp')i=Math.min(points.length-1,activeIndex+1);
  if(ev.key==='Home')i=0;
  if(ev.key==='End')i=points.length-1;
  if(ev.key==='Escape')hideTooltip();
  if(i!==undefined){ev.preventDefault();onInspect(i)}
 });
 return {cursorTo};
}
function renderTemporalSeries(){
 const points=visible(),controllers=[];
 const inspect=(i,ev)=>{
  controllers.forEach(controller=>controller.cursorTo(i));
  readout('readout-f',points[i]);$('series-date').textContent=points[i].label;
  if(ev)showTooltip(points[i],ev.clientX,ev.clientY);
 };
 controllers.push(drawTemporalSeries($('series-x'),'x',points,inspect));
 controllers.push(drawTemporalSeries($('series-y'),'y',points,inspect));
 $('series-x-label').textContent=cfg().xTitle+' · pp';
 $('series-y-label').textContent=cfg().yTitle+' · pp';
 $('series-zero-note').textContent=dataset==='ipca'?'Cero en X = inflación en la meta. Cero en Y = sin cambio frente a diciembre anterior.':'Cero en X = desocupación en la mediana 2012–2019. Cero en Y = sin cambio del crecimiento salarial frente a seis meses antes.';
 inspect(points.length-1);
}
function phaseOf(p){return p.y>=0?(p.x>=0?1:0):(p.x>=0?2:3)}
function renderStateSequence(){
 const c=cfg(),points=visible(),shortLeft=dataset==='ipca'?'Bajo la meta':'Holgura',shortRight=dataset==='ipca'?'Sobre la meta':'Apretado';
 const rows=[
  {title:shortLeft,sub:'Acelera',color:'var(--phase-one)'},
  {title:shortRight,sub:'Acelera',color:'var(--phase-two)'},
  {title:shortRight,sub:'Desacelera',color:'var(--phase-three)'},
  {title:shortLeft,sub:'Desacelera',color:'var(--phase-four)'}
 ];
 const dateCell=p=>{
  if(dataset==='laboral'){const parts=p.label.split(' ');return '<span>'+esc(parts[0])+'</span><span>'+esc(parts[1])+'</span>'}
  return '<span>'+esc(p.date.slice(0,4))+'</span><span>'+(p.label.includes('sep')?'sep':'dic')+'</span>';
 };
 let markup='<table class="phase-matrix"><caption class="sr-only">Secuencia de estados del ciclo. Cada columna representa una observación; su punto indica el cuadrante.</caption><thead><tr><th class="phase-sticky" scope="col">Estado del ciclo</th>'+
 points.map((p,i)=>'<th scope="col" class="'+(i===points.length-1?'phase-selected':'')+'"><div class="phase-date">'+dateCell(p)+'</div></th>').join('')+'</tr></thead><tbody>';
 rows.forEach((row,r)=>{
  markup+='<tr><th class="phase-sticky" scope="row"><div class="phase-label"><span>'+row.title+'</span><small>'+row.sub+'</small></div></th>';
  points.forEach((p,i)=>{
   markup+='<td>';
   if(phaseOf(p)===r)markup+='<button class="phase-point" type="button" data-phase-index="'+i+'" tabindex="'+(i===points.length-1?'0':'-1')+'" aria-pressed="'+String(i===points.length-1)+'" aria-label="'+esc(p.label+': '+quadrant(p))+'" style="--phase-color:'+row.color+'"><span class="phase-mark"></span></button>';
   else markup+='<span class="phase-empty" aria-hidden="true"></span>';
   markup+='</td>';
  });
  markup+='</tr>';
 });
 markup+='</tbody></table>';
 const host=$('phase-scroll');host.innerHTML=markup;
 const buttons=[...host.querySelectorAll('[data-phase-index]')].sort((a,b)=>Number(a.dataset.phaseIndex)-Number(b.dataset.phaseIndex));
 const inspect=i=>{
  const p=points[i];
  buttons.forEach(button=>{const active=Number(button.dataset.phaseIndex)===i;button.setAttribute('aria-pressed',String(active));button.tabIndex=active?0:-1});
  $('phase-summary').textContent=p.label+' · '+quadrant(p);
  readout('readout-g',p);
 };
 buttons.forEach(button=>{
  const index=Number(button.dataset.phaseIndex);
  button.addEventListener('click',()=>inspect(index));
  button.addEventListener('focus',()=>inspect(index));
  button.addEventListener('pointerenter',ev=>{if(ev.pointerType!=='touch')showTooltip(points[index],ev.clientX,ev.clientY)});
  button.addEventListener('pointerleave',hideTooltip);
  button.addEventListener('blur',hideTooltip);
  button.addEventListener('keydown',ev=>{
   let i;
   if(ev.key==='ArrowLeft')i=Math.max(0,index-1);
   if(ev.key==='ArrowRight')i=Math.min(points.length-1,index+1);
   if(ev.key==='Home')i=0;
   if(ev.key==='End')i=points.length-1;
   if(i!==undefined){ev.preventDefault();buttons[i].focus();inspect(i)}
  });
 });
 inspect(points.length-1);
 host.scrollLeft=host.scrollWidth;
 $('phase-note').textContent=points.length+' observaciones · '+(dataset==='ipca'?'una por año; 2026 hasta septiembre':'una por trimestre')+'. Desplázate horizontalmente para recorrer las fechas.';
}
function renderAdditional(){
 if(!additionalReady){
  additionalReady=true;
  $('zoom-window').addEventListener('change',renderFocus);
  $('trail-play').addEventListener('click',toggleClockPlayback);
  $('trail-previous').addEventListener('click',()=>{stopClockPlayback();trailIndex=Math.max(0,trailIndex-1);renderTrail()});
  $('trail-next').addEventListener('click',()=>{stopClockPlayback();trailIndex=Math.min(end,trailIndex+1);renderTrail()});
  $('trail-range').addEventListener('input',ev=>{stopClockPlayback();trailIndex=Number(ev.target.value);renderTrail()});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopClockPlayback()});
  clockMotionPreference.addEventListener('change',()=>{stopClockPlayback();renderTrail()});
 }
 const signature=dataset+':'+end;
 if(signature!==trailSignature){stopClockPlayback();trailIndex=end;trailSignature=signature}
 renderFocus();renderTrail();renderTemporalSeries();renderStateSequence();
}

