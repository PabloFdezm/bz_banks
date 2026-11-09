/* Monitor Brasil · contrato compartido de lectura 1.1.
   Presentación y consulta: no modifica entradas, escalas ni fórmulas económicas.
   Las tablas consumen la misma extracción que Descargar Excel. */
import { datosDeTarjeta } from './excel.js';
const selections=new Map();
const labels=new WeakMap();
const css=name=>getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const nf=new Intl.NumberFormat('es-CL',{maximumFractionDigits:4});
const day=v=>typeof v==='number'&&Math.abs(v)>1e11?new Date(v).toISOString().slice(0,10):String(v??'');
const element=(tag,text,cls)=>{const n=document.createElement(tag);if(text!=null)n.textContent=String(text);if(cls)n.className=cls;return n;};
function safeHTML(value){const t=document.createElement('template');t.innerHTML=String(value??'');t.content.querySelectorAll('script,style,iframe,object,embed').forEach(n=>n.remove());for(const n of t.content.querySelectorAll('*'))for(const a of [...n.attributes])if(a.name.startsWith('on')||/^(javascript:)/i.test(a.value))n.removeAttribute(a.name);return t.content;}
function cellText(cell,column={}){
 const fmt=cell&&typeof cell==='object'&&!(cell instanceof Date)?cell.fmt||column.fmt:column.fmt;
 const value=cell&&typeof cell==='object'&&!(cell instanceof Date)?cell.v:cell;
 if(value==null||value==='')return 'Sin dato';
 if(value instanceof Date)return new Intl.DateTimeFormat('es-CL',{day:'2-digit',month:'short',year:'numeric',timeZone:'UTC'}).format(value);
 if(typeof value!=='number')return String(value);
 if(fmt==='pct')return nf.format(value*100)+' %';
 if(fmt==='pctn')return nf.format(value)+' %';
 if(fmt==='pp')return nf.format(value)+' pp';
 return nf.format(value);
}
function chartsIn(zona){return [zona,...zona.querySelectorAll('[_echarts_instance_]')].map(n=>window.echarts?.getInstanceByDom(n)).filter((ch,i,a)=>ch&&!ch.isDisposed()&&a.indexOf(ch)===i);}
function titleOf(html){const t=element('div');t.append(safeHTML(html));return t.firstElementChild?.textContent?.trim()||t.textContent.trim();}
function visibleSeries(opt){return (opt.series||[]).map((s,i)=>({s,i})).filter(({s})=>!String(s.name||'').startsWith('_')&&!s.silent&&s.tooltip?.show!==false&&s.data?.length);}
function param(opt,i,j){
 const s=opt.series[i],raw=s.data[j],value=raw?.value??raw;
 const x=opt.xAxis?.[s.xAxisIndex||0],y=opt.yAxis?.[s.yAxisIndex||0];
 const cat=(x?.type==='category'?x.data:y?.type==='category'?y.data:null)?.[j];
 const axis=cat?.value??cat??(Array.isArray(value)?value[0]:raw?.name??j);
 return {componentType:'series',seriesType:s.type,seriesIndex:i,dataIndex:j,seriesName:s.name||'Serie',data:raw,value,name:raw?.name??String(cat??''),axisValue:axis,axisValueLabel:String(axis),color:typeof raw?.itemStyle?.color==='string'?raw.itemStyle.color:s.itemStyle?.color||s.lineStyle?.color||css('--navy')};
}
function htmlFor(chart,p,opt=chart.getOption()){
 const tt=Array.isArray(opt.tooltip)?opt.tooltip[0]:opt.tooltip;
 if(typeof tt?.formatter==='function'){
  try{
   const anchor=day(p.axisValue??(Array.isArray(p.value)?p.value[0]:p.name));
   const related=visibleSeries(opt).map(({s,i})=>{const j=s.data.findIndex((_,j)=>day(param(opt,i,j).axisValue)===anchor);return j<0?null:param(opt,i,j);}).filter(Boolean);
   const result=tt.formatter(tt.trigger==='axis'?(related.length?related:[p]):p);if(result)return result;
  }catch{/* el formateador de un nodo puede requerir parámetros internos adicionales */}
 }
 const result=element('div');result.append(element('strong',p.name||p.seriesName));
 result.append(element('p',`${p.seriesName}: ${Array.isArray(p.value)?p.value.map(v=>v==null?'Sin dato':typeof v==='number'?nf.format(v):v).join(' · '):p.value==null?'Sin dato':p.value}`));return result.innerHTML;
}
/* Ejes legibles: se conserva el formateador y se reduce la densidad según el ancho real. */
export function ajustarLectura(chart,{componente}={}){
 if(chart.isDisposed())return;
 const opt=chart.getOption(),width=chart.getWidth();
 const patch={textStyle:{fontSize:12,fontFamily:css('--fuente')},tooltip:{confine:true,textStyle:{fontSize:14}}};
 for(const name of ['xAxis','yAxis'])if(opt[name])patch[name]=opt[name].map(axis=>({
  axisLabel:{fontSize:12,hideOverlap:true,color:css('--texto-2'),...(name==='xAxis'?{showMinLabel:false,showMaxLabel:false}:{}),...(axis.type==='category'&&name==='xAxis'?{interval:'auto'}:{})},
  nameTextStyle:{fontSize:12},...(axis.type==='time'?{splitNumber:Math.max(3,Math.min(6,Math.floor(width/105)))}:{})
 }));
 if(['dispersion','dispersionL','burbujas','clu_sectores'].includes(componente)){
  if(!labels.has(chart))labels.set(chart,(opt.series||[]).map(s=>s.label?.show??false));
  patch.series=(opt.series||[]).map((s,i)=>s.type==='scatter'?{label:{show:width<520?false:labels.get(chart)[i]},itemStyle:{borderWidth:1,borderColor:css('--texto-2')}}:{});
 }
 chart.setOption(patch);
}
export function conectarGrafico({figura,zona,entrada,componente,clave,grande=false,html=false}){
 zona._uxCleanup?.();figura.querySelectorAll(':scope > .ux-tools').forEach(n=>n.remove());
 figura.dataset.uxChart='1';figura.dataset.componente=componente;zona.dataset.uxRender=html?'html':'chart';zona._entrada=entrada;
 const render=zona.firstElementChild;if(render)render.classList.add('ux-render');
 const controller=new AbortController(),signal=controller.signal;
 const listen=(n,type,fn,opts={})=>n.addEventListener(type,fn,{...opts,signal});
 const tools=element('div',null,'ux-tools'),reader=element('section',null,'ux-reader');
 reader.hidden=true;reader.setAttribute('aria-label','Consulta del gráfico');
 const head=element('div',null,'ux-reader-head'),heading=element('strong','Consulta'),clear=element('button','Limpiar consulta','ux-button');clear.type='button';head.append(heading,clear);
 const output=element('div',null,'ux-reading');output.setAttribute('aria-live','polite');output.setAttribute('aria-atomic','true');reader.append(head,output);
 const help=element('p','Toca o pulsa un dato para fijar su lectura. Flechas para recorrer; Enter para fijar; Escape para limpiar.','ux-help');
 const details=element('details',null,'ux-data'),summary=element('summary','Consultar datos');details.append(summary);
 const body=element('div',null,'ux-data-body');details.append(body);tools.append(help,reader,details);
 zona.after(tools);
 let saved=selections.get(clave),tableBuilt=false;
 function update(fragment,selection){if(selection){if(selection.html&&!selection.name)selection.name=titleOf(fragment);selections.set(clave,selection);}reader.hidden=false;reader.dataset.fixed=selection?'true':'false';heading.textContent=selection?'Dato fijado':'Consulta';output.replaceChildren(safeHTML(fragment));figura.dispatchEvent(new CustomEvent('mb:consulta',{detail:{clave,selection},bubbles:true}));}
 function clearSelection(){for(const button of zona.querySelectorAll('.fijo-soltar'))button.click();selections.delete(clave);saved=null;reader.hidden=true;output.replaceChildren();for(const ch of chartsIn(zona))ch.dispatchAction({type:'hideTip'});}
 listen(clear,'click',()=>{clearSelection();zona.focus({preventScroll:true});});
 const escape=()=>{if(reader.hidden)return false;clearSelection();return true;};zona._escapar=escape;tools._escapar=escape;
 // Una sola leyenda cuando el renderizador ya la incluye.
 const ownLegend=render?.querySelector('.leyenda');if(ownLegend?.textContent.trim())for(const leg of figura.querySelectorAll(':scope > .leyenda,:scope > .leyenda-desplazable'))leg.hidden=true;
 // En composición, la leyenda exterior conserva también las partes que no caben dentro.
 for(const [index,row]of [...zona.querySelectorAll('.apilada100-fila')].entries()){
  const parts=entrada.barras?.[index]?.partes?.filter(p=>p.valor!=null)||[];if(!parts.length)continue;
  const list=element('ul',null,'ux-composition-legend');list.setAttribute('aria-label','Categorías y valores');
  for(const p of parts){const li=element('li'),mark=element('i',null,'ux-composition-mark');mark.style.background=p.color||css('--navy');mark.setAttribute('aria-hidden','true');li.append(mark,element('span',p.nombre),element('strong',p.rotulo||nf.format(p.valor)));list.append(li);}row.append(list);
 }
 const chartEvents=[];
 for(const chart of chartsIn(zona)){
  ajustarLectura(chart,{componente});const dom=chart.getDom();let i=visibleSeries(chart.getOption())[0]?.i??0,j=0;
  const select=(p)=>{if(!p||p.componentType!=='series'||String(p.seriesName).startsWith('_'))return;const opt=chart.getOption();i=p.seriesIndex;j=p.dataIndex;const selection={series:p.seriesName,anchor:day(p.axisValue??(Array.isArray(p.value)?p.value[0]:p.name)),index:j};saved=selection;update(htmlFor(chart,p,opt),selection);};
  chart.on('click',select);chartEvents.push([chart,select]);
  // Captura por coordenadas también sobre el espacio entre las marcas y en dispositivos táctiles.
  let start=null;
  listen(dom,'pointerdown',e=>{start=e.target.closest('button,input,select,a')?null:{x:e.screenX,y:e.screenY};},{capture:true,passive:true});
  listen(dom,'pointercancel',()=>{start=null;},{capture:true,passive:true});
  const pickAt=(clientX,clientY)=>{
   const rect=dom.getBoundingClientRect(),x=clientX-rect.left,y=clientY-rect.top,opt=chart.getOption();
   const ss=visibleSeries(opt);let best=null,distance=Infinity;
   for(const {s,i:si}of ss){
    if(!['line','bar','scatter','effectScatter'].includes(s.type))continue;
    const ax=opt.xAxis?.[s.xAxisIndex||0],ay=opt.yAxis?.[s.yAxisIndex||0];
    for(let k=0;k<s.data.length;k++){
     const p=param(opt,si,k);if(p.value==null)continue;
     const v=Array.isArray(p.value)?p.value:ay?.type==='category'?[p.value,k]:[k,p.value];if(v.some(n=>n==null||n==='-'))continue;
     let px;try{px=chart.convertToPixel({seriesIndex:si},v);}catch{continue;}if(!Array.isArray(px)||px.some(n=>!Number.isFinite(n)))continue;
     const d=ax?.type==='time'||ax?.type==='category'?Math.abs(px[0]-x):ay?.type==='category'?Math.abs(px[1]-y):Math.hypot(px[0]-x,px[1]-y);
     if(d<distance){distance=d;best=p;}
    }
   }
   if(best){select(best);chart.dispatchAction({type:'showTip',seriesIndex:best.seriesIndex,dataIndex:best.dataIndex});dom.focus({preventScroll:true});}
  };
  listen(dom,'pointerup',e=>{if(!start||Math.hypot(e.screenX-start.x,e.screenY-start.y)>10){start=null;return;}start=null;pickAt(e.clientX,e.clientY);},{capture:true,passive:true});
  let touchStart=null;
  const finishTouch=e=>{const t=e.changedTouches[0],initial=touchStart;touchStart=null;if(t&&initial&&Math.hypot(t.screenX-initial.x,t.screenY-initial.y)<=10)pickAt(t.clientX,t.clientY);zona.dispatchEvent(new CustomEvent('mb:gesture-end',{bubbles:true}));};
  const cancelTouch=()=>{touchStart=null;zona.dispatchEvent(new CustomEvent('mb:gesture-end',{bubbles:true}));};
  listen(dom,'touchstart',e=>{const t=e.touches[0];touchStart=t?{x:t.screenX,y:t.screenY}:null;
   // ECharts puede reemplazar el path SVG durante el gesto. El destino original
   // recibe touchend aunque ya no pertenezca al documento.
   listen(e.target,'touchend',finishTouch,{once:true,passive:true});listen(e.target,'touchcancel',cancelTouch,{once:true,passive:true});
  },{capture:true,passive:true});
  listen(dom,'touchcancel',cancelTouch,{capture:true,passive:true});
  listen(dom,'touchend',finishTouch,{capture:true,passive:true});
  if(!dom.hasAttribute('tabindex'))dom.tabIndex=0;dom.setAttribute('aria-label',`${figura.querySelector('.tarjeta-titulo')?.textContent||'Gráfico'}. Usa las flechas para recorrer los datos.`);
  listen(dom,'keydown',ev=>{
   if(ev.target!==dom)return;if(ev.key==='Escape'){if(escape()){ev.preventDefault();ev.stopPropagation();}return;}
   if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End','Enter'].includes(ev.key))return;
   // El dibujante temporal ya implementa sus flechas; el panel común escucha su consulta.
   if(dom.classList.contains('grafico-fijable')||dom.classList.contains('reloj-graf')){
    queueMicrotask(()=>{const text=dom.getAttribute('aria-valuetext')||zona.querySelector('.reloj-consulta')?.textContent;if(text&&!text.startsWith('Sin mes fijado')){const n=element('p',text);update(n.outerHTML,{html:n.outerHTML});}});return;
   }
   const opt=chart.getOption(),ss=visibleSeries(opt);if(!ss.length)return;const at=Math.max(0,ss.findIndex(s=>s.i===i));
   if(ev.key==='ArrowDown')i=ss[Math.min(ss.length-1,at+1)].i;else if(ev.key==='ArrowUp')i=ss[Math.max(0,at-1)].i;else if(!ss.some(s=>s.i===i))i=ss[0].i;
   const max=opt.series[i].data.length-1;j=Math.min(j,max);
   if(ev.key==='ArrowRight')j=Math.min(max,j+1);if(ev.key==='ArrowLeft')j=Math.max(0,j-1);if(ev.key==='Home')j=0;if(ev.key==='End')j=max;
   ev.preventDefault();select(param(opt,i,j));chart.dispatchAction({type:'showTip',seriesIndex:i,dataIndex:j});
  });
  const onAxis=ev=>{if(!ev.axesInfo?.length)return;const opt=chart.getOption(),anchor=day(ev.axesInfo[0].value),ss=visibleSeries(opt);for(const {s,i:si}of ss){const at=s.data.findIndex((_,k)=>day(param(opt,si,k).axisValue)===anchor);if(at>=0){if(!reader.hidden&&selections.has(clave))return;update(htmlFor(chart,param(opt,si,at),opt));break;}}};
  chart.on('updateAxisPointer',onAxis);chartEvents.push([chart,onAxis,'updateAxisPointer']);
  if(saved?.series){const opt=chart.getOption(),si=opt.series.findIndex(s=>s.name===saved.series);if(si>=0){const at=opt.series[si].data.findIndex((_,k)=>day(param(opt,si,k).axisValue)===saved.anchor);if(at>=0)select(param(opt,si,at));}}
 }
 // Consultas nativas de líneas (flechas) y relojes.
 listen(document,'mes-fijado',event=>{if(event.detail?.clave!==clave)return;const n=zona.querySelector('.grafico-fijable'),text=n?.getAttribute('aria-valuetext');if(text&&!text.startsWith('Sin mes fijado')){const p=element('p',text);update(p.outerHTML,{html:p.outerHTML});}});
 function enhance(){for(const n of zona.querySelectorAll('[data-tt]')){if(!n.matches('button,a,input,select,textarea'))n.tabIndex=0;if(!n.getAttribute('aria-label')){const t=element('div');t.append(safeHTML(n.dataset.tt));n.setAttribute('aria-label',t.textContent.replace(/\s+/g,' ').trim());}}}
 enhance();
 listen(zona,'click',e=>{const n=e.target.closest('[data-tt]');if(n)update(n.dataset.tt,{html:n.dataset.tt});});
 listen(zona,'keydown',e=>{if(e.key==='Escape'){if(escape()){e.preventDefault();e.stopPropagation();}return;}const n=e.target.closest('[data-tt]');if(n&&['Enter',' '].includes(e.key)){if(!e.target.matches('button,summary,input,select'))e.preventDefault();update(n.dataset.tt,{html:n.dataset.tt});}});
 if(saved?.html)queueMicrotask(()=>{if(signal.aborted)return;const native=zona.querySelector('.grafico-fijable')?.getAttribute('aria-valuetext');if(native&&!native.startsWith('Sin mes fijado'))update(element('p',native).outerHTML,{html:element('p',native).outerHTML});else{const current=[...zona.querySelectorAll('[data-tt]')].find(n=>titleOf(n.dataset.tt)===saved.name);if(current)update(current.dataset.tt,{html:current.dataset.tt,name:saved.name});}});
 function buildTable(){
  body.replaceChildren();const blocks=datosDeTarjeta(figura);
  body.append(element('p',`Datos de la vista actual. ${figura.querySelector('.tarjeta-sub')?.textContent||''} Los valores ausentes se conservan como «Sin dato».`,'ux-help'));
  if(!blocks.length){body.append(element('p','Esta vista no contiene observaciones tabulables. Consulta la nota y la fuente del gráfico.'));return;}
  for(const [index,block]of blocks.entries()){
   let page=0;const section=element('section',null,'ux-data-block'),region=element('div',null,'ux-table-region'),table=element('table');
   region.tabIndex=0;region.setAttribute('role','region');region.setAttribute('aria-label',block.titulo||`Datos del gráfico, bloque ${index+1}`);
   const caption=element('caption',block.titulo||figura.querySelector('.tarjeta-titulo')?.textContent||'Datos del gráfico');table.append(caption);
   const thead=element('thead'),tr=element('tr');block.columnas.forEach((c,i)=>{const th=element('th',c.titulo||(i===0?'Período o categoría':`Valor ${i}`));th.scope='col';tr.append(th);});thead.append(tr);table.append(thead);const tbody=element('tbody');table.append(tbody);region.append(table);
   const nav=element('div',null,'ux-pagination'),prev=element('button','Anterior','ux-button'),next=element('button','Siguiente','ux-button'),status=element('span');prev.type=next.type='button';status.setAttribute('role','status');nav.append(prev,status,next);
   const paint=()=>{tbody.replaceChildren();for(const row of block.filas.slice(page*50,page*50+50)){const tr=element('tr');block.columnas.forEach((c,i)=>{const td=element(i===0?'th':'td',cellText(row[i],c));if(i===0)td.scope='row';tr.append(td);});tbody.append(tr);}const total=Math.max(1,Math.ceil(block.filas.length/50));prev.disabled=page===0;next.disabled=page>=total-1;status.textContent=`${page+1} / ${total} · ${block.filas.length} filas`;};
   listen(prev,'click',()=>{page--;paint();});listen(next,'click',()=>{page++;paint();});section.append(region,nav);body.append(section);paint();
  }
 }
 listen(details,'toggle',()=>{if(details.open&&!tableBuilt){tableBuilt=true;buildTable();}});
 let lastWidth=-1,frame=0;
 const resize=new ResizeObserver(()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(!zona.isConnected){resize.disconnect();return;}const width=Math.round(zona.clientWidth);if(width!==lastWidth){lastWidth=width;for(const ch of chartsIn(zona)){ch.resize();ajustarLectura(ch,{componente});}}});});resize.observe(zona);
 const mutation=new MutationObserver(enhance);mutation.observe(zona,{childList:true,subtree:true});
 const cleanup=()=>{controller.abort();resize.disconnect();mutation.disconnect();cancelAnimationFrame(frame);for(const [ch,fn,type]of chartEvents)if(!ch.isDisposed())ch.off(type||'click',fn);tools.remove();};
 zona._uxCleanup=cleanup;return {cleanup,clear:clearSelection,reader,details};
}
