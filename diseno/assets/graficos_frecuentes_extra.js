// Variantes añadidas: usan el mismo estado, diálogo, tipografía y gestor de tooltips.
const EXTRA_CASES=new Set(['activity','unemployment','spending','waterfall']);
DATA.activity=DATA.activityBaskets.indices.rows;
Object.assign(CASES,{
 activity:{title:'Índices de actividad, a/a',sub:'% a/a · sin desestacionalizar · hasta 48 meses',unit:'% a/a',source:'IBGE y BCB · actv_serie · columna a12',names:DATA.activityBaskets.indices.names,colors:['navy','plum','teal','steel'],dashed:[],design:'Compara cuatro series sobre el mismo calendario y conserva las dos selecciones del monitor.',note:'La variación interanual usa a12, no m12 ni m3a. Un mes ausente no se arrastra ni se une por posición.'},
 unemployment:{title:'Brecha de desocupación',sub:'Desocupación desestacionalizada menos su mediana de 2012–2019',unit:'Brecha en pp · cero = mediana histórica',source:'IBGE / PNAD · empleo_pagina · cálculo del monitor',names:['Brecha frente a la mediana'],colors:['steel'],design:'Conserva el cero y distingue el signo con texto y valores, sin confundir la brecha con la tasa.',note:'La mediana se calcula una vez con los datos válidos de 2012–2019. Cambiar la ventana visible no cambia la referencia.'},
 spending:{title:'Gasto, partida por partida',sub:'Gobierno central · % del PIB, cambios en pp y crecimiento real en %',source:'Tesoro / RTN · fis_gasto · tabla local del monitor',design:'Separa peso, cambio y crecimiento real. La jerarquía evita sumar padres e hijos.',note:'El ancho de barra compara cada partida con el gasto total; el número expresa su peso en el PIB. No se suman las filas de padres y subpartidas.'},
 waterfall:{title:'De la deuda inicial a la de hoy',sub:'Deuda bruta · niveles en % del PIB y contribuciones en pp',unit:'Posición acumulada: % del PIB',source:'BCB · fiscal_cascada · descomposición del monitor',design:'Cada paso conserva su signo, su posición acumulada y el residuo original.',note:'El nivel final observado se conserva separado del cierre calculado. La diferencia de conciliación se muestra sin repartirla entre componentes.'}
});
Object.assign(STATES,{
 activity:{window:'48',basket:'indices',at:DATA.activity.length-1,pinned:false},
 unemployment:{window:'all',at:DATA.unemployment.length-1,pinned:false},
 spending:{item:DATA.spending.rows.findIndex(r=>r.total),metric:'d1',open:new Set(),pinned:false},
 waterfall:{bridge:DATA.waterfall.find(b=>b.label.startsWith('3 '))?.id||DATA.waterfall[0]?.id,step:5,pinned:false}
});
const METRICS={d1:['Cambio 1 año','pp'],d3:['Cambio 3 años','pp'],r1:['Real 1 año','%'],r2:['Real 2 años','%'],r5:['Real 5 años','%']};
const originalRows=currentRows,originalSelected=selected,originalView=caseView,originalRender=renderChart,originalTooltip=tooltipContent;
const bridge=()=>DATA.waterfall.find(b=>b.id===STATES.waterfall.bridge)||DATA.waterfall[0];
currentRows=function(key){
 if(key==='spending')return DATA.spending.rows;
 if(key==='waterfall')return bridge()?.steps||[];
 return originalRows(key);
};
selected=function(key,rr=currentRows(key)){
 if(key==='spending')return rr[STATES[key].item]||rr.at(-1);
 if(key==='waterfall')return rr[Math.min(STATES[key].step,rr.length-1)]||rr.at(-1);
 return originalSelected(key,rr);
};
function extraTip(key,r,persistent=false){
 if(!r)return '<p>Sin datos para esta selección.</p>';
 let head='',body='';
 if(key==='activity'){
  head='<div class="tip-heading"><strong>'+E(dateLabel(r.date))+'</strong><span>Actividad · variación interanual</span></div>';
  body=r.values.map((v,i)=>tipRow(CASES.activity.names[i],v,'% a/a',CASES.activity.colors[i],i===0)).join('');
 }else if(key==='unemployment'){
  head='<div class="tip-heading"><strong>'+E(dateLabel(r.date))+'</strong><span>Desocupación · referencia fija 2012–2019</span></div>';
  body=tipRow('Brecha frente a la mediana',r.values[0],'pp','',true,true)+tipRow('Desocupación desestacionalizada',r.rate,'%')+tipRow('Mediana histórica',r.reference,'%');
  body+='<p class="tip-caption">'+E(r.values[0]==null?'Sin tasa del mes: no se calcula brecha.':r.values[0]<0?'Por debajo de la mediana histórica.':r.values[0]>0?'Por encima de la mediana histórica.':'Coincide con la mediana histórica.')+'</p>';
 }else if(key==='spending'){
  head='<div class="tip-heading"><strong>'+E(r.name)+'</strong><span>'+E(dateLabel(DATA.spending.date))+' · '+(r.total?'Gasto total':r.level?'Subpartida':'Partida principal')+'</span></div>';
  body=tipRow('Peso en el PIB',r.weight,'% PIB','navy',true)+Object.entries(METRICS).map(([k,[label,unit]])=>tipRow(label,r[k],unit,'',false,true)).join('');
  body+='<p class="tip-caption">Los cambios de peso están en pp. Los crecimientos reales están en %. Los hijos ya están incluidos en su partida principal.</p>';
 }else{
  const b=bridge(),isLevel=r.kind==='level';
  head='<div class="tip-heading"><strong>'+E(r.name)+'</strong><span>'+E(b.base)+' → '+E(b.end)+' · '+E(b.label)+'</span></div>';
  body=tipRow(isLevel?'Nivel de deuda':'Contribución',r.value,isLevel?'% PIB':'pp','',true,!isLevel);
  if(!isLevel)body+=tipRow('Acumulado anterior',r.start,'% PIB')+tipRow('Acumulado tras el paso',r.end,'% PIB');
  body+='<p class="tip-caption">'+E(isLevel?'El total se mide desde cero.':r.value==null?'Sin valor para este componente.':r.value>0?'Este componente eleva la deuda.':r.value<0?'Este componente reduce la deuda.':'Este componente no cambia el nivel.')+'</p>';
 }
 return head+body+(persistent?'':'<p class="tip-footer">Vista previa · clic, toque o Enter conserva la consulta. Escape cierra esta ayuda.</p>');
}
tooltipContent=function(key,r,kind=null,id=null,groupId=null,persistent=false){
 return EXTRA_CASES.has(key)?extraTip(key,r,persistent):originalTooltip(key,r,kind,id,groupId,persistent);
};
function extraControls(key,view){
 const st=STATES[key],rr=currentRows(key),r=selected(key,rr);
 let fields='';
 if(key==='activity'){
  fields+=field('basket','Series',st.basket,[['indices','PIM, PMC y PMS'],['ibc','IBC-Br y sectores']],view);
  fields+=field('window','Ventana',st.window,[['48','48 meses'],['24','24 meses']],view);
 }else if(key==='unemployment')fields+=field('window','Ventana',st.window,[['all','Desde 2016'],['60','Últimos 5 años'],['36','Últimos 3 años']],view);
 if(key==='activity'||key==='unemployment')fields+=field('date','Consultar mes',r?.date||'',rr.map(d=>[d.date,dateLabel(d.date)]),view);
 if(key==='spending'){
  fields+=field('metric','Comparar en tarjeta',st.metric,Object.entries(METRICS).map(([k,[n,u]])=>[k,n+' ('+u+')']),view);
  fields+=field('item','Consultar partida',st.item,rr.map((d,i)=>[String(i),d.name]),view);
 }
 if(key==='waterfall'){
  fields+=field('bridge','Ventana',st.bridge,DATA.waterfall.map(b=>[b.id,b.label]),view);
  fields+=field('step','Consultar paso',Math.min(st.step,rr.length-1),rr.map((d,i)=>[String(i),d.name]),view);
 }
 return '<div class="controls">'+fields+'</div>';
}
function extraReading(key,r){
 if(!r)return '<div class="empty">No hay datos para esta selección.</div>';
 const st=STATES[key];
 if(key==='activity')return reading(key,r);
 const heading=key==='unemployment'?dateLabel(r.date):r.name;
 let values='';
 if(key==='unemployment')values=valueBlock('Brecha',valueWithUnit(r.values[0],'pp',2,true))+valueBlock('Tasa desestacionalizada',valueWithUnit(r.rate,'%'))+valueBlock('Mediana 2012–2019',valueWithUnit(r.reference,'%'));
 if(key==='spending')values=valueBlock('Peso en el PIB',valueWithUnit(r.weight,'% PIB'))+valueBlock('Cambio 1 año',valueWithUnit(r.d1,'pp',2,true))+valueBlock('Real 1 año',valueWithUnit(r.r1,'%',2,true));
 if(key==='waterfall')values=valueBlock(r.kind==='level'?'Nivel de deuda':'Contribución',valueWithUnit(r.value,r.kind==='level'?'% PIB':'pp',2,r.kind!=='level'))+(r.kind!=='level'?valueBlock('Acumulado tras el paso',valueWithUnit(r.end,'% PIB')):'');
 const reset=st.pinned?'<button type="button" data-extra-reset="'+key+'">'+(key==='spending'?'Ver gasto total':key==='waterfall'?'Ver nivel final':'Ver último mes')+'</button>':'<span>Consulta actual</span>';
 return '<div class="reading extra-reading"><div class="reading-head"><strong>'+E(heading)+'</strong>'+reset+'</div><div class="values">'+values+'</div>'+(st.pinned?'<p class="query-hint">Consulta fijada · la vista previa no modifica estos valores.</p>':'')+'</div>';
}
function extraDataTable(names,rows,caption){
 return '<table class="data-table details-table"><caption>'+E(caption)+'</caption><thead><tr>'+names.map((n,i)=>'<th scope="col"'+(i?' class="num"':'')+'>'+E(n)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map((v,i)=>'<td'+(i?' class="num" data-label="'+E(names[i])+'"':'')+'>'+E(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
}
function bridgeReconciliation(){
 const b=bridge();if(!b)return '';
 const valid=b.difference!=null&&Math.abs(b.difference)<=.0001;
 return '<div class="reading"><div class="reading-head"><strong>Conciliación de la ventana</strong><span>'+E(b.base)+' → '+E(b.end)+'</span></div><div class="values">'+valueBlock('Nivel inicial',valueWithUnit(b.initial,'% PIB'))+valueBlock('Cierre calculado',valueWithUnit(b.computed,'% PIB'))+valueBlock('Nivel final informado',valueWithUnit(b.final,'% PIB'))+valueBlock('Final − calculado',valueWithUnit(b.difference,'pp',4,true))+'</div><p class="bridge-status">'+(b.difference==null?'No puede conciliarse: faltan contribuciones.':valid?'Cierra dentro de la tolerancia de 0,0001 pp.':'Existe una diferencia de cierre. Se muestra sin modificar los componentes.')+' El residuo es un componente original de la fuente.</p></div>';
}
function extraDetails(key,rr,r,view){
 let html='';
 if(key==='activity'||key==='unemployment'){
  const at=Math.max(0,rr.findIndex(x=>x.date===r?.date));
  html+='<section class="details-block"><h3>Por periodos</h3><p>La consulta mensual conserva el mismo calendario, las series elegidas y la ventana de la tarjeta.</p><div class="period-query"><label for="'+view+'-period">Mes consultado</label><input id="'+view+'-period" type="range" data-control="period" min="0" max="'+(rr.length-1)+'" value="'+at+'"><output for="'+view+'-period">'+E(dateLabel(rr[at].date))+'</output></div>';
  const slice=rr.slice(Math.max(0,at-5),Math.min(rr.length,at+7));
  const names=key==='activity'?['Mes',...CASES.activity.names.map(n=>n+' (% a/a)')]:['Mes','Brecha (pp)','Desocupación SA (%)','Mediana 2012–2019 (%)'];
  const records=slice.map(d=>[dateLabel(d.date)+(d.date===r.date?' · consultado':''),...(key==='activity'?d.values:[d.values[0],d.rate,d.reference]).map(v=>fmt(v,2))]);
  html+=extraDataTable(names,records,'Hasta doce observaciones cercanas al mes consultado.')+'</section>';
 }
 if(key==='waterfall'){
  html+='<section class="details-block"><h3>Conciliación paso a paso</h3>'+extraDataTable(['Paso','Tipo','Antes (% PIB)','Aporte (pp)','Después (% PIB)'],rr.map(s=>[s.name,s.kind==='level'?'Nivel':'Contribución',s.kind==='level'?'No aplica':fmt(s.start,4),s.kind==='level'?'No aplica':valueWithUnit(s.value,'',4,true),fmt(s.end,4)]),'Los niveles inicial y final se miden desde cero; las contribuciones parten del acumulado anterior.')+'</section>';
 }
 html+='<section class="details-block"><h3>Cómo se lee y de dónde sale</h3><p>'+E(CASES[key].note)+'</p>';
 if(key==='activity')html+='<p>Las cestas son PIM, PMC y PMS junto al IBC-Br, o el IBC-Br con sus sectores agropecuario, industria y servicios. Las cuatro líneas son observadas; ninguna es una meta. Se usa a12 × 100, con hasta 48 meses del corte global de actividad.</p>';
 if(key==='unemployment')html+='<p class="formula">Brecha (pp) = (desocupación SA − mediana de desocupación SA de 2012–2019) × 100</p><p>La serie comienza en 2016. La referencia utiliza todos los meses válidos del periodo histórico, no sólo los que se ven en pantalla. La columna brecha_pp del archivo corresponde a otra comparación y no se utiliza aquí.</p>';
 if(key==='spending')html+='<p>Todos los campos de esta tabla entran como fracciones. El peso se expresa en % del PIB; d_pct_1a y d_pct_3a se presentan en pp; real_1a, real_2a y real_5a, en %. La barra es peso de la partida / peso del gasto total. Los horizontes reales son acumulados, no tasas anuales compuestas.</p><p>La vista ampliada muestra las 19 filas y todos los horizontes. La tarjeta conserva el árbol y permite elegir una métrica de comparación. Los grupos ya contienen a sus subpartidas: no se suman las 19 filas.</p>';
 if(key==='waterfall')html+='<p class="formula">Cierre calculado = deuda inicial + suma de las contribuciones originales</p><p>Los valores de fiscal_cascada ya están escalados. Los niveles están en % del PIB y los cambios en pp; no se multiplican por 100. La orientación horizontal permite leer los nombres en móvil. Cada barra de contribución comienza donde terminó el paso anterior.</p>';
 return html+'<p>Fuente: '+E(CASES[key].source)+'. Copia local, no consulta en vivo.</p></section>';
}
function spendingTable(large,view){
 const st=STATES.spending,rows=DATA.spending.rows,total=rows.find(r=>r.total),max=total?.weight;
 const childCount=id=>rows.filter(r=>r.parent===id).length;
 const selectedIndex=st.item;
 const cols=large?Object.entries(METRICS):[[st.metric,METRICS[st.metric]]];
 const head=['Concepto','Peso (% PIB)',...cols.map(([k,[n,u]])=>n+' ('+u+')')];
 const records=rows.map((r,index)=>{
  if(!large&&r.level&&!st.open.has(r.parent))return '';
  const count=childCount(r.id),canExpand=!large&&count>0;
  const name=canExpand?'<button type="button" class="group-button" data-extra-group="'+r.id+'" data-control="group-'+r.id+'" aria-expanded="'+st.open.has(r.id)+'">'+icon('chevron')+'<span class="group-name">'+E(r.name)+' ('+count+')</span></button>':E(r.name);
  const bar=max&&r.weight!=null?'<span class="spending-bar" aria-hidden="true"><i style="width:'+Math.min(100,Math.max(0,r.weight/max*100))+'%"></i></span>':'';
  const weight='<button type="button" class="micro-target" data-extra-item="'+index+'" data-control="inspect-'+index+'" aria-label="'+E('Consultar '+r.name)+ '">'+E(valueWithUnit(r.weight,'%',2))+bar+'</button>';
  return '<tr class="'+(r.level?'spending-child ':'')+(r.total?'spending-total ':'')+(index===selectedIndex?'selected-row':'')+'"><td>'+name+'</td><td class="spending-weight" data-label="Peso (% PIB)">'+weight+'</td>'+cols.map(([k,[n,u]])=>'<td class="num" data-label="'+E(n+' ('+u+')')+'">'+E(valueWithUnit(r[k],u,2,true))+'</td>').join('')+'</tr>';
 }).join('');
 return '<p class="summary-note">'+E(dateLabel(DATA.spending.date))+' · barra relativa al gasto total; cifra en % del PIB. '+(large?'Todas las subpartidas están visibles.':'Abre los grupos o selecciona una partida para ver sus hijos.')+'</p><div class="extra-table-wrap"><table class="data-table details-table '+(large?'spending-full':'')+'"><caption class="sr-only">Gasto del gobierno central: peso, cambios y crecimiento real.</caption><thead><tr>'+head.map((n,i)=>'<th scope="col"'+(i?' class="num"':'')+'>'+E(n)+'</th>').join('')+'</tr></thead><tbody>'+records+'</tbody></table></div>';
}
function extraView(key,large=false){
 const cfg=CASES[key],view=(large?'large-':'compact-')+key,rr=currentRows(key),r=selected(key,rr);
 let top=large?'<h3>Lectura con contexto</h3>':'<div class="card-title"><div><h3 id="title-'+key+'">'+E(cfg.title)+'</h3></div><button type="button" class="enlarge" data-enlarge="'+key+'" aria-haspopup="dialog" aria-controls="detail-dialog">'+icon('expand')+'<span>Agrandar</span></button></div>';
 top+='<p class="sub">'+E(cfg.sub)+'</p>'+extraControls(key,view);
 let content='';
 if(key==='spending')content=extraReading(key,r)+spendingTable(large,view);
 else{
  let legend='';
  if(key==='activity')legend=cfg.names.map((name,i)=>legendItem(name,cfg.colors[i])).join('');
  if(key==='unemployment')legend=legendItem('Por encima de la mediana','steel','box')+legendItem('Por debajo de la mediana','copper','box');
  if(key==='waterfall')legend=legendItem('Eleva la deuda','copper','box')+legendItem('Reduce la deuda','navy','box')+legendItem('Nivel inicial / final','steel','box');
  content='<div class="legend">'+legend+'</div><p class="axis-unit">'+E(cfg.unit)+'</p><div class="chart-host" data-chart="'+key+'" data-large="'+large+'"></div><p class="query-hint">Pasa el ratón para explorar; clic o toque fija la consulta. Con foco: flechas recorren, Inicio/Fin van a extremos y Escape cierra la ayuda.</p>'+extraReading(key,r);
  if(key==='waterfall')content+=bridgeReconciliation();
 }
 const cut=key==='spending'?dateLabel(DATA.spending.date):key==='waterfall'?bridge().base+' → '+bridge().end:dateLabel(rr.at(-1)?.date||'2026-01');
 const bottom='<p class="source">'+E(cfg.source)+' · '+E(cut)+'</p>'+(large?extraDetails(key,rr,r,view):'<p class="design-note">'+E(cfg.design)+'</p>');
 return '<div class="card" data-case="'+key+'" data-view="'+view+'">'+top+content+bottom+'</div>';
}
caseView=function(key,large=false){return EXTRA_CASES.has(key)?extraView(key,large):originalView(key,large)};
function selectExtra(key,index){
 if(key==='waterfall')STATES[key].step=index;
 else if(key==='spending'){STATES[key].item=index;const row=DATA.spending.rows[index];if(row?.parent)STATES[key].open.add(row.parent)}
 else setDate(key,currentRows(key)[index].date);
 STATES[key].pinned=true;
}
function renderExtraChart(host){
 const key=host.dataset.chart,large=host.dataset.large==='true',rr=currentRows(key),r=selected(key,rr),st=STATES[key];
 if(!rr.length){host.innerHTML='<p class="empty">No hay datos para esta selección.</p>';return}
 const w=Math.max(240,Math.round(host.getBoundingClientRect().width));
 const horizontal=key==='waterfall',h=horizontal?rr.length*(large?64:56)+56:large?360:280;
 const p=horizontal?{l:Math.min(144,Math.max(104,w*.24)),r:24,t:16,b:32}:{l:48,r:16,t:12,b:36};
 const pw=w-p.l-p.r,ph=h-p.t-p.b;
 const domain=niceDomain(horizontal?rr.flatMap(s=>[s.start,s.end]):rr.map(d=>d.values[0]),true);
 const Z=v=>horizontal?p.l+(v-domain.lo)/(domain.hi-domain.lo)*pw:p.t+(domain.hi-v)/(domain.hi-domain.lo)*ph;
 const at=horizontal?Math.min(st.step,rr.length-1):Math.max(0,rr.indexOf(r));
 const step=horizontal?ph/rr.length:pw/rr.length;
 const center=i=>horizontal?p.t+(i+.5)*step:p.l+(i+.5)*step;
 const line=(x1,y1,x2,y2,tone='grid',dash='')=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+color(tone)+'"'+(dash?' stroke-dasharray="'+dash+'"':'')+'/>';
 let grid='',shapes='',labels='';
 for(let tick=domain.lo,n=0;tick<=domain.hi+domain.step*.001&&n<12;tick+=domain.step,n++){
  const z=Z(tick),zero=Math.abs(tick)<domain.step*.001;
  grid+=horizontal?line(z,p.t,z,h-p.b,zero?'reference':'grid'):line(p.l,z,w-p.r,z,zero?'reference':'grid');
  grid+='<text x="'+(horizontal?z:p.l-8)+'" y="'+(horizontal?h-8:z+4)+'" text-anchor="'+(horizontal?'middle':'end')+'">'+E(fmt(Math.abs(tick)<1e-10?0:tick,domain.step<1?1:0))+'</text>';
 }
 rr.forEach((row,i)=>{
  const c=center(i),v=horizontal?row.value:row.values[0];
  if(horizontal){
   const words=row.name.split(' '),limit=w<480?16:22,lines=[''];
   words.forEach(word=>{if((lines.at(-1)+' '+word).trim().length>limit&&lines.at(-1))lines.push(word);else lines[lines.length-1]=(lines.at(-1)+' '+word).trim()});
   labels+='<text x="'+(p.l-12)+'" y="'+(c-(lines.length-1)*7+4)+'" text-anchor="end" style="fill:var(--fg)">'+lines.map((s,j)=>'<tspan x="'+(p.l-12)+'" dy="'+(j?14:0)+'">'+E(s)+'</tspan>').join('')+'</text>';
   if(row.start!=null&&row.end!=null){
    const tone=row.kind==='level'?'steel':v>=0?'copper':'navy';
    shapes+='<rect x="'+Math.min(Z(row.start),Z(row.end))+'" y="'+(c-12)+'" width="'+Math.max(1,Math.abs(Z(row.end)-Z(row.start)))+'" height="24" fill="'+color(tone)+'"/>';
   }
   if(i<rr.length-1&&row.end!=null)shapes+=line(Z(row.end),c+12,Z(row.end),center(i+1)-12,'reference','3 3');
  }else if(v!=null){
   shapes+='<rect x="'+(c-step*.36)+'" y="'+Math.min(Z(0),Z(v))+'" width="'+Math.max(1,step*.72)+'" height="'+Math.max(1,Math.abs(Z(v)-Z(0)))+'" fill="'+color(v<0?'copper':'steel')+'"/>';
  }
 });
 if(!horizontal){
  const n=w<480?3:5;
  [...new Set(Array.from({length:n},(_,i)=>Math.round(i*(rr.length-1)/(n-1))))].forEach((i,j,a)=>{labels+='<text x="'+center(i)+'" y="'+(h-8)+'" text-anchor="'+(j===0?'start':j===a.length-1?'end':'middle')+'">'+E(dateLabel(rr[i].date))+'</text>'});
 }
 const selection=horizontal?'<rect x="'+(p.l-4)+'" y="'+(center(at)-20)+'" width="'+(pw+8)+'" height="40" fill="none" stroke="'+color('fg')+'" stroke-dasharray="3 3"/>':line(center(at),p.t,center(at),h-p.b,'fg','3 3');
 const focused=host.contains(document.activeElement);if(tipOwner&&host.contains(tipOwner))hideTip();
 host.innerHTML='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" tabindex="0" data-control="chart" role="slider" aria-orientation="'+(horizontal?'vertical':'horizontal')+'" aria-label="'+E(CASES[key].title)+'" aria-valuemin="0" aria-valuemax="'+(rr.length-1)+'" aria-valuenow="'+at+'" aria-valuetext="'+E(horizontal?r.name:dateLabel(r.date))+'">'+grid+shapes+selection+labels+'</svg>';
 const svg=host.querySelector('svg');
 const nearest=e=>{
  const bounds=svg.getBoundingClientRect(),coord=horizontal?(e.clientY-bounds.top)*h/bounds.height:(e.clientX-bounds.left)*w/bounds.width;
  return rr.reduce((best,_,i)=>Math.abs(center(i)-coord)<Math.abs(center(best)-coord)?i:best,0);
 };
 const preview=(i,event)=>{
  const bounds=svg.getBoundingClientRect(),x=event?.clientX??bounds.left+(horizontal?w*.55:center(i)),y=event?.clientY??bounds.top+(horizontal?center(i):64);
  showTip(svg,extraTip(key,rr[i]),x,y,key+':'+i,()=>{
   svg.querySelector('[data-hover-marker]')?.remove();const marker=document.createElementNS('http://www.w3.org/2000/svg','g');marker.dataset.hoverMarker='true';marker.setAttribute('aria-hidden','true');marker.setAttribute('pointer-events','none');
   marker.innerHTML=horizontal?'<rect x="'+p.l+'" y="'+(center(i)-22)+'" width="'+pw+'" height="44" fill="'+color('band')+'" stroke="'+color('navy')+'"/>':line(center(i),p.t,center(i),h-p.b,'navy','4 4');svg.append(marker);
  });
 };
 svg.addEventListener('pointermove',e=>{if(e.pointerType==='mouse'&&matchMedia('(hover: hover)').matches)preview(nearest(e),e)});
 svg.addEventListener('pointerleave',()=>leaveTip(svg));
 svg.addEventListener('focus',()=>{if(lastInput==='keyboard')preview(at)});
 svg.addEventListener('blur',()=>{if(dismissedOwner===svg)dismissedOwner=null;if(tipOwner===svg)hideTip()});
 svg.addEventListener('click',e=>{hideTip();selectExtra(key,nearest(e));refresh(key);announce('Consulta fijada')});
 svg.addEventListener('keydown',e=>{
  let index=at;
  if(e.key==='ArrowLeft'||e.key==='ArrowUp')index=Math.max(0,at-1);
  else if(e.key==='ArrowRight'||e.key==='ArrowDown')index=Math.min(rr.length-1,at+1);
  else if(e.key==='Home')index=0;
  else if(e.key==='End')index=rr.length-1;
  else if(e.key!=='Enter'&&e.key!==' ')return;
  e.preventDefault();dismissedOwner=null;hideTip();selectExtra(key,index);refresh(key);announce('Consulta fijada');
 });
 if(focused)svg.focus({preventScroll:true});
}
renderChart=function(host){return host.dataset.chart==='unemployment'||host.dataset.chart==='waterfall'?renderExtraChart(host):originalRender(host)};
document.addEventListener('change',e=>{
 const key=e.target.closest('[data-case]')?.dataset.case,c=e.target.dataset.control;
 if(!EXTRA_CASES.has(key)||!c)return;
 e.stopImmediatePropagation();hideTip();const st=STATES[key],before=selected(key);
 if(c==='date')setDate(key,e.target.value);
 else if(c==='period')setDate(key,currentRows(key)[Number(e.target.value)].date);
 else if(c==='basket'){
  st.basket=e.target.value;DATA.activity=DATA.activityBaskets[st.basket].rows;CASES.activity.names=DATA.activityBaskets[st.basket].names;
  if(before)setDate(key,before.date);
 }else if(c==='window'){
  st.window=e.target.value;const available=currentRows(key),date=available.some(d=>d.date===before?.date)?before.date:available.at(-1)?.date;if(date)setDate(key,date);
 }else if(c==='item')selectExtra(key,Number(e.target.value));
 else if(c==='step')selectExtra(key,Number(e.target.value));
 else if(c==='bridge'){st.bridge=e.target.value;st.step=Math.min(st.step,currentRows(key).length-1)}
 else if(c==='metric')st.metric=e.target.value;
 refresh(key);announce('Selección actualizada');
},true);
function spendingPreview(target,event){
 const row=DATA.spending.rows[Number(target.dataset.extraItem)],bounds=target.getBoundingClientRect();
 if(row)showTip(target,extraTip('spending',row),event?.clientX??bounds.left+bounds.width/2,event?.clientY??bounds.bottom,'spending:'+row.id);
}
document.addEventListener('click',e=>{
 const group=e.target.closest('[data-extra-group]');
 if(group){const id=group.dataset.extraGroup,st=STATES.spending;st.open.has(id)?st.open.delete(id):st.open.add(id);refresh('spending');return}
 const item=e.target.closest('[data-extra-item]');
 if(item){hideTip();selectExtra('spending',Number(item.dataset.extraItem));refresh('spending');announce('Partida fijada en la consulta');return}
 const reset=e.target.closest('[data-extra-reset]');
 if(reset){
  const key=reset.dataset.extraReset,view=reset.closest('[data-view]').dataset.view;
  selectExtra(key,key==='spending'?DATA.spending.rows.findIndex(r=>r.total):currentRows(key).length-1);
  STATES[key].pinned=false;hideTip();refresh(key);document.querySelector('[data-view="'+view+'"] [data-control="'+(key==='spending'?'item':key==='waterfall'?'step':'date')+'"]')?.focus({preventScroll:true});
 }
});
document.addEventListener('pointerover',e=>{const target=e.target.closest('[data-extra-item]');if(target&&e.pointerType==='mouse'&&matchMedia('(hover: hover)').matches&&!target.contains(e.relatedTarget))spendingPreview(target,e)});
document.addEventListener('pointermove',e=>{const target=e.target.closest('[data-extra-item]');if(target&&e.pointerType==='mouse'&&tipOwner===target&&!tip.hidden)positionTip(e.clientX,e.clientY)});
document.addEventListener('pointerout',e=>{const target=e.target.closest('[data-extra-item]');if(target&&!target.contains(e.relatedTarget))leaveTip(target)});
document.addEventListener('focusin',e=>{const target=e.target.closest('[data-extra-item]');if(target&&lastInput==='keyboard')spendingPreview(target)});
document.addEventListener('focusout',e=>{const target=e.target.closest('[data-extra-item]');if(target){if(dismissedOwner===target)dismissedOwner=null;if(tipOwner===target)hideTip()}});
