"""Fuente de la maqueta: python assets/generar_graficos_frecuentes.py --html | --guide.
Lee los JSON originales; no modifica el sitio monitor. La salida HTML es autónoma.
"""
import argparse
import collections
import datetime
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\pablo\OneDrive\Documentos\macro_bz\monitor\qwen3.8-max\site")
DATA = SOURCE / "data"
GROUPS = [
    ("ipca|k7170", "Alimentación y bebidas", "navy"),
    ("ipca|k7445", "Vivienda", "teal"),
    ("ipca|k7625", "Transportes", "plum"),
    ("ipca|k7660", "Salud y cuidados personales", "steel"),
    ("ipca|k7712", "Gastos personales", "history"),
    ("ipca|k7766", "Educación", "secondary"),
    ("ipca|k7486", "Artículos de residencia", "reference"),
    ("ipca|k7558", "Vestuario", "copper"),
    ("ipca|k7786", "Comunicación", "muted"),
]
AGGREGATES = [
    ("ibc", "IBC-Br (sectores)", ["IBC-Br"]),
    ("all", "Todas las series (PMC, PMS, PIM)", ["Comercio", "Servicios", "Industria"]),
    ("pmc", "PMC (actividades)", ["Comercio"]),
    ("pms", "PMS (actividades)", ["Servicios"]),
    ("pim", "PIM (secciones)", ["Industria"]),
]

def rows(name):
    d = json.loads((DATA / (name + ".json")).read_text(encoding="utf-8-sig"))
    return [dict(zip(d["columnas"], x)) for x in d["filas"]]

def months(start, end):
    y, m = map(int, start[:7].split("-"))
    result = []
    while (s := f"{y:04d}-{m:02d}") <= end[:7]:
        result.append(s)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return result

def mul(x):
    return None if x is None else x * 100

def build_data():
    inf = rows("infj_serie")
    index = {(r["categoria_id"], r["fecha"][:7]): r for r in inf}
    dates = sorted(r["fecha"][:7] for r in inf if r["categoria_id"] == "t433" and r["fecha"] >= "2008")
    meta = {str(r["anio"]): r["meta"] for r in rows("od_bcb") if r["meta"] is not None}
    annual = collections.defaultdict(list)
    for r in rows("od_total"):
        if r["meta"] is not None:
            annual[r["fecha"][:4]].append(r["meta"])
    meta.update({y: sum(v) / len(v) for y, v in annual.items()})
    cores = ["n11427", "n27839", "n4466", "n16122", "n28750"]
    inflation = []
    for f in months(dates[0], dates[-1]):
        nuc = [index.get((c, f), {}).get("aa") for c in cores]
        inflation.append({"date": f, "values": [
            mul(index.get(("t433", f), {}).get("aa")),
            mul(sum(nuc) / 5) if all(x is not None for x in nuc) else None,
            mul(meta.get(f[:4])),
        ]})
    fiscal_raw = {r["fecha"][:7]: r for r in rows("fiscal_mensual") if r["fecha"] >= "2010"}
    fiscal = [{"date": f, "values": [
        fiscal_raw.get(f, {}).get("primario_observado_pib"),
        fiscal_raw.get(f, {}).get("primario_estabilizador_pib"),
    ]} for f in months(min(fiscal_raw), max(fiscal_raw))]
    by_combo = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows("grafico_inflacion_v2"):
        by_combo[r["periodo"] + "|" + r["ajuste"]][r["fecha"][:7]].append(r)
    contributions = {}
    for key, fs in by_combo.items():
        values = []
        # Últimos 36 meses reales de cada combinación; no se inventa el calendario.
        for f in sorted(fs)[-36:]:
            rr = fs[f]
            vals = []
            for gid, _, _ in GROUPS:
                matches = [r["aporte"] for r in rr if r["serie_id"] == gid]
                vals.append(mul(sum(matches)) if matches and all(x is not None for x in matches) else None)
            values.append({"date": f, "values": vals, "total": mul(rr[0]["total_ipca"])})
        contributions[key] = values
    members = rows("actv_miembro")
    act = rows("actv_serie")
    ai = {(r["categoria_id"], r["fecha"][:7]): r for r in act}
    last = max(r["fecha"][:7] for r in act)
    months_a = sorted(set(r["fecha"][:7] for r in act))[-24:]
    amplitude = []
    for f in months_a:
        out = []
        for gid, name, families in AGGREGATES:
            seen = set()
            children = []
            for r in members:
                cid = r["categoria_id"]
                if r["unidad"] != "Volumen" or r["rol"] != "Hijo" or r["familia"] not in families or cid in seen:
                    continue
                seen.add(cid)
                a = ai.get((cid, f), {})
                slow, fast = a.get("m12"), a.get("m3a")
                if slow is None or fast is None:
                    continue
                gap = fast - slow
                status = "igual" if abs(gap) <= .001 else ("acelera" if gap > 0 else "desacelera")
                children.append({"id": cid, "name": r["nombre"], "slow": mul(slow), "fast": mul(fast),
                                 "gap": mul(gap), "status": status})
            children.sort(key=lambda r: -r["gap"])
            count = {k: sum(r["status"] == k for r in children) for k in ["acelera", "igual", "desacelera"]}
            out.append({"id": gid, "name": name, "n": len(children), "counts": count, "children": children})
        amplitude.append({"date": f, "groups": out})
    # AM1-01-4: misma columna a12, dos cestas de cuatro series y 48 meses.
    activity = {}
    baskets = {
        "indices": [("v001", "IBC-Br"), ("v006", "Industria (PIM-PF)"), ("v003", "Comercio ampliado (PMC)"), ("v005", "Servicios (PMS)")],
        "ibc": [("v001", "IBC-Br"), ("v007", "IBC-Br agropecuario"), ("v008", "IBC-Br industria"), ("v009", "IBC-Br servicios")],
    }
    dates_activity = sorted(set(r["fecha"][:7] for r in act))[-48:]
    for key, series in baskets.items():
        activity[key] = {"names": [name for _, name in series],
                         "rows": [{"date": f, "values": [mul(ai.get((cid, f), {}).get("a12")) for cid, _ in series]} for f in dates_activity]}
    # AM3-02-3: referencia fija calculada en 2012-2019, no en la ventana visible.
    employment = rows("empleo_pagina")
    reference = statistics.median(r["desocupacion_sa"] for r in employment
                                  if "2012-01-01" <= r["fecha"] <= "2019-12-31" and r["desocupacion_sa"] is not None)
    ei = {r["fecha"][:7]: r for r in employment if r["fecha"] >= "2016-01-01"}
    unemployment = []
    for f in months(min(ei), max(ei)):
        rate = ei.get(f, {}).get("desocupacion_sa")
        unemployment.append({"date": f, "values": [mul(rate - reference) if rate is not None else None],
                             "rate": mul(rate), "reference": mul(reference)})
    # AM4-07-3: nivel y sus hijos; conservar jerarquía, no sumar padres e hijos.
    spending_rows = []
    parent = None
    for i, r in enumerate(sorted(rows("fis_gasto"), key=lambda r: r["orden"])):
        name = r["concepto"].lstrip("\u2003 ·").strip()
        ident = "gasto-" + str(r["orden"])
        if not r["nivel"]:
            parent = ident
        spending_rows.append({"id": ident, "name": name, "level": r["nivel"],
                              "parent": parent if r["nivel"] else None, "total": r["concepto"] == "Gasto total",
                              "weight": mul(r["pct_pib"]), "d1": mul(r["d_pct_1a"]), "d3": mul(r["d_pct_3a"]),
                              "r1": mul(r["real_1a"]), "r2": mul(r["real_2a"]), "r5": mul(r["real_5a"])})
    gasto_raw = rows("fis_gasto")
    spending = {"date": max(r["hasta"][:7] for r in gasto_raw), "rows": spending_rows}
    # AM4-04-0: cada ventana conserva sus propios niveles y componentes originales.
    bridges = collections.defaultdict(list)
    for r in rows("fiscal_cascada"):
        bridges[r["ventana"]].append(r)
    waterfall = []
    for label, rr in sorted(bridges.items(), key=lambda kv: kv[1][0]["orden_ventana"]):
        rr.sort(key=lambda r: r["orden_componente"])
        base = rr[0]
        acc = base["deuda_inicial"]
        steps = [{"name": "Deuda inicial", "kind": "level", "start": 0, "end": acc, "value": acc}]
        for r in rr:
            following = None if acc is None or r["valor"] is None else acc + r["valor"]
            steps.append({"name": r["componente"], "kind": "change", "start": acc, "end": following, "value": r["valor"]})
            acc = following
        steps.append({"name": "Deuda final", "kind": "level", "start": 0, "end": base["deuda_final"], "value": base["deuda_final"]})
        waterfall.append({"id": str(base["orden_ventana"]), "label": label, "base": base["mes_base"], "end": base["mes_fin"],
                          "initial": base["deuda_inicial"], "final": base["deuda_final"],
                          "computed": acc, "difference": None if acc is None else base["deuda_final"] - acc, "steps": steps})
    return {"snapshot": "2026-11-05", "inflation": inflation, "fiscal": fiscal, "contributions": contributions,
            "groups": [{"id": a, "name": b, "color": c} for a, b, c in GROUPS],
            "amplitude": amplitude, "activityLast": last, "activityBaskets": activity,
            "unemployment": unemployment, "spending": spending, "waterfall": waterfall}

