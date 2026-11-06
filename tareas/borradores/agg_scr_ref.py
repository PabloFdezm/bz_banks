import zipfile, pandas as pd, sys, time
from pathlib import Path
CR=Path(__file__).resolve().parents[2]/'datos/crudo/bcb_scr/scrdata/actual'
SAL=Path(__file__).resolve().parent/'_salida'; SAL.mkdir(exist_ok=True)
cols=['data_base','segmento','cliente','porte','modalidade','submodalidade','carteira_ativa','carteira_inadimplencia','vencido_de_15_ate_90_dias','ativo_problematico']
def grupo(m, s):
    s=s.lower(); m=m.lower()
    if 'cartão' in s: return 'Tarjeta'
    if 'com consignação' in s: return 'Consignado'
    if 'sem consignação' in s: return 'No consignado'
    if 'veículos' in s: return 'Vehículos'
    if 'habitacional' in s or 'home equity' in s or 'imobili' in m: return 'Habitacional'
    if 'rura' in m or 'agroindustria' in s: return 'Rural y agroindustrial'
    return 'Otros'
lim=time.time()+float(sys.argv[1]); anios=sys.argv[2:]
for anio in anios:
    z=zipfile.ZipFile(CR/f'scrdata_{anio}.zip')
    for n in sorted(x for x in z.namelist() if x.endswith('.csv')):
        out=SAL/f'g_{n[8:14]}.parquet'
        if out.exists() or n[8:14]<'201812': continue
        if time.time()>lim: print('tiempo'); sys.exit()
        t=time.time()
        d=pd.concat(pd.read_csv(z.open(n), sep=';', dtype=str, usecols=cols, encoding='utf-8-sig', chunksize=500000))
        for c in cols[6:]: d[c]=pd.to_numeric(d[c].str.replace(',','.'),errors='coerce')
        mp={k:grupo(*k) for k in d[['modalidade','submodalidade']].drop_duplicates().itertuples(index=False,name=None)}
        d['grupo']=[mp[k] for k in zip(d.modalidade,d.submodalidade)]
        d.loc[d.cliente=='PF','porte']='PF'
        g=d.groupby(['data_base','cliente','grupo','porte','segmento'],as_index=False)[cols[6:]].sum()
        g.to_parquet(out); print(n, len(g), round(time.time()-t,1),'s', flush=True)
