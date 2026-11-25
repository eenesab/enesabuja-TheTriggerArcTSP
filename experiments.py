"""Eksperimente: disa seed për instancë, kohë, memorie, kosto.
Përdorimi:  python experiments.py            (nëngrupi i paracaktuar)
            python experiments.py grf1 grf14 (vetëm këto)
Shkruan results/experiments.csv."""
import csv
import glob
import os
import statistics
import sys
import time
import tracemalloc

from src.loader import load_instance
from src.evaluator import is_valid, tour_cost, build_trigger_index
from src.algorithms import nearest_neighbour
from src.localsearch import local_search
from src.ils import iterated_local_search

SUBSET = ["grf1", "grf4", "grf6", "grf10", "grf14", "grf18",
          "grf101", "grf104", "grf110", "grf114", "grf120", "grf125", "grf131", "grf134"]
SEEDS = [0, 1, 2, 3, 4]
LS_LIMIT = 10.0
ILS_LIMIT = 5.0


def check(inst, trig, arcs, cost):
    """Kontroll i pavarur me evaluatorin e ngadaltë."""
    assert is_valid(inst, arcs), "tur jo i vlefshëm"
    assert abs(tour_cost(inst, arcs, trig) - cost) < 1e-6, "kosto e papërputhshme"


def measure_memory(path):
    """Kulmi i memories (MB) për ngarkim dhe për gjithë rrjedhën. Ekzekutim i veçantë."""
    tracemalloc.start()
    inst = load_instance(path)
    load_peak = tracemalloc.get_traced_memory()[1]
    trig = build_trigger_index(inst)
    tour = nearest_neighbour(inst, total_steps=150_000, trig=trig)
    local_search(inst, tour, 2.0)
    iterated_local_search(inst, tour, 1.0)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return load_peak / 1e6, peak / 1e6


def main():
    names = sys.argv[1:] or SUBSET
    files = {os.path.splitext(os.path.basename(p))[0]: p
             for p in glob.glob("data/**/*.txt", recursive=True)}
    os.makedirs("results", exist_ok=True)
    rows = []
    print(f"{'instanca':<9}{'N':>5}{'baseline':>10}{'LS':>9}{'ILS mes':>9}{'std':>6}"
          f"{'min':>8}{'load MB':>9}{'peak MB':>9}")
    for name in names:
        path = files.get(name)
        if path is None:
            print(f"{name}: skedari mungon në data/")
            continue
        load_mb, peak_mb = measure_memory(path)

        inst = load_instance(path)
        trig = build_trigger_index(inst)
        n_rel = sum(len(d) for d in inst.triggers.values())

        t0 = time.perf_counter()
        tour = nearest_neighbour(inst, total_steps=150_000, trig=trig)
        base_dt = time.perf_counter() - t0
        if tour is None:
            print(f"{name}: baseline pa tur")
            continue
        base = tour_cost(inst, tour, trig)

        t0 = time.perf_counter()
        ls_arcs, ls_cost, _ = local_search(inst, tour, LS_LIMIT)
        ls_dt = time.perf_counter() - t0
        check(inst, trig, ls_arcs, ls_cost)

        ils_costs = []
        for seed in SEEDS:
            t0 = time.perf_counter()
            arcs, cost, iters = iterated_local_search(inst, tour, ILS_LIMIT, seed=seed)
            dt = time.perf_counter() - t0
            check(inst, trig, arcs, cost)
            ils_costs.append(cost)
            rows.append({
                "instance": name, "nodes": inst.n, "arcs": len(inst.arcs), "relations": n_rel,
                "seed": seed, "baseline": round(base, 3), "baseline_sec": round(base_dt, 3),
                "ls": round(ls_cost, 3), "ls_sec": round(ls_dt, 3),
                "ils": round(cost, 3), "ils_sec": round(dt, 3), "ils_iters": iters,
                "load_peak_mb": round(load_mb, 2), "peak_mb": round(peak_mb, 2),
            })

        print(f"{name:<9}{inst.n:>5}{base:>10.1f}{ls_cost:>9.1f}"
              f"{statistics.mean(ils_costs):>9.1f}{statistics.stdev(ils_costs):>6.2f}"
              f"{min(ils_costs):>8.1f}{load_mb:>9.1f}{peak_mb:>9.1f}")

    with open("results/experiments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("U shkrua results/experiments.csv")


if __name__ == "__main__":
    main()