CSS = r"""
:root {
 --bg:#F6F7F8;--surface:#FFFFFF;--surface-alt:#F0F4F8;--fg:#24324A;--secondary:#5B6573;
 --muted:#606C7A;--navy:#2E5C8A;--teal:#2F7A86;--plum:#7B5E8C;--steel:#6C819B;
 --history:#A9B8CB;--reference:#8A8F96;--copper:#A85E24;--sand:#EDC9A6;--neutral:#D6DDE6;
 --border:#DCE2E9;--grid:#E6EAEF;--selected:#E8EEF5;--focus:#0C5CAB;--white:#FFFFFF;
 --backdrop:rgba(22,33,50,.52);--band:rgba(108,129,155,.13);
 --font-body:"IBM Plex Sans",sans-serif;--font-display:"Bricolage Grotesque",sans-serif;
 --text-sm:14px;--text-base:16px;--text-lg:20px;--text-title:28px;--text-display:40px;
 --s1:4px;--s2:8px;--s3:12px;--s4:16px;--s6:24px;--s8:32px;--s12:48px;
 --radius:12px;--radius-small:8px;--motion:200ms;--ease:cubic-bezier(.2,0,0,1);
 --tooltip-shadow:0 8px 24px rgba(22,33,50,.16);--tooltip-width:360px;--tooltip-layer:4000;
}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:var(--bg);color:var(--fg);font:var(--text-base)/1.55 var(--font-body)}
::selection{background:var(--navy);color:var(--white)}
button,input,select{font:inherit;color:inherit;caret-color:var(--navy)}
button,a,select,input[type=range]{cursor:pointer}
button:disabled{cursor:not-allowed;opacity:.55}
a{color:var(--navy);text-underline-offset:4px}
:focus-visible{outline:3px solid var(--focus);outline-offset:4px}
button,select,input{min-height:44px}
button,select,input[type=search]{border:1px solid var(--border);border-radius:var(--radius-small);background:var(--surface);padding:var(--s2) var(--s3)}
button{display:inline-flex;align-items:center;justify-content:center;gap:var(--s2);font-weight:600}
button[aria-expanded=true]{background:var(--selected)}
h1,h2,h3{font-family:var(--font-display);line-height:1.2;letter-spacing:-.02em;margin:0;text-wrap:balance}
h1{font-size:clamp(28px,4vw,var(--text-display));max-width:26ch}
h2{font-size:var(--text-title)}h3{font-size:var(--text-lg)}
p{margin:0}svg text{font-family:var(--font-body);font-size:13px;fill:var(--muted)}
.od-icon{fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;--od-icon-size:20px}
.container{max-width:1488px;margin-inline:auto;padding-inline:var(--s8)}
.masthead{border-bottom:1px solid var(--border);background:var(--surface)}
.masthead .container{display:flex;align-items:center;justify-content:space-between;gap:var(--s4);min-height:72px;flex-wrap:wrap;padding-block:var(--s3)}
.brand{font:600 var(--text-lg) var(--font-display);color:var(--navy)}
.masthead a{font-size:var(--text-sm)}
.intro{display:grid;grid-template-columns:1.25fr 1fr;gap:var(--s8);align-items:end;padding-block:var(--s12) var(--s8)}
.intro p{color:var(--secondary);max-width:65ch}
.intro h1+p{margin-top:var(--s4)}
.scope{border-top:1px solid var(--border);padding-top:var(--s4)}
.scope strong{display:block;margin-bottom:var(--s2)}
.family-nav{display:flex;flex-wrap:wrap;gap:var(--s2);margin-bottom:var(--s8)}
.family-nav a{padding:var(--s2) var(--s4);border:1px solid var(--border);border-radius:var(--radius-small);background:var(--surface);text-decoration:none;font-weight:600;min-height:44px;display:flex;align-items:center;gap:var(--s2)}
.count{font-size:var(--text-sm);font-weight:400;color:var(--secondary)}
.family-head{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s4);flex-wrap:wrap;margin-bottom:var(--s6)}
.family-head p{color:var(--secondary);max-width:60ch}
.line-grid,.bottom-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--s6);align-items:start}
.bottom-grid{margin-top:var(--s12)}.bottom-grid>section{min-width:0}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:var(--s6);min-width:0}
.card-title{display:flex;align-items:flex-start;justify-content:space-between;gap:var(--s4)}
.card-title h3{max-width:34ch}.card-title .enlarge{flex:none}
.sub{color:var(--secondary);margin-top:var(--s2);font-size:var(--text-sm)}
.controls{display:flex;flex-wrap:wrap;gap:var(--s3);margin-block:var(--s6) var(--s4);align-items:end}
.field{display:grid;gap:var(--s1);flex:1 1 128px;min-width:0}
label{font-size:var(--text-sm);font-weight:600}
select,input[type=search]{width:100%;min-width:0}
.legend{display:flex;flex-wrap:wrap;gap:var(--s2) var(--s4);font-size:var(--text-sm);padding-block:var(--s2)}
.legend span{display:flex;align-items:center;gap:var(--s2)}
.swatch{display:inline-block;width:20px;height:3px;background:var(--tone);flex:none}
.swatch.dashed{height:0;border-top:2px dashed var(--tone);background:none}
.swatch.box{width:10px;height:10px}
.chart-host{min-width:0;margin-top:var(--s3)}
.chart-host svg{display:block;width:100%;touch-action:pan-y}
.axis-unit{color:var(--secondary);font-size:var(--text-sm);margin-top:var(--s4)}
.query-hint{font-size:var(--text-sm);color:var(--secondary);margin-top:var(--s2)}
.chart-host svg[tabindex]{cursor:crosshair;border-radius:var(--s1)}
.chart-tooltip{position:fixed;inset:auto;margin:0;padding:var(--s4);width:min(var(--tooltip-width),calc(100vw - 32px));max-height:calc(100dvh - 32px);overflow-y:auto;overscroll-behavior:contain;background:var(--surface);color:var(--fg);border:1px solid var(--border);border-radius:var(--radius-small);box-shadow:var(--tooltip-shadow);z-index:var(--tooltip-layer);font:var(--text-sm)/1.5 var(--font-body);font-variant-numeric:tabular-nums;scrollbar-color:var(--history) var(--surface-alt)}
.chart-tooltip[hidden]{display:none}
.tip-heading{display:grid;gap:var(--s1);margin-bottom:var(--s3)}
.tip-heading strong{font-size:var(--text-base);line-height:1.4;overflow-wrap:anywhere}
.tip-heading span,.tip-caption,.tip-footer{color:var(--secondary)}
.tip-row{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:baseline;gap:var(--s3);padding-block:var(--s1)}
.tip-label{display:flex;align-items:baseline;gap:var(--s2);overflow-wrap:anywhere}
.tip-label i{display:block;flex:none;width:8px;height:8px;background:var(--tone)}
.tip-row>strong{white-space:nowrap;text-align:right;font-size:var(--text-base)}
.tip-primary{border-bottom:1px solid var(--border);margin-bottom:var(--s2);padding-bottom:var(--s2)}
.tip-primary>strong{font-size:var(--text-lg)}
.tip-caption{font-size:var(--text-sm);margin-block:var(--s2)}
.tip-footer{border-top:1px solid var(--border);padding-top:var(--s2);margin-top:var(--s3)}
.micro-target{display:block;width:100%;min-height:44px;padding:var(--s2) 0;border:0;background:transparent;border-radius:var(--s1)}
.micro-target .mix{pointer-events:none}
.table-inspection{margin-block:var(--s4);padding:var(--s4);background:var(--surface-alt);border-radius:var(--radius-small)}
.table-inspection .tip-footer{display:none}
.table-inspection .reading-head{margin-bottom:var(--s3)}
.table-inspection .tip-heading{margin-top:var(--s3)}
.reading{padding:var(--s4);background:var(--surface-alt);border-radius:var(--radius-small);margin-top:var(--s4);font-variant-numeric:tabular-nums;min-height:96px}
.reading-head{display:flex;align-items:baseline;justify-content:space-between;gap:var(--s2);flex-wrap:wrap;margin-bottom:var(--s2)}
.values{display:flex;flex-wrap:wrap;gap:var(--s2) var(--s6)}
.values .od-stat{--od-gap:0px;min-width:112px}.values strong{font-size:var(--text-lg);white-space:nowrap}
.values span{font-size:var(--text-sm);color:var(--secondary)}
.source{border-top:1px solid var(--border);padding-top:var(--s3);margin-top:var(--s4);font-size:var(--text-sm);color:var(--secondary)}
.design-note{color:var(--secondary);font-size:var(--text-sm);margin-top:var(--s4);max-width:70ch}
.summary-note{padding-block:var(--s4);color:var(--secondary)}
.legend-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--s2) var(--s3)}
.legend-columns span{align-items:flex-start}
.legend-columns .swatch{margin-top:var(--s1)}
.data-table{width:100%;border-collapse:collapse;font-size:var(--text-sm);font-variant-numeric:tabular-nums}
.data-table th{text-align:left;font-weight:600;color:var(--secondary);border-bottom:1px solid var(--fg);padding:var(--s3) var(--s2)}
.data-table td{padding:var(--s3) var(--s2);border-bottom:1px solid var(--border);vertical-align:middle}
.data-table .num{text-align:right;white-space:nowrap}
.data-table caption{text-align:left;padding-block:var(--s4);color:var(--secondary)}
.group-button{border:0;background:none;min-height:44px;padding:0;text-align:left;justify-content:flex-start;font-size:var(--text-base);width:100%}
.group-name{display:block;overflow-wrap:anywhere}.group-button .od-icon{flex:none;transition:transform var(--motion) var(--ease)}
.group-button[aria-expanded=true] .od-icon{transform:rotate(90deg)}
.mix{display:flex;height:16px;width:100%;min-width:72px;background:var(--surface-alt);border-radius:var(--s1)}
.mix i{display:block;height:100%}
.mix-meta{display:block;font-size:var(--text-sm);color:var(--secondary);margin-top:var(--s1)}
.amplitude-table th:first-child{width:42%}.amplitude-table th:nth-child(2){width:42%}
.component-list{display:grid;gap:var(--s3);padding:var(--s2)}
.component{padding-block:var(--s3);border-bottom:1px solid var(--border);display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:var(--s3);align-items:center}
.component:last-child{border:0}
.component strong{font-weight:500;overflow-wrap:anywhere}
.component svg{width:100%;display:block}
.component .values{grid-column:1/-1;gap:var(--s2) var(--s4)}
.component .values .od-stat{min-width:96px}
.component .values strong{font-size:var(--text-base)}
.status{font-size:var(--text-sm);display:block;color:var(--secondary);margin-top:var(--s1)}
.empty{padding:var(--s6);background:var(--surface-alt);border-radius:var(--radius-small);color:var(--secondary)}
.details-block{border-top:1px solid var(--border);padding-top:var(--s6);margin-top:var(--s8)}
.details-block h3{margin-bottom:var(--s4)}
.details-block p{max-width:75ch}.details-block p+p{margin-top:var(--s3)}
.period-query{margin-block:var(--s4);display:flex;align-items:center;gap:var(--s4);flex-wrap:wrap}
.period-query input[type=range]{width:min(100%,560px);flex:1 1 160px;accent-color:var(--navy)}
.period-query output{font-variant-numeric:tabular-nums;white-space:nowrap}
.formula{font-variant-numeric:tabular-nums;color:var(--navy);font-weight:600}
dialog{padding:0;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--fg);width:min(1200px,calc(100vw - 48px));max-height:92dvh}
dialog::backdrop{background:var(--backdrop)}
.dialog-layout{display:flex;flex-direction:column;max-height:92dvh}
.dialog-header{display:flex;justify-content:space-between;align-items:center;gap:var(--s4);padding:var(--s6);border-bottom:1px solid var(--border);flex:none}
.dialog-header h2{font-size:var(--text-title);max-width:42ch}
.dialog-body{overflow-y:auto;padding:var(--s6);min-height:0;overscroll-behavior:contain;scrollbar-color:var(--history) var(--surface-alt)}
.dialog-body .card{border:0;padding:0}
.dialog-body .reading{min-height:0}
.footer{padding-block:var(--s12);color:var(--secondary);max-width:75ch}
.case-stack{display:grid;gap:var(--s6)}
.cascade-section{margin-top:var(--s12)}
.spending-bar{display:block;width:100%;height:8px;margin-top:var(--s2);background:var(--surface-alt);border-radius:var(--s1)}
.spending-bar i{display:block;height:100%;background:var(--navy);border-radius:var(--s1)}
.spending-weight{min-width:80px;font-variant-numeric:tabular-nums}
.spending-weight .micro-target{padding-inline:var(--s1);text-align:right}
.spending-child td:first-child{padding-left:var(--s6)}
.spending-total{font-weight:600;border-top:2px solid var(--fg)}
.selected-row{background:var(--selected)}
.extra-reading{margin-bottom:var(--s4)}
.extra-table-wrap{min-width:0}
.spending-full th:first-child{width:28%}
.spending-full .micro-target{text-align:left}
.card[data-case=spending] .controls>.field{flex-basis:100%}
.bridge-status{margin-top:var(--s3);font-size:var(--text-sm)}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
@media(hover:hover){button:hover{background:var(--selected);border-color:var(--navy)}a:hover{color:var(--fg);text-decoration:underline}.group-button:hover{background:var(--surface-alt)}}
@media(min-width:1440px){.container{padding-inline:var(--s12)}}
@media(max-width:1023px){.container{padding-inline:var(--s6)}.intro{grid-template-columns:1fr}.line-grid,.bottom-grid{grid-template-columns:1fr}.card-title h3{max-width:48ch}.legend-columns{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:767px){.container{padding-inline:var(--s4)}.intro{padding-top:var(--s8)}.card{padding:var(--s4)}.card-title{flex-wrap:wrap}.card-title h3{font-size:var(--text-lg);max-width:none}.enlarge{margin-left:auto}.legend-columns{grid-template-columns:repeat(2,minmax(0,1fr))}.bottom-grid{margin-top:var(--s8)}dialog{width:calc(100vw - 16px);max-height:96dvh;border-radius:var(--radius-small)}.dialog-layout{max-height:96dvh}.dialog-header,.dialog-body{padding:var(--s4)}.dialog-header h2{font-size:var(--text-lg)}.dialog-header button span{display:none}.data-table th,.data-table td{padding:var(--s2) var(--s1)}.component{grid-template-columns:1fr}.component .values{grid-column:auto}.amplitude-table th:first-child{width:44%}.amplitude-table th:nth-child(2){width:36%}.mix-meta{font-size:12px}.details-table thead{display:none}.details-table tr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-bottom:1px solid var(--border);padding-block:var(--s2)}.details-table td{border:0;text-align:left!important;white-space:normal!important}.details-table td:first-child{grid-column:1/-1;font-weight:600}.details-table td::before{content:attr(data-label);display:block;font-size:12px;color:var(--secondary)}.details-table td:first-child::before{display:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{transition:none!important;animation:none!important}}
"""

BODY = r"""
<div id="page">
<header class="masthead"><div class="container"><a class="brand" href="#inicio">Monitor Brasil</a><a href="IMPLEMENTACION_GRAFICOS.md">Guía de implementación</a></div></header>
<main class="container" id="inicio">
 <div class="intro">
  <div><h1>Más claridad en cada gráfico</h1><p>Ocho casos reales para explorar líneas, tablas, columnas y cascadas. La tarjeta resume; “Agrandar” conserva la selección y abre el detalle.</p></div>
  <div class="scope"><strong>Cuatro familias · 97 tarjetas en el inventario</strong><p>Esta maqueta desarrolla ocho casos representativos. Los datos son una copia local de las tablas del monitor, con cortes distintos según la fuente.</p></div>
 </div>
 <nav class="family-nav" aria-label="Familias de gráficos"><a href="#lineas">Líneas <span class="count">53 tarjetas</span></a><a href="#tablas">Tablas <span class="count">20 tarjetas</span></a><a href="#columnas">Columnas <span class="count">16 tarjetas</span></a><a href="#cascadas">Cascadas <span class="count">8 tarjetas</span></a></nav>
 <section id="lineas" aria-labelledby="line-heading">
  <div class="family-head"><h2 id="line-heading">Líneas que explican la comparación</h2><p>Una referencia visible y un punto de consulta compartido por todas las series.</p></div>
  <div class="line-grid"><article id="card-inflation"></article><article id="card-fiscal"></article><article id="card-activity"></article></div>
 </section>
 <div class="bottom-grid">
  <section id="tablas" aria-labelledby="table-heading"><div class="family-head"><h2 id="table-heading">Tablas para explorar</h2></div><div class="case-stack"><article id="card-amplitude"></article><article id="card-spending"></article></div></section>
  <section id="columnas" aria-labelledby="column-heading"><div class="family-head"><h2 id="column-heading">Columnas con contexto</h2></div><div class="case-stack"><article id="card-contributions"></article><article id="card-unemployment"></article></div></section>
 </div>
 <section id="cascadas" class="cascade-section" aria-labelledby="cascade-heading"><div class="family-head"><h2 id="cascade-heading">Una cascada que cierra la cuenta</h2><p>Nivel inicial, contribuciones y nivel final, con el residuo visible.</p></div><article id="card-waterfall"></article></section>
 <footer class="footer"><p>Los valores proceden de los archivos locales del monitor, extraídos el 5 de noviembre de 2026. Las mejoras son propuestas de diseño; las bandas y colores describen relaciones entre datos, sin calificarlas como buenas o malas por defecto.</p></footer>
</main>
</div>
<dialog id="detail-dialog" aria-labelledby="dialog-title"><div class="dialog-layout"><header class="dialog-header"><h2 id="dialog-title"></h2><button type="button" id="close-dialog" aria-label="Cerrar detalle"><svg class="od-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg><span>Cerrar</span></button></header><div id="dialog-content" class="dialog-body"></div></div></dialog>
<div id="announcement" class="sr-only" role="status" aria-live="polite"></div>
"""

