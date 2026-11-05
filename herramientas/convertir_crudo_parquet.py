"""Convierte a parquet los CSV crudos de IF.Data (valores y cadastro) que todavía no lo están.

El parquet guarda todas las columnas como texto, igual que el CSV (sin pérdida; ver almacen.csv_a_parquet),
y el manifiesto anota URL y sha256 del CSV original más los del parquet. Por defecto NO borra los CSV.

Uso (desde la raíz del repo):
    python -X utf8 herramientas/convertir_crudo_parquet.py            # convierte lo que falte
    python -X utf8 herramientas/convertir_crudo_parquet.py --borrar   # además borra cada CSV ya convertido
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import almacen as A  # noqa: E402

DATASETS = ("valores", "cadastro")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--borrar", action="store_true", help="borra cada CSV cuyo parquet ya está anotado en el manifiesto")
    args = ap.parse_args()
    antes = despues = 0
    for ds in DATASETS:
        d = A.ruta_cruda("bcb_ifdata", ds)
        csvs = sorted(d.glob("*.csv"))
        print(f"== {ds}: {len(csvs)} CSV")
        for i, c in enumerate(csvs, 1):
            pq = A.ruta_parquet(c)
            tam = c.stat().st_size
            anotado = (A.leer_manifiesto(d) or {}).get("archivos", {}).get(c.name, {}).get("parquet")
            if not pq.exists() or not anotado or anotado.get("bytes") != pq.stat().st_size:
                t = time.time()
                A.csv_a_parquet("bcb_ifdata", ds, c)
                print(f"  [{i}/{len(csvs)}] {c.name}: {tam/1e6:.1f} MB -> {pq.stat().st_size/1e6:.2f} MB ({time.time()-t:.0f} s)")
            antes += tam
            despues += pq.stat().st_size
            if args.borrar:
                meta = (A.leer_manifiesto(d) or {}).get("archivos", {}).get(c.name, {}).get("parquet")
                if meta and meta.get("bytes") == pq.stat().st_size:
                    c.unlink()
                else:
                    print(f"  [!] {c.name}: el manifiesto no anota su parquet; no se borra")
    print(f"Total: {antes/1e9:.2f} GB en CSV -> {despues/1e6:.0f} MB en parquet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
