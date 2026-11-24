"""Baseline + local search + ILS mbi të gjitha instancat në data/; shkruan results/metrics.csv."""
import csv
import glob
import os
import time

from src.loader import load_instance
from src.evaluator import is_valid, tour_cost, build_trigger_index
from src.algorithms import nearest_neighbour
from src.localsearch import local_search
from src.ils import iterated_local_search

LS_LIMIT = 3.0
ILS_LIMIT = 5.0


def check(inst, trig, arcs, cost):
    """Kontroll i pavarur me evaluatorin e ngadaltë."""
    assert is_valid(inst, arcs), "tur jo i vlefshëm"
    assert abs(tour_cost(inst, arcs, trig) - cost) < 1e-6, "kosto e papërputhshme"


def main():
    files = sorted(glob.glob("data/**/*.txt", recursive=True))
    os.makedirs("results", exist_ok=True)
    rows = []
    print(f"{'instanca':<26}{'N':>5}{'baseline':>10}{'LS':>9}{'ILS':>9}{'ulje%':>7}{'iter':>7}{'LS s':>7}")
    for path in files:
        inst = load_instance(path)
        trig = build_trigger_index(inst)
        tour = nearest_neighbour(inst, total_steps=150_000, trig=trig)
        if tour is None:
            print(f"{path:<26}{inst.n:>5}{'pa tur':>10}")
            continue
        base = tour_cost(inst, tour, trig)

        t0 = time.perf_counter()
        ls_arcs, ls_cost, _ = local_search(inst, tour, LS_LIMIT)
        ls_dt = time.perf_counter() - t0
        check(inst, trig, ls_arcs, ls_cost)

        t0 = time.perf_counter()
        ils_arcs, ils_cost, iters = iterated_local_search(inst, tour, ILS_LIMIT)
        ils_dt = time.perf_counter() - t0
        check(inst, trig, ils_arcs, ils_cost)

        gain = 100 * (base - ils_cost) / base
        print(f"{path:<26}{inst.n:>5}{base:>10.1f}{ls_cost:>9.1f}{ils_cost:>9.1f}{gain:>7.1f}{iters:>7}{ls_dt:>7.2f}")
        rows.append({
            "instance": path.replace("\\", "/"), "nodes": inst.n, "arcs": len(inst.arcs),
            "relations": sum(len(d) for d in inst.triggers.values()),
            "baseline": round(base, 3), "ls": round(ls_cost, 3), "ils": round(ils_cost, 3),
            "ls_sec": round(ls_dt, 3), "ils_sec": round(ils_dt, 3), "ils_iters": iters,
        })

    with open("results/metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("U shkrua results/metrics.csv")


if __name__ == "__main__":
    main()