JS = r"""
'use strict';
// ADAPTADORES: DATA conserva fechas mensuales, null y unidades finales explícitas.
const DATA=JSON.parse(document.getElementById('chart-data').textContent);
const CASES={
 inflation:{title:'IPCA y núcleos desde 2008',sub:'% a/a · IPCA, promedio de cinco núcleos y meta',unit:'% a/a',source:'IBGE, BCB y CMN · infj_serie, od_bcb y od_total',note:'Las bandas señalan meses con IPCA sobre el promedio de núcleos. La meta sólo aparece donde existe un dato local.',design:'Separa observado y referencia; reduce el peso de las bandas y conserva el último mes identificable.',names:['IPCA','Núcleos (promedio)','Meta'],colors:['navy','teal','reference']},
 fiscal:{title:'Primario observado frente al estabilizador',sub:'% del PIB · sector público consolidado · 12 meses',unit:'% del PIB',source:'BCB · fiscal_mensual · cálculo de dinámica de deuda del monitor',note:'Brecha = primario estabilizador − observado. El relleno distingue falta de primario y superávit respecto del estabilizador; no es un intervalo de confianza.',design:'Hace explícitos el cero, las unidades y los cambios de signo de la brecha.',names:['Primario observado','Estabilizador'],colors:['navy','reference']},
 amplitude:{title:'Cuántos componentes aceleran',sub:'Cinco agregados · comparación de 3m a/a con 12m a/a',source:'IBGE y BCB · actv_serie y actv_miembro · cálculo del monitor',note:'Acelera si 3m a/a − 12m a/a supera 0,1 pp; igual si la diferencia absoluta es ≤ 0,1 pp. Se excluyen componentes sin ambos datos del mes.',design:'Expone el denominador, los tres estados y el acceso a componentes sin depender del color.'},
 contributions:{title:'Aportes al IPCA por grupo',sub:'Nueve grupos · aportes en pp y línea del IPCA en %',unit:'Aportes: pp · línea IPCA: %',source:'IBGE / IPCA · grafico_inflacion_v2 · cálculo del monitor',note:'Los nueve grupos se conservan en todas las vistas. No se normalizan a 100 %. La diferencia entre suma y total se informa, sin redistribuirla.',design:'Conserva los nueve grupos, dibuja negativos desde cero y permite leer el desglose del mes.'}
};
const STATES={inflation:{window:'all',at:DATA.inflation.length-1},fiscal:{window:'all',at:DATA.fiscal.length-1},
 amplitude:{at:DATA.amplitude.length-1,open:new Set(),query:'',order:'source'},
 contributions:{window:'24',variation:'a/a',adjust:'Sin ajuste',date:null}};
Object.values(STATES).forEach(s=>{s.pinned=false});
STATES.amplitude.inspection=null;
let activeCase=null,opener=null,observer;
const dialog=document.getElementById('detail-dialog');
const E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const color=k=>getComputedStyle(document.documentElement).getPropertyValue('--'+k).trim();
const fmt=(v,d=1)=>v==null||!Number.isFinite(v)?'Sin dato':new Intl.NumberFormat('es-CL',{minimumFractionDigits:d,maximumFractionDigits:d}).format(v);
const signed=v=>v==null?'Sin dato':(v>0?'+':'')+fmt(v);
const dateLabel=f=>{const [y,m]=f.split('-');return ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'][Number(m)-1]+' '+y};
const time=f=>{const [y,m]=f.split('-').map(Number);return Date.UTC(y,m-1,1)};
const icon=(name)=>'<svg class="od-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="'+(name==='expand'?'M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7':'m9 5 7 7-7 7')+'"/></svg>';
function legendItem(name,k,kind='line'){return '<span><i class="swatch '+(kind==='dash'?'dashed':kind==='box'?'box':'')+'" style="--tone:var(--'+k+')"></i>'+E(name)+'</span>'}
function field(key,label,value,options,view){return '<div class="field od-field"><label for="'+view+'-'+key+'">'+E(label)+'</label><select id="'+view+'-'+key+'" data-control="'+key+'">'+options.map(o=>{const [v,n]=Array.isArray(o)?o:[o,o];return '<option value="'+E(v)+'"'+(String(v)===String(value)?' selected':'')+'>'+E(n)+'</option>'}).join('')+'</select></div>'}
function contributionRows(){return DATA.contributions[STATES.contributions.variation+'|'+STATES.contributions.adjust]||[]}
function currentRows(key){if(key==='amplitude')return DATA.amplitude;if(key==='contributions'){const rr=contributionRows();return rr.slice(-Number(STATES[key].window))}const rr=DATA[key];return STATES[key].window==='all'?rr:rr.slice(-Number(STATES[key].window))}
function selected(key,rr=currentRows(key)){if(!rr.length)return null;if(key==='contributions'){return rr.find(r=>r.date===STATES[key].date)||rr.at(-1)}const full=key==='amplitude'?DATA.amplitude:DATA[key];const date=full[STATES[key].at]?.date;return rr.find(r=>r.date===date)||rr.at(-1)}
// La vista previa es efímera: sólo setDate / pinTable cambian la consulta persistente.
let tip=null,tipOwner=null,tipDescription=null,tipTimer=null,tipHideTimer=null,tipToken='',dismissedOwner=null,lastInput='keyboard';
const valueWithUnit=(v,unit,d=2,sign=false)=>v==null||!Number.isFinite(v)?'Sin dato':(sign&&v>0?'+':'')+fmt(v,d)+(unit?' '+unit:'');
function tipRow(label,value,unit='',tone='',primary=false,sign=false){
 return '<div class="tip-row'+(primary?' tip-primary':'')+'"><span class="tip-label">'+(tone?'<i aria-hidden="true" style="--tone:var(--'+tone+')"></i>':'')+E(label)+'</span><strong>'+E(typeof value==='string'?value:valueWithUnit(value,unit,2,sign))+'</strong></div>';
}
function tooltipContent(key,r,kind=null,id=null,groupId=null,persistent=false){
 if(!r)return '<p>Sin datos para esta fecha.</p>';
 let head='',body='';
 if(key==='amplitude'){
  const group=r.groups.find(g=>g.id===(kind==='group'?id:groupId));
  const c=kind==='component'?group?.children.find(c=>c.id===id):null;
  if(!group||(kind==='component'&&!c))return '<p>Sin datos para el elemento consultado en '+E(dateLabel(r.date))+'. Selecciona otro componente.</p>';
  head='<div class="tip-heading"><strong>'+E(c?c.name:group.name)+'</strong><span>'+E(dateLabel(r.date))+' · '+(c?'Ritmo del componente':'Composición del agregado')+'</span></div>';
  if(c){
   body=tipRow('Diferencia',c.gap,'pp','',true,true)+tipRow('12m a/a · círculo vacío',c.slow,'%','reference')+tipRow('3m a/a · círculo lleno',c.fast,'%','navy');
   body+='<p class="tip-caption">'+E(c.status==='igual'?'Sin cambio de ritmo: diferencia absoluta ≤ 0,1 pp.':c.status==='acelera'?'Acelera: 3m a/a supera 12m a/a en más de 0,1 pp.':'Desacelera: 3m a/a queda por debajo de 12m a/a en más de 0,1 pp.')+'</p>';
  }else{
   body=tipRow('Componentes que aceleran',group.n?100*group.counts.acelera/group.n:null,'%','',true);
   body+=tipRow('Aceleran',String(group.counts.acelera)+' de '+group.n,'','navy')+tipRow('Iguales',String(group.counts.igual)+' de '+group.n,'','neutral')+tipRow('Desaceleran',String(group.counts.desacelera)+' de '+group.n,'','copper');
   body+='<p class="tip-caption">Denominador: componentes con ambas tasas del mes. Igual significa diferencia absoluta ≤ 0,1 pp.</p>';
  }
 }else{
  head='<div class="tip-heading"><strong>'+E(dateLabel(r.date))+'</strong><span>'+E(key==='inflation'?'Inflación · variación a/a':key==='fiscal'?'Primario · 12 meses':'IPCA · '+({'m/m':'mes a mes','3m':'trimestre a trimestre','a/a':'año a año'}[STATES.contributions.variation])+' · '+STATES.contributions.adjust)+'</span></div>';
  if(key==='inflation')body=r.values.map((v,i)=>tipRow(CASES[key].names[i],v,'% a/a',CASES[key].colors[i],i===0)).join('');
  if(key==='fiscal'){
   const [a,b]=r.values,gap=a==null||b==null?null:b-a;
   body=tipRow('Brecha · estabilizador − observado',gap,'pp','',true,true)+tipRow('Primario observado',a,'% PIB','navy')+tipRow('Estabilizador',b,'% PIB','reference');
   body+='<p class="tip-caption">'+E(gap==null?'No hay ambos valores para calcular la brecha.':gap>0?'Falta primario para alcanzar el estabilizador.':gap<0?'El observado supera al estabilizador.':'El observado coincide con el estabilizador.')+'</p>';
  }
  if(key==='contributions')body=tipRow('IPCA total',r.total,'%','fg',true)+'<p class="tip-caption">Aportes por grupo · puntos porcentuales</p>'+DATA.groups.map((g,i)=>tipRow(g.name,r.values[i],'pp',g.color,false,true)).join('');
 }
 return head+body+(persistent?'':'<p class="tip-footer">Vista previa · clic, toque o Enter conserva la consulta. Escape cierra esta ayuda.</p>');
}
function ensureTip(){
 if(tip)return;
 tip=document.createElement('div');tip.id='chart-tooltip';tip.className='chart-tooltip';tip.setAttribute('role','tooltip');tip.setAttribute('popover','manual');tip.hidden=true;document.body.append(tip);
 tip.addEventListener('pointerenter',()=>clearTimeout(tipHideTimer));
 tip.addEventListener('pointerleave',()=>hideTip());
}
function hideTip(dismiss=false){
 clearTimeout(tipTimer);clearTimeout(tipHideTimer);
 if(dismiss)dismissedOwner=tipOwner;
 if(tipOwner){if(tipDescription==null)tipOwner.removeAttribute('aria-describedby');else tipOwner.setAttribute('aria-describedby',tipDescription)}
 if(tip){if(typeof tip.hidePopover==='function'&&tip.matches(':popover-open'))tip.hidePopover();tip.hidden=true}
 document.querySelectorAll('[data-hover-marker]').forEach(n=>n.remove());
 tipOwner=null;tipDescription=null;tipToken='';
}
function positionTip(x,y){
 const width=tip.offsetWidth,height=tip.offsetHeight,vw=document.documentElement.clientWidth,vh=window.innerHeight;
 let left=x+16;if(left+width>vw-16)left=x-width-16;
 let top=y+16;if(top+height>vh-16)top=y-height-16;
 tip.style.left=Math.max(16,Math.min(left,vw-width-16))+'px';
 tip.style.top=Math.max(16,Math.min(top,vh-height-16))+'px';
}
function showTip(owner,html,x,y,token,mark=null){
 if(dismissedOwner===owner)return;
 ensureTip();clearTimeout(tipHideTimer);
 if(tipOwner!==owner){
  hideTip();tipOwner=owner;tipDescription=owner.getAttribute('aria-describedby');owner.setAttribute('aria-describedby',((tipDescription||'')+' '+tip.id).trim());
 }
 tip.innerHTML=html;tipToken=token;clearTimeout(tipTimer);
 const show=()=>{
  if(!owner.isConnected||tipOwner!==owner||dismissedOwner===owner)return;
  const mount=dialog.open?dialog:document.body;if(tip.parentNode!==mount)mount.append(tip);
  tip.hidden=false;
  if(typeof tip.showPopover==='function'&&!tip.matches(':popover-open'))tip.showPopover();
  positionTip(x,y);if(mark)mark();
 };
 if(!tip.hidden)show();else tipTimer=setTimeout(show,120);
}
function leaveTip(owner){if(dismissedOwner===owner)dismissedOwner=null;clearTimeout(tipTimer);tipHideTimer=setTimeout(()=>{if(tipOwner===owner)hideTip()},160)}
function tableRecord(target){
 const row=selected('amplitude');if(!row)return null;
 return {row,kind:target.dataset.tipKind,id:target.dataset.tipId,group:target.dataset.tipGroup||null};
}
function tablePreview(target,event){
 const item=tableRecord(target);if(!item)return;
 const rect=target.getBoundingClientRect();
 showTip(target,tooltipContent('amplitude',item.row,item.kind,item.id,item.group),event?.clientX??rect.left+rect.width/2,event?.clientY??rect.bottom,'amplitude:'+item.row.date+':'+item.kind+':'+item.id);
}
function pinTable(target){
 const item=tableRecord(target);if(!item)return;
 STATES.amplitude.inspection={kind:item.kind,id:item.id,group:item.group};STATES.amplitude.pinned=true;
 hideTip();refresh('amplitude');announce('Detalle del componente o agregado conservado en la tabla');
}
function tableInspection(r){
 const s=STATES.amplitude.inspection;if(!s)return '';
 return '<section class="table-inspection" aria-label="Consulta de tabla fijada"><div class="reading-head"><strong>Consulta fijada</strong><button type="button" data-release="amplitude">Limpiar consulta</button></div>'+tooltipContent('amplitude',r,s.kind,s.id,s.group,true)+'</section>';
}
function valueBlock(label,value){return '<div class="od-stat"><strong>'+E(value)+'</strong><span>'+E(label)+'</span></div>'}
function reading(key,r){if(!r)return '<div class="empty">No hay datos para esta selección. Elige otra variación o ajuste.</div>';
 let content='';
 if(key==='contributions'){
  const sum=r.values.every(v=>v!=null)?r.values.reduce((a,b)=>a+b,0):null;
  content=valueBlock('IPCA total',fmt(r.total,2)+' %')+valueBlock('Suma de aportes',fmt(sum,2)+' pp')+valueBlock('Total − suma',signed(sum==null||r.total==null?null:r.total-sum)+' pp');
 }else if(key==='fiscal'){
  const [a,b]=r.values,gap=a==null||b==null?null:b-a;
  content=valueBlock('Observado',fmt(a)+' % PIB')+valueBlock('Estabilizador',fmt(b)+' % PIB')+valueBlock(gap==null?'Brecha':gap>=0?'Falta primario':'Sobre el estabilizador',fmt(gap==null?null:Math.abs(gap))+' pp');
 }else{content=r.values.map((v,i)=>valueBlock(CASES[key].names[i],v==null?'Sin dato':fmt(v)+' %')).join('')}
 return '<div class="reading"><div class="reading-head"><strong>'+E(dateLabel(r.date))+'</strong>'+(STATES[key].pinned?'<button type="button" data-release="'+key+'">Ver último mes</button>':'<span>Fecha consultada</span>')+'</div><div class="values">'+content+'</div>'+(STATES[key].pinned?'<p class="query-hint">Consulta fijada · recorrer el gráfico no cambia estos valores.</p>':'')+'</div>';
}
function makeControls(key,view){
 const state=STATES[key],rr=currentRows(key),r=selected(key,rr);
 let fields='';
 if(key==='contributions'){
 fields+=field('variation','Variación',state.variation,[['m/m','Mes a mes'],['3m','Trimestre a trimestre'],['a/a','Año a año']],view);
 fields+=field('adjust','Ajuste',state.adjust,['Sin ajuste','Desestacionalizado'],view);
 fields+=field('window','Ventana',state.window,[['12','12 meses'],['24','24 meses'],['36','36 meses']],view);
 }else if(key!=='amplitude'){fields+=field('window','Ventana',state.window,[['all','Historia completa'],['120','Últimos 10 años'],['60','Últimos 5 años']],view)}
 fields+=field('date','Consultar mes',r?.date||'',rr.map(x=>[x.date,dateLabel(x.date)]),view);
 if(key==='amplitude'){fields+=field('order','Ordenar agregados',state.order,[['source','Orden del monitor'],['high','Mayor % que acelera'],['low','Menor % que acelera']],view)}
 return '<div class="controls">'+fields+'</div>';
}
function caseView(key,large=false){
 const cfg=CASES[key],view=(large?'large-':'compact-')+key,rr=currentRows(key),r=selected(key,rr);
 let top=large?'<h3>Lectura con contexto</h3>':'<div class="card-title"><div><h3 id="title-'+key+'">'+E(cfg.title)+'</h3></div><button type="button" class="enlarge" data-enlarge="'+key+'" aria-haspopup="dialog" aria-controls="detail-dialog">'+icon('expand')+'<span>Agrandar</span></button></div>';
 top+='<p class="sub">'+E(cfg.sub)+'</p>'+makeControls(key,view);
 let chart='';
 if(key==='amplitude'){chart=amplitudeTable(r,key,view,large)}
 else{
  let legend='';
  if(key==='contributions'){legend=DATA.groups.map(g=>legendItem(g.name,g.color,'box')).join('')+legendItem('IPCA total','fg')}
  else {legend=cfg.names.map((n,i)=>legendItem(n,cfg.colors[i],i===cfg.names.length-1?'dash':'line')).join('');if(key==='inflation')legend+=legendItem('IPCA > núcleos','neutral','box');else legend+=legendItem('Falta primario','sand','box')+legendItem('Sobre estabilizador','history','box')}
  chart='<div class="legend '+(key==='contributions'?'legend-columns':'')+'">'+legend+'</div><p class="axis-unit">'+E(cfg.unit)+'</p><div class="chart-host" data-chart="'+key+'" data-large="'+large+'"></div><p class="query-hint">Pasa el ratón para explorar; clic o toque fija la consulta. Con foco en el gráfico: flechas cambian de mes y Escape cierra la ayuda.</p>'+reading(key,r);
 }
 let bottom='<p class="source">'+E(cfg.source)+' · corte disponible: '+E(dateLabel(rr.at(-1)?.date||'2026-01'))+'</p>';
 if(large){bottom+=expandedDetails(key,rr,r,view)}
 else bottom+='<p class="design-note">'+E(cfg.design)+'</p>';
 return '<div class="card" data-case="'+key+'" data-view="'+view+'">'+top+chart+bottom+'</div>';
}
function amplitudeTable(r,key,view,large){
 if(!r)return '<div class="empty">No hay componentes disponibles para este mes.</div>';
 const st=STATES.amplitude,q=st.query.trim().toLocaleLowerCase('es');
 let gs=[...r.groups];
 if(st.order!=='source')gs.sort((a,b)=>((a.n?a.counts.acelera/a.n:-1)-(b.n?b.counts.acelera/b.n:-1))*(st.order==='high'?-1:1));
 const search='<div class="field od-field"><label for="'+view+'-search">Buscar agregado o componente</label><input id="'+view+'-search" type="search" data-control="search" value="'+E(st.query)+'" placeholder="Ejemplo: transporte"></div>';
 let rendered=0;
 const html=gs.map(g=>{
  const matchGroup=g.name.toLocaleLowerCase('es').includes(q),children=q&&!matchGroup?g.children.filter(c=>c.name.toLocaleLowerCase('es').includes(q)):g.children;
  if(q&&!matchGroup&&!children.length)return '';
  rendered++;
  const open=st.open.has(g.id)||!!q,childrenId=view+'-children-'+g.id,counts=g.counts;
  const mix=g.n?'<button type="button" class="micro-target" data-tip-kind="group" data-tip-id="'+g.id+'" aria-label="'+E('Consultar '+g.name+': '+counts.acelera+' aceleran, '+counts.igual+' iguales y '+counts.desacelera+' desaceleran, de '+g.n)+'"><span class="mix" aria-hidden="true">'+[['acelera','navy'],['igual','neutral'],['desacelera','copper']].map(([s,c])=>'<i style="width:'+(counts[s]/g.n*100)+'%;background:var(--'+c+')"></i>').join('')+'</span></button><span class="mix-meta">'+counts.acelera+' / '+counts.igual+' / '+counts.desacelera+' · n = '+g.n+'</span>':'Sin pares válidos';
  let line='<tr><td><button type="button" class="group-button" data-group="'+g.id+'" aria-expanded="'+open+'" aria-controls="'+childrenId+'">'+icon('chevron')+'<span class="group-name">'+E(g.name)+'</span></button></td><td>'+mix+'</td><td class="num">'+(g.n?fmt(100*counts.acelera/g.n,0)+' %':'Sin dato')+'</td></tr>';
  const values=g.children.flatMap(c=>[c.slow,c.fast]),lo=Math.min(0,...values),hi=Math.max(1,...values);
  line+='<tr id="'+childrenId+'"'+(open?'':' hidden')+'><td colspan="3"><div class="component-list">'+children.map(c=>{
    const x=v=>8+(v-lo)/(hi-lo)*184,tone=c.status==='acelera'?'navy':c.status==='desacelera'?'copper':'muted';
    const mini='<svg viewBox="0 0 200 28" width="200" height="28" role="img" aria-label="'+E('12m a/a '+fmt(c.slow)+' por ciento; 3m a/a '+fmt(c.fast)+' por ciento')+'"><line x1="'+x(c.slow)+'" x2="'+x(c.fast)+'" y1="14" y2="14" stroke="'+color(tone)+'" stroke-width="2"/><circle cx="'+x(c.slow)+'" cy="14" r="5" fill="'+color('surface')+'" stroke="'+color(tone)+'" stroke-width="2"/><circle cx="'+x(c.fast)+'" cy="14" r="5" fill="'+color(tone)+'"/></svg>';
    return '<div class="component"><div><strong>'+E(c.name)+'</strong><span class="status">'+E(c.status==='igual'?'Sin cambio de ritmo':c.status==='acelera'?'Acelera':'Desacelera')+'</span></div><button type="button" class="micro-target" data-tip-kind="component" data-tip-id="'+E(c.id)+'" data-tip-group="'+g.id+'" aria-label="'+E('Consultar tasas y diferencia de '+c.name)+'">'+mini+'</button><div class="values">'+valueBlock('12m a/a · vacío',fmt(c.slow)+' %')+valueBlock('3m a/a · lleno',fmt(c.fast)+' %')+valueBlock('Diferencia',signed(c.gap)+' pp')+'</div></div>';
  }).join('')+(children.length?'':'<p>Sin componentes con ambos datos para este mes.</p>')+'</div></td></tr>';
  return line;
 }).join('');
 return '<div class="legend">'+legendItem('Aceleran','navy','box')+legendItem('Iguales','neutral','box')+legendItem('Desaceleran','copper','box')+'</div>'+search+tableInspection(r)+'<p class="summary-note">'+E(dateLabel(r.date))+' · abre un agregado para ver sus componentes. Pasa el ratón o enfoca una barra o un par de círculos para consultar su ayuda; clic o toque conserva el detalle. Los agregados se superponen: no se suman.</p>'+(rendered?'<table class="data-table amplitude-table"><caption class="sr-only">Amplitud de actividad por agregado</caption><thead><tr><th scope="col">Agregado</th><th scope="col">Aceleran / igual / desaceleran</th><th scope="col" class="num">% acelera</th></tr></thead><tbody>'+html+'</tbody></table>':'<div class="empty">No hay coincidencias. Borra la búsqueda o escribe parte del nombre.</div>');
}
function expandedDetails(key,rr,r,view){
 let html='';
 if(key==='contributions'&&r){
  const sum=r.values.every(x=>x!=null)?r.values.reduce((a,b)=>a+b,0):null;
  html+='<section class="details-block"><h3>Aportes del mes consultado</h3><table class="data-table details-table"><caption>'+E(dateLabel(r.date))+' · nueve grupos originales, en puntos porcentuales</caption><thead><tr><th scope="col">Grupo</th><th scope="col" class="num">Aporte (pp)</th></tr></thead><tbody>'+DATA.groups.map((g,i)=>'<tr><td>'+E(g.name)+'</td><td class="num" data-label="Aporte (pp)">'+signed(r.values[i])+'</td></tr>').join('')+'<tr><td>Suma de los nueve grupos</td><td class="num" data-label="Suma (pp)">'+fmt(sum,2)+'</td></tr><tr><td>IPCA total (variación en %)</td><td class="num" data-label="Total (%)">'+fmt(r.total,2)+'</td></tr><tr><td>Total menos suma de aportes</td><td class="num" data-label="Diferencia (pp)">'+signed(sum==null||r.total==null?null:r.total-sum)+'</td></tr></tbody></table></section>';
 }
 if(key!=='amplitude'&&rr.length){
  const at=Math.max(0,rr.findIndex(x=>x.date===r?.date));
  html+='<section class="details-block"><h3>Por periodos</h3><p>Mueve la consulta mes a mes. El gráfico, la lectura y el detalle usan la misma fecha.</p><div class="period-query"><label for="'+view+'-period">Mes consultado</label><input id="'+view+'-period" data-control="period" type="range" min="0" max="'+(rr.length-1)+'" value="'+at+'"><output for="'+view+'-period">'+E(dateLabel(rr[at].date))+'</output></div>';
  const from=Math.max(0,at-5),to=Math.min(rr.length,at+7),slice=rr.slice(from,to);
  const names=key==='contributions'?['IPCA (%)','Suma (pp)','Total − suma (pp)']:key==='fiscal'?['Observado (% PIB)','Estabilizador (% PIB)','Brecha (pp)']:['IPCA (%)','Núcleos (%)','Meta (%)'];
  html+='<table class="data-table details-table"><caption>Hasta doce observaciones cercanas al mes consultado; la ventana seleccionada limita el recorrido.</caption><thead><tr><th scope="col">Mes</th>'+names.map(n=>'<th scope="col" class="num">'+E(n)+'</th>').join('')+'</tr></thead><tbody>'+slice.map(x=>{
   let vs=x.values;
   if(key==='contributions'){const sum=x.values.every(v=>v!=null)?x.values.reduce((a,b)=>a+b,0):null;vs=[x.total,sum,sum==null||x.total==null?null:x.total-sum]}
   if(key==='fiscal')vs=[...vs,vs.some(v=>v==null)?null:vs[1]-vs[0]];
   return '<tr'+(x.date===r?.date?' style="background:var(--selected)"':'')+'><td>'+E(dateLabel(x.date))+(x.date===r?.date?' · consultado':'')+'</td>'+vs.map((v,i)=>'<td class="num" data-label="'+E(names[i])+'">'+fmt(v,2)+'</td>').join('')+'</tr>';
  }).join('')+'</tbody></table></section>';
 }
 html+='<section class="details-block"><h3>Cómo se lee y de dónde sale</h3><p>'+E(CASES[key].note)+'</p>';
 if(key==='amplitude')html+='<p class="formula">Diferencia (pp) = (m3a − m12) × 100 · % acelera = aceleran / pares válidos × 100</p><p>El círculo vacío representa 12m a/a y el lleno, 3m a/a. La línea une dos tasas del mismo componente. No es una tendencia temporal. Los componentes comparten la escala dentro de cada agregado.</p>';
 if(key==='inflation')html+='<p>El promedio de núcleos exige los cinco valores del mismo mes. La meta anual proviene de od_bcb y se sustituye por la media anual disponible en od_total cuando existe. No se extrapola hacia años sin información.</p>';
 if(key==='fiscal')html+='<p class="formula">Brecha (pp) = estabilizador (% PIB) − observado (% PIB)</p><p>Los cruces de las curvas dividen el relleno. Las cifras fiscales ya están expresadas en puntos de porcentaje: no se multiplican por 100.</p>';
 if(key==='contributions')html+='<p>Los aportes y el total del archivo se multiplican por 100. Cada aporte se expresa en pp; la línea conserva la variación total en %. Los apilados positivos y negativos se acumulan por separado.</p>';
 return html+'<p>Fuente: '+E(CASES[key].source)+'. Copia local extraída el 5 de noviembre de 2026; no constituye una consulta en vivo.</p></section>';
}
// MOTOR SVG: coordenadas propias del contenedor; ninguna biblioteca remota.
function niceDomain(values,zero){
 const v=values.filter(x=>x!=null&&Number.isFinite(x));
 if(!v.length)return {lo:0,hi:1,step:.2};
 let lo=Math.min(...v),hi=Math.max(...v);if(zero){lo=Math.min(0,lo);hi=Math.max(0,hi)}
 let span=hi-lo;if(!span)span=Math.max(1,Math.abs(lo)*.2);
 if(!zero||lo<0)lo-=span*.08;if(!zero||hi>0)hi+=span*.08;
 const raw=(hi-lo)/5,pow=10**Math.floor(Math.log10(raw)),n=raw/pow,step=(n<=1?1:n<=2?2:n<=2.5?2.5:n<=5?5:10)*pow;
 return {lo:Math.floor(lo/step)*step,hi:Math.ceil(hi/step)*step,step};
}
function linePath(rr,i,X,Y){let path='',pen=false;for(const r of rr){const v=r.values[i];if(v==null){pen=false;continue}path+=(pen?'L':'M')+X(r.date).toFixed(2)+','+Y(v).toFixed(2);pen=true}return path}
function renderChart(host){
 const key=host.dataset.chart,rr=currentRows(key),large=host.dataset.large==='true',w=Math.max(240,Math.round(host.getBoundingClientRect().width));
 if(!rr.length){host.innerHTML='<p class="empty">No hay datos para esta combinación. Cambia los filtros.</p>';return}
 const h=large?360:280,p={l:48,r:16,t:12,b:36},pw=w-p.l-p.r,ph=h-p.t-p.b,r=selected(key,rr),at=Math.max(0,rr.indexOf(r));
 let vals=rr.flatMap(r=>r.values);
 if(key==='contributions')vals=rr.flatMap(r=>[r.values.filter(v=>v!=null&&v>0).reduce((a,b)=>a+b,0),r.values.filter(v=>v!=null&&v<0).reduce((a,b)=>a+b,0),r.total]);
 const domain=niceDomain(vals,key!=='inflation'),Y=v=>p.t+(domain.hi-v)/(domain.hi-domain.lo)*ph;
 const t0=time(rr[0].date),t1=time(rr.at(-1).date),stepX=pw/rr.length;
 const X=f=>key==='contributions'?p.l+(rr.findIndex(x=>x.date===f)+.5)*stepX:p.l+(time(f)-t0)/(t1-t0||1)*pw;
 const tag=(t,attrs,body='')=>'<'+t+' '+attrs+'>'+body+'</'+t+'>';
 let svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" tabindex="0" data-control="chart" role="slider" aria-label="'+E(CASES[key].title)+'. Consulta mensual" aria-orientation="horizontal" aria-valuemin="0" aria-valuemax="'+(rr.length-1)+'" aria-valuenow="'+at+'" aria-valuetext="'+E(dateLabel(r.date))+'"><defs><clipPath id="clip-'+(large?'l':'s')+'-'+key+'"><rect x="'+p.l+'" y="'+p.t+'" width="'+pw+'" height="'+ph+'"/></clipPath></defs>';
 let shapes='';
 if(key==='inflation'){
  rr.forEach((d,i)=>{if(d.values[0]!=null&&d.values[1]!=null&&d.values[0]>d.values[1]){
   const a=i?(X(rr[i-1].date)+X(d.date))/2:X(d.date),b=i<rr.length-1?(X(rr[i+1].date)+X(d.date))/2:X(d.date);
   shapes+=tag('rect','x="'+a+'" y="'+p.t+'" width="'+Math.max(0,b-a)+'" height="'+ph+'" fill="'+color('band')+'"');
  }});
 }
 if(key==='fiscal'){
  for(let i=1;i<rr.length;i++){
   const a=rr[i-1],b=rr[i];if([...a.values,...b.values].some(v=>v==null))continue;
   const x0=X(a.date),x1=X(b.date),d0=a.values[1]-a.values[0],d1=b.values[1]-b.values[0];
   const polygon=(xA,xB,vA,vB,sign)=>tag('path','d="M'+xA+','+Y(vA[0])+' L'+xB+','+Y(vB[0])+' L'+xB+','+Y(vB[1])+' L'+xA+','+Y(vA[1])+' Z" fill="'+color(sign>=0?'sand':'history')+'" fill-opacity=".62"');
   if(d0*d1<0){const t=d0/(d0-d1),xc=x0+(x1-x0)*t,vc=a.values[0]+(b.values[0]-a.values[0])*t;shapes+=polygon(x0,xc,a.values,[vc,vc],d0)+polygon(xc,x1,[vc,vc],b.values,d1)}
   else shapes+=polygon(x0,x1,a.values,b.values,d0||d1);
  }
 }
 let axes='';
 for(let tick=domain.lo,n=0;tick<=domain.hi+domain.step*.001&&n<12;tick+=domain.step,n++){
  const y=Y(tick),isZero=Math.abs(tick)<domain.step*.001;
  axes+=tag('line','x1="'+p.l+'" x2="'+(w-p.r)+'" y1="'+y+'" y2="'+y+'" stroke="'+color(isZero?'reference':'grid')+'" stroke-width="'+(isZero?1.2:1)+'"')+tag('text','x="'+(p.l-8)+'" y="'+(y+4)+'" text-anchor="end"',E(fmt(Math.abs(tick)<1e-10?0:tick,domain.step<1?1:0)));
 }
 const tickN=w<480?3:5,indexes=[...new Set(Array.from({length:tickN},(_,i)=>Math.round(i*(rr.length-1)/(tickN-1))))];
 indexes.forEach((i,j)=>{const x=X(rr[i].date);axes+=tag('text','x="'+x+'" y="'+(h-8)+'" text-anchor="'+(j===0?'start':j===indexes.length-1?'end':'middle')+'"',E(dateLabel(rr[i].date)))});
 if(key==='contributions'){
  const barW=Math.max(2,stepX*.72);
  rr.forEach(row=>{
   let pos=0,neg=0;
   row.values.forEach((v,i)=>{
    if(v==null)return;
    const base=v>=0?pos:neg,end=base+v;if(v>=0)pos=end;else neg=end;
    shapes+=tag('rect','x="'+(X(row.date)-barW/2)+'" y="'+Math.min(Y(base),Y(end))+'" width="'+barW+'" height="'+Math.abs(Y(base)-Y(end))+'" fill="'+color(DATA.groups[i].color)+'"');
   });
  });
  const temp=rr.map(d=>({date:d.date,values:[d.total]}));
  shapes+=tag('path','d="'+linePath(temp,0,X,Y)+'" fill="none" stroke="'+color('fg')+'" stroke-width="2.5"');
 }else CASES[key].names.forEach((_,i)=>{shapes+=tag('path','d="'+linePath(rr,i,X,Y)+'" fill="none" stroke="'+color(CASES[key].colors[i])+'" stroke-width="'+(i===0?2.5:2)+'"'+((CASES[key].dashed??[CASES[key].names.length-1]).includes(i)?' stroke-dasharray="6 4"':'')+' stroke-linejoin="round"')});
 const sx=X(r.date);
 let cursor=tag('line','x1="'+sx+'" x2="'+sx+'" y1="'+p.t+'" y2="'+(h-p.b)+'" stroke="'+color('fg')+'" stroke-width="1" stroke-dasharray="2 4"');
 const sv=key==='contributions'?[r.total]:r.values;
 sv.forEach((v,i)=>{if(v!=null)cursor+=tag('circle','cx="'+sx+'" cy="'+Y(v)+'" r="4" fill="'+color(key==='contributions'?'fg':CASES[key].colors[i])+'" stroke="'+color('surface')+'" stroke-width="2"')});
 svg+=axes+'<g clip-path="url(#clip-'+(large?'l':'s')+'-'+key+')">'+shapes+cursor+'</g></svg>';
 const wasFocused=host.contains(document.activeElement),wasDescribed=tipOwner&&host.contains(tipOwner);
 if(wasDescribed)hideTip();
 host.innerHTML=svg;
 const chart=host.querySelector('svg');
 const nearest=event=>{
  const rect=chart.getBoundingClientRect(),x=(event.clientX-rect.left)*w/rect.width;
  return rr.reduce((best,row,j)=>Math.abs(X(row.date)-x)<Math.abs(X(rr[best].date)-x)?j:best,0);
 };
 const preview=(i,event)=>{
  const rect=chart.getBoundingClientRect(),px=X(rr[i].date);
  const marker=()=>{
   chart.querySelector('[data-hover-marker]')?.remove();
   const group=document.createElementNS('http://www.w3.org/2000/svg','g');group.dataset.hoverMarker='true';group.setAttribute('aria-hidden','true');group.setAttribute('pointer-events','none');
   group.innerHTML=tag('line','x1="'+px+'" x2="'+px+'" y1="'+p.t+'" y2="'+(h-p.b)+'" stroke="'+color('navy')+'" stroke-width="1.5" stroke-dasharray="4 4"');
   chart.append(group);
  };
  showTip(chart,tooltipContent(key,rr[i]),event?.clientX??rect.left+px,event?.clientY??rect.top+p.t+48,key+':'+rr[i].date,marker);
 };
 chart.addEventListener('pointermove',event=>{if(event.pointerType==='mouse'&&matchMedia('(hover: hover)').matches)preview(nearest(event),event)});
 chart.addEventListener('pointerleave',()=>leaveTip(chart));
 chart.addEventListener('focus',()=>{if(lastInput==='keyboard')preview(at)});
 chart.addEventListener('blur',()=>{if(dismissedOwner===chart)dismissedOwner=null;if(tipOwner===chart)hideTip()});
 chart.addEventListener('click',event=>{const i=nearest(event);hideTip();setDate(key,rr[i].date);refresh(key);announce(dateLabel(rr[i].date)+' fijado en la consulta')});
 chart.addEventListener('keydown',event=>{
  let i=at;
  if(event.key==='ArrowLeft'||event.key==='ArrowDown')i=Math.max(0,at-1);
  else if(event.key==='ArrowRight'||event.key==='ArrowUp')i=Math.min(rr.length-1,at+1);
  else if(event.key==='Home')i=0;
  else if(event.key==='End')i=rr.length-1;
  else if(event.key!=='Enter'&&event.key!==' ')return;
  event.preventDefault();dismissedOwner=null;hideTip();setDate(key,rr[i].date);refresh(key);announce(dateLabel(rr[i].date)+' fijado en la consulta');
 });
 if(wasFocused)chart.focus({preventScroll:true});
}
function setDate(key,date){if(key==='contributions')STATES[key].date=date;else STATES[key].at=(key==='amplitude'?DATA.amplitude:DATA[key]).findIndex(r=>r.date===date);STATES[key].pinned=true}
function announce(text){document.getElementById('announcement').textContent=text}
function drawAll(){document.querySelectorAll('[data-chart]').forEach(renderChart)}
function refresh(key,restore=true){
 const a=document.activeElement,view=a?.closest('[data-view]')?.dataset.view,control=a?.dataset.control,group=a?.dataset.group,tipId=a?.dataset.tipId,tipKind=a?.dataset.tipKind,tipGroup=a?.dataset.tipGroup;
 hideTip();
 document.getElementById('card-'+key).innerHTML=caseView(key);
 if(activeCase===key&&dialog.open)document.getElementById('dialog-content').innerHTML=caseView(key,true);
 observeCharts();
 document.querySelectorAll('[data-case="'+key+'"] [data-chart]').forEach(renderChart);
 if(restore&&view&&(control||group||tipId)){
  const selector='[data-view="'+view+'"] '+(control?'[data-control="'+control+'"]':group?'[data-group="'+group+'"]':'[data-tip-kind="'+tipKind+'"][data-tip-id="'+tipId+'"]'+(tipGroup?'[data-tip-group="'+tipGroup+'"]':''));
  document.querySelector(selector)?.focus({preventScroll:true});
 }
}
function observeCharts(){if(observer)observer.disconnect();observer=new ResizeObserver(entries=>entries.forEach(e=>{if(e.contentRect.width>0)renderChart(e.target)}));document.querySelectorAll('[data-chart]').forEach(el=>observer.observe(el))}
function openDetail(key,button){
 hideTip();
 opener=button;activeCase=key;document.getElementById('dialog-title').textContent=CASES[key].title;
 document.getElementById('dialog-content').innerHTML=caseView(key,true);
 dialog.showModal();document.body.style.overflow='hidden';document.getElementById('dialog-content').scrollTop=0;
 drawAll();observeCharts();document.getElementById('close-dialog').focus();
}
document.addEventListener('click',e=>{
 const release=e.target.closest('[data-release]');
 if(release){
  const key=release.dataset.release,view=release.closest('[data-view]').dataset.view;
  if(key==='amplitude')STATES.amplitude.inspection=null;else setDate(key,currentRows(key).at(-1).date);
  STATES[key].pinned=false;hideTip();refresh(key);
  document.querySelector('[data-view="'+view+'"] [data-control="date"]')?.focus({preventScroll:true});announce(key==='amplitude'?'Consulta de tabla limpiada':'Último mes disponible seleccionado');return;
 }
 const micro=e.target.closest('[data-tip-kind]');if(micro){pinTable(micro);return}
 const enlarge=e.target.closest('[data-enlarge]');if(enlarge){openDetail(enlarge.dataset.enlarge,enlarge);return}
 const group=e.target.closest('[data-group]');if(group){const s=STATES.amplitude.open,id=group.dataset.group;s.has(id)?s.delete(id):s.add(id);refresh('amplitude');announce(s.has(id)?'Componentes abiertos':'Componentes cerrados')}
});
document.addEventListener('change',e=>{
 const el=e.target,key=el.closest('[data-case]')?.dataset.case,c=el.dataset.control;if(!key||!c)return;
 if(c==='date')setDate(key,el.value);
 else if(c==='period')setDate(key,currentRows(key)[Number(el.value)].date);
 else if(c==='search')STATES[key].query=el.value;
 else STATES[key][c]=el.value;
 if(key==='contributions'){const rr=currentRows(key);if(!rr.some(r=>r.date===STATES[key].date))STATES[key].date=rr.at(-1)?.date||null}
 if((c==='window')&&key!=='contributions'){const r=selected(key);if(r)setDate(key,r.date)}
 refresh(key);announce('Selección actualizada');
});
document.addEventListener('input',e=>{
 if(e.target.dataset.control!=='search')return;
 const pos=e.target.selectionStart;STATES.amplitude.query=e.target.value;refresh('amplitude');
 const field=document.activeElement;if(field?.type==='search')field.setSelectionRange(pos,pos);
});
document.addEventListener('pointerover',e=>{
 const target=e.target.closest('[data-tip-kind]');if(!target||e.pointerType!=='mouse'||!matchMedia('(hover: hover)').matches)return;
 if(target.contains(e.relatedTarget))return;
 tablePreview(target,e);
});
document.addEventListener('pointermove',e=>{const target=e.target.closest('[data-tip-kind]');if(target&&e.pointerType==='mouse'&&tipOwner===target&&!tip.hidden)positionTip(e.clientX,e.clientY)});
document.addEventListener('pointerout',e=>{const target=e.target.closest('[data-tip-kind]');if(target&&!target.contains(e.relatedTarget))leaveTip(target)});
document.addEventListener('pointerdown',e=>{lastInput=e.pointerType||'mouse'},true);
document.addEventListener('focusin',e=>{const target=e.target.closest('[data-tip-kind]');if(target&&lastInput==='keyboard')tablePreview(target)});
document.addEventListener('focusout',e=>{const target=e.target.closest('[data-tip-kind]');if(target){if(dismissedOwner===target)dismissedOwner=null;if(tipOwner===target)hideTip()}});
document.addEventListener('keydown',e=>{
 lastInput='keyboard';
 if(e.key==='Escape'&&tipOwner){e.preventDefault();e.stopImmediatePropagation();hideTip(true)}
},true);
document.addEventListener('scroll',e=>{if(!tip?.contains(e.target))hideTip()},true);
window.addEventListener('resize',()=>hideTip());
document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',e=>{if(e.target===dialog){const b=dialog.getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)dialog.close()}});
dialog.addEventListener('close',()=>{hideTip();const key=activeCase;activeCase=null;document.body.style.overflow='';refresh(key,false);const focus=document.querySelector('[data-enlarge="'+key+'"]');focus?.focus();opener=null;observeCharts()});
// EXTRA_ADAPTERS
Object.keys(CASES).forEach(key=>{document.getElementById('card-'+key).innerHTML=caseView(key)});
observeCharts();drawAll();
"""

