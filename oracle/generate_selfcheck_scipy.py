"""
oracle/generate_selfcheck_scipy.py
1280 sentetik parametre kombinasyonunda t-paired değerlerini scipy ile üretir.
KÂHİN DEĞİLDİR: motorla aynı algoritmayı (kesikli N araması + scipy.stats.nct) kullanır,
yalnızca motorun kendi kendine tutarlılığını sınar. statsmodels kullanılmaz.
Bilinen fark: bu betikte sol kuyruk NaN koruması yoktur; motor (distributions.nct_power)
NaN'ı 0.0 kabul eder. Selfcheck uyuşmazlıklarının kaynağı budur.
"""

import csv
import math
from pathlib import Path
import numpy as np
from scipy import stats

def compute_t_paired(dz: float, alpha: float, target_power: float, tails: int):
    # Kesikli arama: Power(N) >= target_power olan en küçük N
    for n in range(2, 5000):
        df = n - 1
        ncp = dz * math.sqrt(n)
        alpha_eff = alpha / 2.0 if tails == 2 else alpha
        t_crit = stats.t.ppf(1.0 - alpha_eff, df)
        
        if tails == 1:
            pwr = stats.nct.sf(t_crit, df, ncp)
        else:
            pwr = stats.nct.sf(t_crit, df, ncp) + stats.nct.cdf(-t_crit, df, ncp)
            
        if pwr >= target_power:
            return {
                "n": n,
                "df": df,
                "ncp": round(ncp, 6),
                "critical_t": round(t_crit, 6),
                "actual_power": round(pwr, 6)
            }
    return None

def main():
    output_path = Path(__file__).parent / "selfcheck_scipy.csv"
    
    dz_values = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5]
    alpha_values = [0.001, 0.01, 0.025, 0.05, 0.10]
    power_values = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99]
    tails_values = [1, 2]
    
    rows = []
    vector_id = 1
    
    for tails in tails_values:
        for dz in dz_values:
            for alpha in alpha_values:
                for target_pwr in power_values:
                    res = compute_t_paired(dz, alpha, target_pwr, tails)
                    if res:
                        rows.append({
                            "id": f"REF_{vector_id:04d}",
                            "test": "t-paired",
                            "mode": "a-priori",
                            "tails": tails,
                            "dz": dz,
                            "alpha": alpha,
                            "target_power": target_pwr,
                            "n_rounded": res["n"],
                            "df": res["df"],
                            "ncp": res["ncp"],
                            "critical_t": res["critical_t"],
                            "actual_power": res["actual_power"]
                        })
                        vector_id += 1

    fieldnames = ["id", "test", "mode", "tails", "dz", "alpha", "target_power", "n_rounded", "df", "ncp", "critical_t", "actual_power"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Başarıyla {len(rows)} selfcheck vektörü üretildi -> {output_path}")

if __name__ == "__main__":
    main()