def html():
    data = build_data()
    fonts = (ROOT / "assets/fonts.css").read_text(encoding="utf-8-sig")
    layout = (ROOT / ".od-frames/layout.css").read_text(encoding="utf-8-sig")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    extra = (ROOT / "assets/graficos_frecuentes_extra.js").read_text(encoding="utf-8-sig")
    script = JS.replace("// EXTRA_ADAPTERS", extra)
    doc = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>Monitor Brasil · Gráficos frecuentes</title>'
           '<meta name="description" content="Ocho casos reales con vistas compactas y ampliadas: líneas, tablas, columnas y cascadas.">'
           '<style>\n' + layout + "\n" + fonts + "\n" + CSS + '</style></head><body>' + BODY +
           '<script type="application/json" id="chart-data">' + payload + '</script><script>' + script +
           '</script></body></html>\n')
    (ROOT / "maqueta-graficos-frecuentes.html").write_text(doc, encoding="utf-8")
    print("Escrito: maqueta-graficos-frecuentes.html")

def guide():
    (ROOT / "GUIA_GRAFICOS_FRECUENTES_LLM.md").write_text(GUIDE, encoding="utf-8")
    print("Escrito: GUIA_GRAFICOS_FRECUENTES_LLM.md")

GUIDE = r"""# Gráficos frecuentes: guía de inspección, diseño y réplica con LLMs

**Entrega:** maqueta-graficos-frecuentes.html  
**Fecha de extracción:** 5 de noviembre de 2026  
**Alcance:** ocho casos reales de cuatro familias. No es una migración de las 97 tarjetas de esas familias.

## 1. Qué contiene y cómo usarlo

Abre **maqueta-graficos-frecuentes.html** directamente en un navegador moderno. No necesita servidor, conexión, instalación ni CDN. El documento contiene fuentes WOFF2, estilos, datos y lógica. El enlace superior abre IMPLEMENTACION_GRAFICOS.md, la guía breve. Este documento conserva las especificaciones y los prompts completos.

La página presenta ocho tarjetas. Pasa el ratón para explorar tooltips por familia; haz clic o toca para conservar la consulta en el panel de valores. Selecciona los filtros disponibles y pulsa **Agrandar**: el detalle conserva el estado del caso. Al cerrar con el botón, Escape o un clic fuera del diálogo, vuelves a la misma tarjeta. Si hay una ayuda abierta, el primer Escape la cierra y el segundo cierra el diálogo. La amplitud abre componentes, el gasto abre subpartidas y la cascada conserva sus cinco ventanas reales.

Las vistas ampliadas no repiten el bloque de ciclo laboral de los relojes: ese bloque pertenecía a aquel caso. Cada familia recibe el detalle que necesita.

### Archivos y responsabilidades

| Archivo | Función |
|---|---|
| maqueta-graficos-frecuentes.html | Entrega principal, editable y autónoma |
| IMPLEMENTACION_GRAFICOS.md | Guía breve para integrar y replicar los ocho ejemplos |
| GUIA_GRAFICOS_FRECUENTES_LLM.md | Diagnóstico, contratos, decisiones y prompts |
| assets/generar_graficos_frecuentes.py | Fuente de construcción y extracción reproducible; requiere Python 3.8 o posterior |
| assets/graficos_frecuentes_extra.js | Adaptadores de interfaz de actividad, brecha de desocupación, gasto y cascada; se incrusta al generar |
| assets/fonts.css | Fuente local reutilizada por el generador; las fuentes quedan incrustadas en el HTML |
| .od-frames/layout.css | Primitivas estructurales existentes que el generador incorpora |

El generador no es necesario para abrir o editar el HTML. Para regenerar desde los JSON del monitor, ejecuta desde el proyecto:

~~~powershell
python assets/generar_graficos_frecuentes.py --html
python assets/generar_graficos_frecuentes.py --guide
~~~

La constante SOURCE del generador apunta al sitio original de este equipo. En otro equipo cambia SOURCE al directorio que contiene assets/js y data. Deben existir los diez JSON enumerados más abajo, assets/fonts.css, assets/graficos_frecuentes_extra.js y .od-frames/layout.css. No sobrescribas una adaptación manual del HTML sin guardar sus cambios en la fuente del generador. El JavaScript adicional queda incrustado: no es una petición externa al abrir el HTML.

## 2. Por qué estos casos

El inventario de INFORME_GRAFICOS.md clasifica **155 tarjetas** por su tarea visual dominante. Las líneas reúnen 53, las tablas analíticas 20 y las columnas 16: las tres familias de la primera entrega suman **89 tarjetas**. Se añade F04, con 8 cascadas: las cuatro familias suman **97 tarjetas**, aproximadamente el 63 % del inventario.

Los recuentos son de tarjetas, no de algoritmos independientes. Tampoco significan que los ocho casos aquí construidos cubran todas las variantes. Se propone reutilizar estructura y controles; las fórmulas y la semántica permanecen en adaptadores separados.

| Familia | Caso | Identificador original | Variante que aporta |
|---|---|---|---|
| F01 · líneas | IPCA y núcleos desde 2008 | AM2-03-1 | Varias series, meta anual y bandas de episodios |
| F01 · líneas | Primario observado contra el que estabiliza la deuda | AM4-02-0 | Dos curvas, negativos, cruces y relleno de brecha |
| F03 · tablas | Cuántos componentes aceleran en cada agregado | AM1-03-0 | Amplitud, denominadores y filas con componentes desplegables |
| F02 · columnas | Aportes al IPCA por grupo | AM2-01-0 | Nueve grupos, apilado de positivos/negativos y línea total |
| F01 · líneas | Índices de actividad, a/a | AM1-01-4 | Cuatro series observadas y cambio entre dos cestas |
| F02 · columnas | Brecha de desocupación | AM3-02-3 | Barras con signo frente a una referencia histórica fija |
| F03 · tablas | Gasto, partida por partida | AM4-07-3 | Jerarquía de 19 filas, peso, cambios y cinco horizontes de comparación |
| F04 · cascadas | De la deuda inicial a la de hoy | AM4-04-0 | Cinco ventanas, pasos acumulados, residuo y conciliación |

### Evidencia examinada y sus límites

- Se consultó el inventario del proyecto, los adaptadores JavaScript originales y las tablas JSON locales.
- Se observaron las referencias AM2_03_1.png, AM4_02_0.png, AM1_03_0.png y AM2_01_0.png de monitor/web/ref.
- Esas imágenes son referencias de diseño. No prueban el estado actual de ejecución: incluyen valores de plantilla y dos estructuras que ya cambiaron.
- La referencia de amplitud muestra seis filas; el código actual define cinco agregados, incluido IBC-Br.
- La referencia de aportes agrupa en tres conjuntos; el código actual exige los nueve grupos. La maqueta conserva nueve.
- La maqueta utiliza una extracción estática de datos locales, no una descarga oficial nueva ni una verificación estadística independiente.
- En la ampliación se leyeron los adaptadores de los cuatro casos nuevos y sus JSON. No se atribuye una inspección visual de nuevas capturas a estos casos.
- No se realizó una renderización, recorrido de navegador ni prueba posterior a la escritura de esta entrega.

## 3. Diagnóstico y propuesta por caso

### 3.1 IPCA y núcleos desde 2008

**Pregunta:** ¿cómo evoluciona la inflación general frente al promedio de núcleos y la meta?

**Problema observado en la referencia:** las bandas tienen gran presencia, faltan valores legibles en el eje vertical y la meta puede confundirse con otra serie observada. Los datos de la captura son de referencia, no valores que deban copiarse.

**Propuesta compacta:** IPCA azul, núcleos petróleo y meta gris discontinua. Bandas tenues sólo para meses en que IPCA supera núcleos. Eje con unidades, calendario visible, selector de mes y lectura numérica de las tres series. Por defecto se conserva la historia completa; ventanas de cinco y diez años permiten acercarse.

**Agrandar:** mismo filtro y mismo mes; gráfico más amplio; lectura numérica; bloque Por periodos con un recorrido mensual y hasta doce observaciones cercanas; definición de las bandas, del promedio y de la meta.

**Lo que no debe cambiar:** la banda no significa recesión, alarma ni incertidumbre. La meta no se extrapola a años sin dato. Los cinco núcleos deben existir en el mismo mes para calcular la media.

### 3.2 Primario observado frente al estabilizador

**Pregunta:** ¿cuánto resultado primario falta para alcanzar el que estabilizaría la deuda según el cálculo del monitor?

**Problema observado en la referencia:** el relleno concentra mucha atención y las anotaciones narrativas quedan desligadas del periodo que se consulta. Sin valores de eje o signos explícitos, es fácil confundir el nivel de primario con la distancia entre ambas curvas.

**Propuesta compacta:** observado azul continuo; estabilizador gris discontinuo; cero visible; relleno arena para falta de primario y azul grisáceo para primario por encima del estabilizador. La lectura separa observado, estabilizador y magnitud de la brecha.

**Agrandar:** comparación con más espacio, tabla mensual y fórmula explícita. Las anotaciones históricas fijas del diseño original se sustituyen en esta propuesta por la consulta del mes y una definición de la brecha. No se generan conclusiones causales nuevas.

**Lo que no debe cambiar:** datos en % del PIB ya escalados; brecha en pp; los rellenos se dividen exactamente en los cruces de las dos líneas. El área no mide probabilidad.

### 3.3 Componentes que aceleran por agregado

**Pregunta:** ¿qué proporción de componentes muestra un ritmo de tres meses mayor que el de doce meses y cuáles son?

**Problema de la referencia y del patrón original:** la tira apilada describe bien la composición, pero el denominador y el detalle quedan demasiado dependientes de ayudas emergentes o del clic en una fila. La estructura de la captura además está desactualizada.

**Propuesta compacta:** cinco agregados reales; tira con tres estados; conteo visible en el orden aceleran / iguales / desaceleran; n de pares válidos y porcentaje que acelera. Cada agregado tiene un botón nativo con flecha y estado desplegado.

**Detalle de componentes:** nombre completo, clasificación textual, círculo vacío en 12m a/a, círculo lleno en 3m a/a, valores numéricos y diferencia. El par de círculos compara dos métricas del mismo mes; no es una serie temporal. La escala es común dentro de cada agregado, no necesariamente entre agregados.

**Agrandar:** misma fecha, orden, búsqueda y agregados abiertos; mayor ancho y explicación completa. El buscador encuentra tanto agregados como componentes. Con una búsqueda activa se muestran los grupos y componentes coincidentes para evitar ocultar el resultado dentro de una fila cerrada.

**Lo que no debe cambiar:** no sumar filas agregadas: Todas las series incluye PMC/PMS/PIM y se superpone con esas tres filas. IBC-Br es otro universo. El denominador excluye componentes sin ambas tasas del mes.

### 3.4 Aportes al IPCA por grupo

**Pregunta:** ¿qué aporta cada grupo a la variación del IPCA elegida?

**Problema observado:** una leyenda simplificada de tres grupos no corresponde al código actual. Nueve colores sin detalle numérico pueden ser difíciles de distinguir, especialmente con barras estrechas o aportes negativos.

**Propuesta compacta:** nueve grupos persistentes, leyenda multilínea, cero claro, positivos arriba y negativos abajo; línea total oscura. Variación, ajuste, ventana y mes son controles funcionales. El eje cubre simultáneamente el total de los positivos, el total de los negativos y la línea del IPCA.

**Agrandar:** conserva los filtros, presenta los nueve aportes del mes, la suma, el total y su diferencia; añade consulta Por periodos y definiciones de unidades.

**Lo que no debe cambiar:** no agrupar categorías arbitrariamente, no normalizar a 100 %, no borrar negativos ni corregir un residuo repartiéndolo entre grupos. Los colores ayudan a localizar, pero el desglose numérico permite leer sin distinguir nueve tonos.

## 4. Especificación visual compartida

Se continúa el lenguaje claro de la maqueta de relojes y del monitor existente. Esta elección conserva la referencia concreta del proyecto; no aplica el fondo oscuro de la descripción genérica del paquete Dashboard.

| Elemento | Regla |
|---|---|
| Fondo | #F6F7F8 |
| Superficie | #FFFFFF |
| Texto | #24324A; secundarios #5B6573 y #606C7A |
| Serie principal | #2E5C8A |
| Segunda serie | #2F7A86 |
| Referencia | #8A8F96, trazo discontinuo |
| Diferencia negativa de ritmo | #A85E24 más etiqueta textual |
| Rellenos fiscales | Arena #EDC9A6 / historia #A9B8CB, con leyenda |
| Titulares | Bricolage Grotesque local |
| Cuerpo y datos | IBM Plex Sans local; números tabulares |
| Texto de interfaz | Base 16 px; auxiliares 14 px; etiquetas numéricas del SVG 13 px |
| Espaciado | Múltiplos de 4/8; sección 48, tarjeta 24, grupos 16/8 px |
| Bordes | 1 px, sin sombra decorativa; radio de tarjeta 12 px |
| Controles | Altura mínima 44 px y foco visible |
| Movimiento | 200 ms para la flecha de despliegue; sin animar datos; reduced-motion desactiva transiciones |

Las etiquetas densas de ejes, tablas y leyendas usan tamaños menores que el texto de cuerpo para conservar la composición de un monitor analítico. Los valores consultados aparecen además en texto HTML. Los tonos claros se reservan a marcas o rellenos; no se usan como texto principal.

### Distribución y adaptación

- A partir de 1024 px: dos casos de líneas en columnas; debajo, tabla y aportes en columnas.
- Por debajo de 1024 px: una columna, sin ocultar acciones.
- Por debajo de 768 px: menos relleno, leyenda de aportes en dos columnas y tabla de periodos convertida en filas de datos apilados.
- El SVG usa el ancho real de su contenedor y no escala una página de escritorio completa.
- El diálogo ocupa casi todo el ancho móvil; cabecera y cuerpo tienen espacio propio, y el cuerpo desplaza su contenido.
- Textos de datos largos envuelven completos; no se truncaron nombres de componentes.

## 5. Contratos de datos y fórmulas

### 5.1 Entrada común del sitio original

Los JSON tienen esta forma, no una lista directa de objetos:

~~~json
{
  "tabla": "nombre",
  "columnas": ["fecha", "categoria_id", "aa"],
  "filas": [["2026-09-30", "t433", 0.045761]]
}
~~~

Conversión: cada fila se convierte en un objeto usando columnas como claves. Los valores null permanecen null. Nunca se sustituyen automáticamente por cero.

La maqueta alinea series mensuales mediante AAAA-MM. Ésta es una decisión de granularidad: el IPCA viene fechado al cierre del mes y los fiscales al inicio. No se unen por posición de fila ni se mezclan ambas familias en un supuesto día común.

### 5.2 Inflación y núcleos

**Tablas:** infj_serie.json, od_bcb.json, od_total.json.

1. IPCA: categoria_id = t433, columna aa.
2. Núcleos: n11427, n27839, n4466, n16122, n28750; columna aa.
3. Para cada mes, promedio aritmético de los cinco aa sólo si los cinco son válidos.
4. IPCA y núcleos pasan de fracción a porcentaje multiplicando por 100.
5. Meta base: meta por anio de od_bcb con datos disponibles.
6. Si od_total contiene metas válidas en un año, su media anual sustituye a od_bcb para ese año, igual que en el adaptador original.
7. Meta × 100; años sin información permanecen null.
8. Banda activa sólo con ambos valores válidos e IPCA > núcleos.
9. Calendario mensual completo desde enero de 2008 hasta el último mes del IPCA. Los meses sin valor interrumpen la línea.

El promedio anual de metas replica el código actual: si un escenario futuro exige cambios de meta dentro del año, adapta explícitamente el contrato; no reutilices esta transformación sin revisarla.

### 5.3 Primario fiscal

**Tabla:** fiscal_mensual.json.

- Observado: primario_observado_pib.
- Referencia: primario_estabilizador_pib.
- Unidad de ambas columnas: puntos de porcentaje del PIB, ya escalados.
- Fórmula: brecha = estabilizador − observado.
- Brecha positiva: falta primario. Brecha negativa: observado por encima del estabilizador.
- Se conserva el signo en la tabla Por periodos; el resumen expresa magnitud absoluta con una etiqueta que explica el signo.
- Desde enero de 2010 al último mes de la tabla; calendario completo y discontinuidades ante null.

**Cruce entre dos meses:** si d0 y d1 son las brechas de extremos y d0 × d1 < 0:

~~~text
t = d0 / (d0 − d1)
x_cruce = x0 + t × (x1 − x0)
y_cruce = observado0 + t × (observado1 − observado0)
~~~

Dibuja dos polígonos, uno a cada lado del cruce. No pintes todo el intervalo con el color del primer mes. Si falta cualquiera de los cuatro valores, no dibujes ese tramo de relleno. La interpolación es geométrica entre observaciones mensuales; no añade un dato observado.

### 5.4 Amplitud

**Tablas:** actv_serie.json y actv_miembro.json.

Universos, en orden del código:

| Agregado | Familias de miembros |
|---|---|
| IBC-Br (sectores) | IBC-Br |
| Todas las series (PMC, PMS, PIM) | Comercio, Servicios, Industria |
| PMC (actividades) | Comercio |
| PMS (actividades) | Servicios |
| PIM (secciones) | Industria |

Filtra miembros con unidad = Volumen y rol = Hijo. Deduplica categoria_id dentro de cada agregado. Para el mes consultado, conserva sólo componentes con m3a y m12 no nulos.

~~~text
d = m3a − m12                 # fracción
si abs(d) <= 0.001: igual     # incluye exactamente el límite de 0,1 pp
si d > 0.001: acelera
si d < -0.001: desacelera

n = aceleran + iguales + desaceleran
porcentaje_acelera = 100 × aceleran / n, si n > 0
diferencia_pp = 100 × d
~~~

No confundas m12 con a12. En este caso se compara m3a con m12. Es una distinción importante del código auditado del 5 de noviembre.

Cada fecha conserva grupos con children, counts y n. Los componentes se ordenan por diferencia descendente. El filtro de búsqueda no recalcula los porcentajes del agregado: filtra la presentación de componentes, manteniendo su universo original.

La maqueta incorpora los últimos 24 meses de actv_serie para explorar fechas, sin ejecutar una consulta remota. No arrastra el dato de un componente rezagado hasta el corte global.

### 5.5 Contribuciones

**Tabla:** grafico_inflacion_v2.json.

| Control | Valores del JSON |
|---|---|
| Mes a mes | periodo = m/m |
| Trimestre a trimestre | periodo = 3m |
| Año a año | periodo = a/a |
| Ajuste | Sin ajuste / Desestacionalizado |

Las seis combinaciones existen en la extracción utilizada. Se incorporan hasta 36 meses de cada combinación. La ventana elige los últimos 12, 24 o 36 registros mensuales disponibles.

| Grupo | serie_id |
|---|---|
| Alimentación y bebidas | ipca\|k7170 |
| Vivienda | ipca\|k7445 |
| Transportes | ipca\|k7625 |
| Salud y cuidados personales | ipca\|k7660 |
| Gastos personales | ipca\|k7712 |
| Educación | ipca\|k7766 |
| Artículos de residencia | ipca\|k7486 |
| Vestuario | ipca\|k7558 |
| Comunicación | ipca\|k7786 |

Para cada mes y grupo, suma aporte × 100 de sus filas válidas. Si falta el grupo o alguno de sus aportes es null, conserva null. Esto hace explícita la falta de información en vez de convertirla en cero, a diferencia del reduce original.

El total toma total_ipca de la primera fila del mes, como el adaptador del monitor, y lo multiplica por 100. El contrato de origen presupone el mismo total repetido para todas las filas del mes. Si se conecta otra fuente, hay que rechazar o resolver totales inconsistentes; esta maqueta no introduce una conciliación nueva.

~~~text
positivo_mes = suma(max(aporte_grupo, 0))
negativo_mes = suma(min(aporte_grupo, 0))
residuo = total_ipca_pct − suma(aportes_pp), sólo con los nueve aportes válidos
dominio_y cubre positivo_mes, negativo_mes, total_ipca_pct y cero
~~~

El residuo se muestra como diferencia, no se etiqueta automáticamente como error ni como décimo grupo. Puede reflejar redondeo o metodología; la maqueta no infiere la causa.

## 6. Arquitectura de la réplica

El HTML tiene tres bloques editables:

1. style: primitivas de layout, fuentes incrustadas y tokens/componentes.
2. script#chart-data: JSON serializado de los ocho adaptadores.
3. script de aplicación: CASES, STATES, vistas, motor SVG, eventos y adaptadores adicionales incrustados.

### Interfaces internas

~~~javascript
// Una observación mensual de líneas; null rompe el trazo.
{ date: "2026-09", values: [4.58, 4.2, 3.0] }

// Una observación de aportes; el orden sigue DATA.groups.
{ date: "2026-09", values: [/* nueve valores o null */], total: 4.58 }

// Una observación de amplitud.
{
  date: "2026-08",
  groups: [{
    id: "pmc",
    name: "PMC (actividades)",
    n: 0,
    counts: { acelera: 0, igual: 0, desacelera: 0 },
    children: [{
      id: "identificador",
      name: "Nombre del componente",
      slow: null, fast: null, gap: null, status: "igual"
    }]
  }]
}
~~~

Estos fragmentos describen la forma, no son registros del archivo real. En la amplitud generada, los hijos sin ambas tasas se excluyen y no quedan como hijos con null.

### Funciones y límites de responsabilidad

| Función / bloque | Responsabilidad |
|---|---|
| build_data en Python | Extraer, alinear y convertir unidades desde los JSON |
| CASES | Títulos, unidades, nombres, colores y notas por caso |
| STATES | Ventana, fecha, búsqueda, orden y grupos abiertos |
| currentRows / selected | Resolver la ventana y el registro consultado |
| caseView | Componer el mismo caso en compacto o ampliado |
| makeControls | Etiquetas y selectores persistentes |
| reading | Dar valores HTML sin depender de leer el SVG |
| amplitudeTable | Mostrar universos, composición y componentes |
| expandedDetails | Desglose del mes, Por periodos y metodología |
| niceDomain | Calcular escala que incluya los valores necesarios |
| linePath | Cortar el trazo ante un null |
| renderChart | Dibujar geometría, ejes, cursor persistente y exploración temporal |
| tooltipContent / tipRow | Contenido semántico por familia; null y unidades explícitas |
| showTip / hideTip / positionTip | Apertura, cierre, ubicación y relación accesible de una ayuda compartida |
| tablePreview / pinTable / tableInspection | Explorar y conservar el detalle de un micrográfico |
| setDate / refresh | Sincronizar todas las representaciones del caso |
| openDetail | Abrir el diálogo sin crear un estado paralelo |

Las vistas compacta y ampliada leen el mismo estado. No dupliques sus cálculos ni mantengas dos fechas independientes. Cuando un filtro deja fuera el mes consultado, se selecciona el último mes de la nueva ventana. La tabla conserva sus grupos abiertos al cambiar de mes.

### Límites deliberados del prototipo

- No conecta en vivo con el monitor ni reemplaza sus renderizadores ECharts.
- No incluye todos los tipos de líneas, tablas o columnas del catálogo.
- No añade un editor de datos, panel de diseño, descarga CSV ni nuevas métricas.
- Los tooltips flotantes son una vista previa con ratón o foco de teclado. En táctil, clic/toque fija la misma información en un panel persistente; el selector de mes y el recorrido mensual siguen disponibles.
- La tabla temporal muestra hasta doce observaciones cercanas al mes consultado; el selector y el recorrido permiten visitar el resto de la ventana.
- El buscador es una ayuda de presentación; los porcentajes mantienen el denominador del agregado.
- Las líneas fiscales son interpolaciones geométricas entre meses, no mediciones diarias.

## 7. Estados, interacción y accesibilidad

| Acción / situación | Comportamiento definido |
|---|---|
| Abrir la página | Ocho casos; último mes en series, corte único de gasto y ventana de tres años en cascada |
| Cambiar ventana | Recalcular vista; conservar mes si sigue dentro, si no elegir último |
| Cambiar variación o ajuste | Usar la combinación local correspondiente; mismo mes si existe |
| Consultar mes | Actualizar cursor, lectura, desglose y tabla temporal |
| Pasar el ratón por un gráfico | Vista previa del mes más cercano; no cambia la consulta persistente |
| Hacer clic o tocar gráfico | Seleccionar el mes más cercano en X y fijar su lectura |
| Ver último mes | Liberar la consulta fijada y volver al corte de la ventana |
| Enfocar gráfico con teclado | Mostrar ayuda del mes seleccionado; flechas recorren, Inicio/Fin van a extremos y Enter fija |
| Escape con ayuda abierta | Cerrar sólo la ayuda; sin ayuda abierta se conserva el cierre normal del diálogo |
| Pasar el ratón o enfocar un micrográfico | Mostrar conteos del agregado o tasas/diferencia del componente |
| Pulsar micrográfico | Conservar su detalle encima de la tabla; Limpiar consulta lo retira |
| Agrandar | Abrir diálogo nativo; mismo caso, estado y datos |
| Cerrar | Botón, Escape o clic exterior; devolver foco al botón Agrandar |
| Navegar por teclado | Selectores, botones, búsqueda y recorrido nativos con foco visible |
| Abrir agregado | Botón con aria-expanded y aria-controls; hijos completos |
| Buscar | Mostrar grupos coincidentes y componentes encontrados; mensaje si no hay resultados |
| Sin ambas tasas | Excluir del denominador de amplitud |
| Sin dato de línea | Mostrar discontinuidad y Sin dato en la consulta |
| Sin combinación de aportes | Mensaje de ausencia y controles para recuperarse |
| Cambiar tamaño | ResizeObserver redibuja sólo la geometría con el ancho del contenedor |
| Movimiento reducido | Sin transiciones ni desplazamiento suave |

El SVG ofrece un nombre accesible; los valores relevantes se leen además en HTML y tablas. El diálogo nativo aporta modalidad y navegación de foco en navegadores modernos. El texto de estado comunica cambios de selección sin depender de color.

### 7.1 Tooltips: vista previa y consulta persistente

**Dos estados distintos:** recorrer un gráfico es explorar; hacer clic, tocar, cambiar el selector o usar flechas es elegir una fecha. La vista previa nunca llama a setDate ni cambia filtros. La consulta elegida se conserva aunque el puntero visite otros meses.

Al fijar una fecha de línea o columnas, el panel inferior muestra Consulta fijada y un botón Ver último mes. Ese botón vuelve al último registro de la ventana actual y retira la marca de fijación. En la tabla, cada micrográfico puede conservar un detalle en un panel encima de las filas; Limpiar consulta retira ese panel sin cambiar el mes ni los agregados abiertos.

| Caso | Jerarquía del tooltip |
|---|---|
| IPCA y núcleos | Mes, IPCA destacado, promedio de núcleos y meta; todos con % a/a |
| Primario fiscal | Mes, brecha con signo en pp, observado y estabilizador en % PIB, significado del signo |
| Aportes | Mes, variación y ajuste; total en % separado de los nueve aportes en pp, en orden estable |
| Amplitud por agregado | Nombre y mes; porcentaje que acelera y conteos de los tres estados con denominador |
| Componente de amplitud | Nombre y mes; diferencia en pp y ambas tasas en %, con explicación del umbral |

**Datos ausentes:** se escribe Sin dato en la fila correspondiente. No se suprime una serie nula del tooltip, no se transforma a cero y no se añade una unidad a un valor inexistente.

**Formato:** el título y los valores usan al menos 16 px; el dato principal, 20 px; rótulos y ayudas, 14 px. Etiquetas largas envuelven dentro de una columna flexible y números con unidades quedan juntos. En aportes se mantienen los nueve grupos: no se acorta la lista en silencio ni se cambia de orden al recorrer meses.

**Ubicación:** la ayuda se coloca junto al puntero o al elemento enfocado, cambia de lado cuando se acerca al borde y se mantiene dentro del viewport con margen. La anchura máxima es de 360 px; en ventanas bajas la ayuda puede desplazarse verticalmente. Cuando el navegador ofrece Popover API, una capa manual permite mostrarla sobre el diálogo sin quedar detrás. La alternativa mantiene el nodo dentro del diálogo abierto o del body.

**Interacción:** apertura inicial tras 120 ms, actualización inmediata mientras la ayuda ya está visible, cierre al salir con un margen de 160 ms para poder entrar al propio tooltip. El puntero puede situarse sobre la ayuda y seleccionar o desplazar su contenido. La ayuda no contiene botones ni enlaces; la acción persistente se hace en el gráfico o micrográfico.

**Teclado:** cada gráfico mensual se expone como un control deslizante horizontal con mínimo, máximo, posición y mes accesible. Las flechas fijan el mes siguiente/anterior, Inicio/Fin seleccionan extremos y Enter o espacio conservan el mes actual. Los micrográficos son botones nativos, accesibles por Tab, Enter y espacio. El selector mensual sigue siendo una alternativa equivalente.

**Escape:** cierra la ayuda y evita que el mismo evento cierre también Agrandar. No borra la consulta persistente. La ayuda no reaparece bajo el mismo puntero hasta salir y volver a entrar; la siguiente interacción de teclado permite abrir otra consulta.

**Táctil:** no se simula hover. Un toque sobre el gráfico fija el mes y un toque sobre una barra de composición o un par de círculos conserva su detalle. La restauración de foco tras el toque no abre una burbuja accidental encima del contenido.

**Limpieza:** al cambiar filtros, redimensionar, desplazar el documento, abrir o cerrar Agrandar o sustituir un gráfico, se retira la vista previa y su relación aria-describedby. El desplazamiento dentro del propio tooltip no lo cierra. Los datos fijados pertenecen a STATES y sobreviven al cambio compacto/ampliado.

**Separación técnica:** tooltipContent sólo formatea; showTip sólo presenta; setDate y pinTable fijan el estado. Los nombres se escapan con E antes de insertarlos en HTML. No se ejecuta HTML procedente de una fuente de datos.

Los datos se cargan de forma síncrona desde el propio HTML: no se simula una espera de red ni se introduce un spinner. Si se conecta una API en una réplica futura, habrá que añadir carga, error recuperable y cancelación sin borrar el estado vigente.

## 8. Cómo extender a las tarjetas repetidas

### Líneas: qué reutilizar y qué adaptar

Reutiliza cabecera, controles, calendario, consulta mensual, ejes, fuentes, diálogo, lectura y tabla temporal.

Adapta unidad, frecuencia, dominio, semántica de series y referencias. Para expectativas por año de referencia, no confundas la fecha de encuesta con el año proyectado. Para índices de actividad, no compares niveles con porcentajes en el mismo eje sin una transformación explícita. Para intervalos de pronóstico, documenta probabilidades y límites; no reutilices las bandas de IPCA > núcleos.

### Tablas: qué reutilizar y qué adaptar

Reutiliza alineación numérica, encabezados, búsquedas, botones desplegables, conservación del estado y presentación móvil.

Adapta las columnas y las filas a su tarea. El gasto con barras de peso necesita una unidad monetaria y su propio total. La sensibilidad con R² necesita horizonte, muestra y modelo. No conviertas todas esas tablas en amplitud. AM1-03-2 y AM2-02-2 siguen siendo excepciones del inventario: su geometría dominante corresponde a otras familias.

### Columnas: qué reutilizar y qué adaptar

Reutiliza cero visible, separación de positivos/negativos, selección mensual, consulta y detalle.

Adapta apilado frente a agrupación, número de componentes y relación entre barra y línea. Una columna de nivel simple no necesita nueve colores. Una descomposición en pp no se convierte a proporción del total. Si cada serie tiene una unidad diferente, resuelve la comparación explícitamente; no añadas un doble eje silencioso.

### Orden sugerido de aplicación

1. Elegir un caso nuevo de cada variante, no todas las repeticiones a la vez.
2. Copiar la estructura de interacción de la familia.
3. Escribir el adaptador y declarar unidades antes de dibujar.
4. Conservar el identificador original para trazabilidad.
5. Comparar requisitos del nuevo caso con las excepciones documentadas.
6. Sólo después extender a las tarjetas equivalentes.

## 9. Prompt maestro para otro LLM

Copia este bloque junto con el HTML, esta guía y las tablas del caso que quieras adaptar:

~~~text
Quiero adaptar un gráfico del monitor usando la maqueta entregada como referencia.

Primero lee la guía y el HTML. Conserva su lenguaje visual, sus controles accesibles
y la separación entre datos, adaptadores y renderizadores.

Caso a adaptar:
- Identificador original: [completar]
- Familia y variante: [línea / tabla / columna y su variante]
- Pregunta que debe responder: [completar]
- Fuente y columnas: [adjuntar o identificar archivos reales]
- Frecuencia y fecha de referencia: [completar]
- Unidad de entrada y de presentación: [completar]
- Fórmulas y referencias que deben conservarse: [completar]

Entregables:
1. HTML funcional y editable que abra sin servidor, con fuentes y datos locales.
2. Guía detallada de las decisiones, adaptador, cálculos y casos límite.

Vista compacta:
- Mantén título, unidad, corte y comparación principal.
- Conserva acceso a todas las series o categorías exigidas.
- Usa un selector de fecha accesible y una lectura numérica en HTML.
- Añade tooltip al pasar el ratón y al enfocar con teclado, con fecha, unidades
  y datos ausentes explícitos. La vista previa no modifica la consulta fijada.
- Clic/toque conserva los datos en el panel; Escape cierra sólo la ayuda.
- Para columnas, separa total en % y componentes en pp; conserva las categorías.
- En micrográficos, usa un botón accesible y detalla sólo la comparación concreta.

Agrandar:
- Debe conservar filtros y fecha del compacto.
- Añade espacio, detalle por periodo y metodología pertinente a la familia.
- Cierra con botón y Escape y devuelve el foco al control que lo abrió.
- No copies secciones de otro caso si no corresponden a su semántica.

Reglas:
- No inventes datos ni sustituyas null por cero.
- No alinees series por posición: une por periodo y declara su granularidad.
- No multipliques por 100 columnas que ya están en porcentaje o pp.
- No normalices contribuciones a 100 %.
- No elimines categorías para simplificar la estética.
- No conviertas un episodio en un intervalo de incertidumbre.
- Conserva las identidades de comentario existentes si editas nodos con UUID.
- Centraliza tokens; evita CDN, fuentes remotas y dependencias ocultas.
- Haz que todos los controles implementen un comportamiento real.
- No modifiques el sitio original cuando se haya pedido una maqueta separada.

Antes de crear una nueva entrega, describe el alcance y las diferencias del caso.
Si sólo faltan decisiones pequeñas y reversibles, decláralas como supuestos.
Si faltan datos esenciales, identifica exactamente el archivo o campo requerido.
No afirmes que probaste o renderizaste algo si no lo hiciste.
~~~

## 10. Prompts específicos

### Nueva línea

~~~text
Usa el caso IPCA como estructura de una serie temporal y el caso fiscal sólo si
necesitas un relleno de brecha. Declara cada serie como observada, referencia,
expectativa o contrafactual. Conserva null, las fechas y las unidades.
Si hay cruces, calcula su intersección antes de colorear el área.
Añade el caso a CASES y STATES sin duplicar el motor.
~~~

### Nueva tabla

~~~text
Usa el caso de amplitud para las interacciones, no para copiar sus fórmulas.
Define el significado y la unidad de cada columna, el universo de cada fila,
la regla de agrupación y si los grupos se superponen.
La búsqueda no debe cambiar un denominador estadístico.
Los detalles deben poder abrirse con teclado y conservarse al Agrandar.
~~~

### Nuevas columnas

~~~text
Usa el caso de aportes como estructura de selección y consulta.
Decide explícitamente si las barras son simples, agrupadas o apiladas.
Declara la unidad de cada barra y de la línea, si existe.
Calcula el dominio con positivos, negativos y línea, y conserva cero.
Si hay suma y total, muestra su diferencia sin modificar los componentes.
~~~

## 11. Criterios de revisión para una futura integración

Esta sección es una pauta para quien integre la propuesta; no documenta pruebas ejecutadas en esta entrega.

1. Elegir último mes, un mes intermedio y un mes sin referencia.
2. Comprobar un null y una discontinuidad sin interpolación inventada.
3. Comparar contra los JSON un valor y una transformación por familia.
4. Revisar la brecha fiscal positiva, negativa, exactamente cero y con cruce entre meses.
5. Comprobar que la escala contiene apilados y línea.
6. Revisar que los nueve grupos siguen presentes y no se normalizaron.
7. Verificar el límite de amplitud ±0,001 en fracción y n = 0.
8. Abrir componentes, cambiar fecha y Agrandar: no debe perderse el estado.
9. Buscar un hijo, borrar búsqueda y recuperar la lista completa.
10. Recorrer con teclado, cerrar con Escape y confirmar retorno de foco.
11. Revisar 375, 768, 1024 y 1440 px con nombres largos y zoom.
12. Comprobar que la tabla móvil conserva unidades y todos sus valores.
13. Si se modifica el adaptador de origen, actualizar la guía junto al código.
14. Recorrer varios meses con el ratón sin que cambie la fecha fijada en el panel.
15. Conservar una consulta, abrir Agrandar y cerrar: mismo mes y mismo detalle.
16. Revisar tooltip cerca de cada borde, con nueve grupos y con un valor null.
17. Pulsar Escape sobre una ayuda dentro del diálogo: primero cierra la ayuda, después el diálogo.
18. Recorrer con flechas, Inicio/Fin y selector mensual; fijar micrográficos con Enter y espacio.
19. En táctil, confirmar consulta persistente sin burbuja de hover ni pérdida de desplazamiento vertical.

## 12. Trazabilidad y decisiones pendientes

La extracción se basa en:

- assets/js/derivados/am2.js: AM2-03-1, nucleoAA, GRUPOS_APORTE y AM2-01-0.
- assets/js/derivados/am4.js: AM4-02-0.
- assets/js/derivados/am1.js: AGREG_03, conteo, tablaAmplitud e idsDe.
- data/infj_serie.json, od_bcb.json, od_total.json, fiscal_mensual.json, grafico_inflacion_v2.json, actv_serie.json y actv_miembro.json.
- Ampliación: data/empleo_pagina.json, fis_gasto.json y fiscal_cascada.json.
- Adaptadores nuevos: AM1-01-4 e ids de actividad; AM3-02-3 y medianaDesoc; AM4-07-3 y tablaGasto; AM4-04-0 y selector ventana04.

Directorio de referencia original:
C:\Users\pablo\OneDrive\Documentos\macro_bz\monitor\qwen3.8-max\site

El monitor original, index.html, maqueta-relojes.html e INFORME_GRAFICOS.md no se modifican con esta entrega. La guía conserva el trabajo previo y documenta ocho ejemplos de cuatro familias.

Queda pendiente elegir qué propuestas se trasladan al monitor y revisar las variantes no representadas antes de aplicarlas de forma masiva. No hay una dependencia pendiente para abrir la maqueta autónoma.

## 13. Especificación detallada de los cuatro ejemplos añadidos

La ampliación conserva los cuatro ejemplos iniciales y sus tooltips. No se cambian sus universos, fórmulas ni fuentes. Se suman cuatro adaptadores y se mantiene un solo diálogo de Agrandar para los ocho casos.

### 13.1 Líneas: índices de actividad, a/a

**Caso original:** AM1-01-4.  
**Tabla:** actv_serie.json.  
**Pregunta:** ¿cómo cambia la actividad del conjunto y de sus sectores en el mismo periodo?

La tarjeta añade el selector Series con dos cestas completas:

| Cesta | Serie 1 | Serie 2 | Serie 3 | Serie 4 |
|---|---|---|---|---|
| PIM, PMC y PMS | IBC-Br (v001) | Industria PIM-PF (v006) | Comercio ampliado PMC (v003) | Servicios PMS (v005) |
| IBC-Br y sectores | IBC-Br (v001) | IBC-Br agropecuario (v007) | IBC-Br industria (v008) | IBC-Br servicios (v009) |

**Contrato:** fecha mensual y a12 × 100. No se utiliza m12, que en otros ejemplos representa otra comparación. Todas las series son observadas y sus trazos son continuos cuando hay datos. No se marca la cuarta como referencia discontinua sólo por ser la última de la lista.

El calendario toma los últimos 48 meses disponibles del conjunto actv_serie. Cada cesta contiene el mismo calendario; un mes sin valor para una serie permanece null. La ventana de 24 meses recorta ese calendario sin modificar los valores ni arrastrar una tasa anterior.

**Compacto:** cuatro líneas, leyenda completa, cesta, ventana y consulta mensual. El panel muestra los cuatro valores del mes.

**Tooltip:** mes y las cuatro variaciones en % a/a, con IBC-Br como lectura principal y el mismo orden de la leyenda. Una serie ausente se identifica como Sin dato.

**Agrandar:** conserva cesta, ventana y mes. Añade el recorrido mensual y una tabla de hasta doce observaciones cercanas, con una columna por serie. Cambiar la cesta conserva el mes cuando existe.

**Reglas de réplica:**

- Declarar todos los identificadores y sus nombres en el adaptador.
- No aplicar un trazo de meta a una serie observada.
- No sumar índices ni tasas de series distintas para inventar un agregado.
- Mantener el calendario completo y no unir datos por posición.
- El corte global y el último dato de una serie concreta pueden diferir: no se inventa el dato del mes global.

### 13.2 Columnas: brecha de desocupación

**Caso original:** AM3-02-3.  
**Tabla:** empleo_pagina.json.  
**Pregunta:** ¿la desocupación desestacionalizada del mes está por encima o por debajo de su referencia histórica?

~~~text
historia = desocupacion_sa válida entre 2012-01-01 y 2019-12-31
referencia = mediana(historia)
tasa_porcentaje = desocupacion_sa × 100
referencia_porcentaje = referencia × 100
brecha_pp = (desocupacion_sa − referencia) × 100
~~~

La columna brecha_pp existente en empleo_pagina pertenece a una comparación distinta y NO se utiliza para este gráfico. Reutilizarla por su nombre sería un error semántico.

La referencia permanece fija al cambiar de ventana. Se representa la historia desde enero de 2016 y se ofrecen los últimos cinco o tres años. Las fechas faltantes se conservan como huecos mensuales.

**Compacto:** barras desde cero, acero para valores positivos y cobre para negativos. Las etiquetas dicen Por encima / Por debajo de la mediana: el color no se interpreta como bueno o malo sin contexto.

**Consulta persistente:** brecha en pp, tasa SA en % y mediana histórica en %. No son tres magnitudes intercambiables.

**Tooltip:** los mismos tres valores y una frase que explica el signo. No se coloca % a una brecha en puntos porcentuales.

**Agrandar:** mismo mes y ventana, gráfico mayor y tabla temporal. El eje contiene positivos, negativos y cero.

**Reglas de réplica:**

- Calcular la mediana con todos los datos válidos del intervalo base, no con el tramo visible.
- No recalcular la referencia al cambiar de ventana o al consultar un mes.
- No convertir null en cero.
- Si se adopta otro intervalo histórico en un escenario nuevo, cambiar la etiqueta, el cálculo y la guía juntos.
- Si faltara toda la historia base, no inventar una mediana: mostrar el caso como no disponible y explicar la dependencia.

### 13.3 Tabla: gasto, partida por partida

**Caso original:** AM4-07-3.  
**Tabla:** fis_gasto.json.  
**Corte disponible:** julio de 2026 en esta extracción.  
**Estructura:** 19 filas ordenadas por orden, con partidas principales, subpartidas y Gasto total.

La fuente es una foto del último corte, no una serie por mes. Por eso la interfaz no añade un selector temporal ficticio. Usa:

1. Comparar en tarjeta: elige Cambio 1 año, Cambio 3 años o crecimiento Real a 1, 2 o 5 años.
2. Consultar partida: permite seleccionar cualquiera de las 19 filas, incluidas las subpartidas plegadas.
3. Botón de grupo: despliega o pliega los hijos en la tarjeta compacta.
4. Barra/valor de peso: vista previa al pasar el ratón o enfocar; clic/toque fija la partida.

Seleccionar una subpartida abre automáticamente su padre en compacto. Cambiar la métrica conserva esa selección. La vista ampliada muestra todas las filas y todos los horizontes, manteniendo el estado de los grupos que se usará al volver al compacto.

#### Unidades: entrada y salida

| Campo de entrada | Transformación | Presentación |
|---|---|---|
| pct_pib | × 100 | Peso en % del PIB |
| d_pct_1a | × 100 | Cambio de peso a 1 año en pp |
| d_pct_3a | × 100 | Cambio de peso a 3 años en pp |
| real_1a | × 100 | Crecimiento real acumulado a 1 año en % |
| real_2a | × 100 | Crecimiento real acumulado a 2 años en % |
| real_5a | × 100 | Crecimiento real acumulado a 5 años en % |

Estas columnas entran como fracciones. Es distinto de fiscal_mensual y fiscal_cascada, que ya contienen niveles en porcentaje y cambios en pp. No aplique una conversión uniforme a todos los archivos fiscales.

Los crecimientos reales multianuales no se anualizan. La maqueta mantiene la magnitud acumulada de origen.

#### Geometría de las barras de peso

~~~text
ancho relativo = peso_partida_en_PIB / peso_gasto_total_en_PIB × 100
~~~

La cifra visible sigue siendo el peso en el PIB. La leyenda explica que la barra compara contra el gasto total. La escala es común para todos los padres e hijos; no se recalcula para magnificar cada fila.

**Jerarquía:** nivel = 1 identifica subpartidas de la partida principal anterior. Gasto total es la referencia de las barras, no una fila que se sume a las demás.

**Tooltip:** nombre completo, corte, tipo de fila, peso, ambos cambios y los tres crecimientos reales, todos con unidad. La consulta fija muestra el peso, el cambio a 1 año y el crecimiento real a 1 año. El detalle completo permanece en Agrandar y en el tooltip.

**Móvil:** la tabla convierte cada fila en un bloque de datos con rótulos explícitos. No se ocultan métricas de la tabla ampliada. Los nombres envuelven completos.

**Reglas de réplica:**

- No sumar partidas principales y subpartidas: hay doble conteo.
- No derivar tasas de crecimiento del gasto total como media de las tasas de los hijos.
- No llamar variación real a un cambio de participación en el PIB.
- No usar el signo de una variación como diagnóstico económico automático.
- Si se cambia el denominador de la barra, cambiar su explicación visible.
- No fabricar una fecha seleccionable para un archivo que sólo tiene un corte.

### 13.4 Cascada: de la deuda inicial a la de hoy

**Caso original:** AM4-04-0.  
**Tabla:** fiscal_cascada.json.  
**Ventanas reales:** 1, 2, 3, 5 y 10 años. La selección inicial es tres años.

Cada ventana tiene deuda_inicial, deuda_final, mes_base, mes_fin y cuatro componentes ordenados: Intereses, Déficit primario, Crecimiento y Residuo.

**Contrato de unidades:** los niveles están en % del PIB y valor de cada componente, en pp. Ya están escalados; no se multiplican por 100.

~~~text
acumulado_0 = deuda_inicial
acumulado_i = acumulado_(i−1) + valor_componente_i
cierre_calculado = acumulado_último
diferencia = deuda_final_informada − cierre_calculado
tolerancia = 0.0001 pp
~~~

La fuente define un residuo como componente. No se elimina por considerarlo ruido, ni se sustituye por la diferencia calculada por la interfaz. Si el cierre supera la tolerancia, la maqueta lo informa y mantiene todas las cifras originales.

#### Por qué la cascada es horizontal

Los pasos se leen de arriba hacia abajo y el eje horizontal mide la posición acumulada en % del PIB. La orientación permite leer nombres completos en tarjetas estrechas y en móvil sin una tira que exija desplazamiento horizontal.

- Nivel inicial: barra desde cero a deuda_inicial.
- Contribución positiva: desde acumulado anterior hasta un nivel mayor, en cobre.
- Contribución negativa: desde acumulado anterior hasta un nivel menor, en azul.
- Conexión entre pasos: guía discontinua en el cierre del paso anterior.
- Nivel final: barra desde cero a deuda_final informada.
- Residuo: tiene el mismo tratamiento geométrico que los demás componentes y una etiqueta explícita.

El selector Consultar paso, clic/toque o las flechas permiten conservar la lectura de una etapa. Las flechas arriba/abajo siguen el orden de la cascada; Inicio/Fin seleccionan niveles inicial/final. El tooltip describe el componente, su contribución y el acumulado antes/después.

**Compacto:** ventana, paso consultado, cascada completa, lectura y conciliación visible. No se esconde una discrepancia hasta que el usuario abra Agrandar.

**Agrandar:** conserva ventana y paso; añade una tabla con tipo, nivel anterior, aporte y cierre de cada etapa. En los niveles, el campo de aporte se marca No aplica, no cero ni Sin dato.

El panel de conciliación presenta nivel inicial, cierre calculado, final informado y diferencia con cuatro decimales. El mensaje distingue un cierre dentro de tolerancia de una discrepancia.

**Reglas de réplica:**

- Mantener orden_componente: reordenar por tamaño cambia la lectura acumulada.
- Usar mes_base y mes_fin reales, no sólo etiquetas relativas como Hoy.
- Mostrar total inicial y final desde cero; las contribuciones son barras flotantes.
- Separar % del PIB de pp en tablas y tooltips.
- Si falta una contribución, no completar silenciosamente el acumulado.
- No introducir una corrección de conciliación inventada.
- Conservar el residuo de origen aunque el cierre aritmético ya parezca correcto.

### 13.5 Arquitectura de extensión sin duplicar la aplicación

El archivo assets/graficos_frecuentes_extra.js se incorpora en el marcador EXTRA_ADAPTERS del script principal antes de montar los casos. Sus funciones no requieren otra página ni un segundo diálogo.

| Pieza adicional | Responsabilidad |
|---|---|
| EXTRA_CASES | Identificar los cuatro adaptadores nuevos |
| DATA.activityBaskets | Dos cestas con el mismo calendario de actividad |
| METRICS | Nombre y unidad de cada horizonte del gasto |
| bridge | Resolver la ventana vigente de cascada |
| extraControls | Controles propios de cada variante |
| extraReading | Consulta persistente con unidades del caso |
| extraTip | Tooltip semántico de las cuatro variantes |
| spendingTable | Jerarquía compacta y detalle completo del gasto |
| bridgeReconciliation | Cierre calculado, final informado y diferencia |
| renderExtraChart | Barras con signo y cascada horizontal |
| selectExtra | Fijar partida, paso o mes sin modificar el resto |
| extraDetails | Tabla temporal o conciliación según la variante |

La extensión delega las líneas al motor existente y reutiliza el gestor de tooltips y el diálogo. Los renderizadores de barras y cascada comparten formato, dominio, selección y estilos. Los eventos de controles propios se resuelven antes del manejador genérico para no tratar una partida como si fuera una fecha.

Al integrar en otro proyecto, puede reorganizarse este código en módulos. Lo que debe conservarse es el contrato de cada adaptador y un solo estado por caso, compartido entre compacto y Agrandar. No copie dos motores de selección independientes.

### 13.6 Prompts específicos de las variantes nuevas

~~~text
ACTIVIDAD
Añade un caso de cuatro líneas observadas con dos cestas seleccionables.
Usa a12 × 100 de actv_serie, el mismo calendario mensual y hasta 48 meses.
Conserva el mes al cambiar de cesta. No dibujes ninguna serie como meta.
Replica tooltips, consulta persistente, tabla por periodos y Agrandar.

BRECHA DE DESOCUPACIÓN
Calcula la mediana de desocupacion_sa válida entre 2012 y 2019.
Representa (tasa SA − mediana) × 100 en pp desde 2016.
No uses el campo brecha_pp del archivo: pertenece a otra comparación.
La referencia no cambia con la ventana visible. Distingue tasa y brecha.

GASTO
Conserva las 19 filas, su jerarquía y el corte real de fis_gasto.
Convierte cada campo según la tabla de unidades, una sola vez.
No sumes padres e hijos. Declara el denominador de las barras.
Muestra todos los horizontes en Agrandar y permite desplegar hijos en compacto.
No inventes una serie temporal para un archivo de corte único.

CASCADA
Usa las cinco ventanas de fiscal_cascada y conserva el orden de sus componentes.
Los niveles ya están en % del PIB; las contribuciones ya están en pp.
Dibuja barras flotantes, conserva el residuo y muestra la conciliación.
No redistribuyas la diferencia de cierre. Usa una tolerancia de 0,0001 pp.
Mantén ventana y paso entre compacto y Agrandar, con consulta por teclado.
~~~

### 13.7 Casos que debe revisar quien integre

Esta lista no afirma pruebas ejecutadas en esta entrega.

1. Cambiar entre las dos cestas de actividad y conservar la fecha.
2. Comparar un valor a12 con la fila original y distinguirlo de m12.
3. Revisar un mes de actividad sin alguna serie: Sin dato, sin arrastre.
4. Cambiar la ventana de desocupación y confirmar que la mediana no se mueve.
5. Contrastar tasa, mediana y resta en pp con los JSON.
6. Ver el cero y los dos signos de las columnas sin recorte.
7. Abrir una partida de gasto y seleccionar un hijo desde el desplegable.
8. Revisar que cambiar la métrica no cambia el universo ni la partida fijada.
9. Comprobar una fila de cada tipo: padre, hijo y total.
10. Comparar d_pct_1a, d_pct_3a y real_2a: una sola conversión × 100.
11. Recorrer las cinco ventanas de cascada y sus seis pasos.
12. Contrastar inicio + cuatro contribuciones con el final informado.
13. Conservar el residuo aunque sea negativo y aunque el cierre sea exacto.
14. Revisar una discrepancia y un valor nulo sin corrección automática.
15. Abrir Agrandar con una partida o paso fijado y regresar sin perderlo.
16. Usar ratón, teclado y toque, incluyendo Escape sobre el tooltip.
17. Revisar 375, 768, 1024 y 1440 px, nombres largos y zoom.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--guide", action="store_true")
    args = parser.parse_args()
    if args.html:
        html()
    if args.guide:
        guide()
