"""Ekzekuton baseline-in mbi të gjitha instancat në data/ dhe printon një tabelë."""
import glob
import time

from src.loader import load_instance
from src.evaluator import is_valid, tour_cost, build_trigger_index
from src.algorithms import nearest_neighbour


def main():
    files = sorted(glob.glob("data/**/*.txt", recursive=True))
    print(f"{'instanca':<26}{'N':>5}{'kosto':>12}{'hapa':>9}{'prova':>7}{'status':>14}{'sek':>8}")
    for path in files:
        inst = load_instance(path)
        trig = build_trigger_index(inst)

        t0 = time.perf_counter()
        tour = nearest_neighbour(inst, total_steps=150_000, trig=trig)
        dt = time.perf_counter() - t0
        steps, attempts, status = nearest_neighbour.last_info

        if tour is None:
            cost = "-"
        elif not is_valid(inst, tour):
            cost, status = "JO VALID", "gabim"
        else:
            cost = f"{tour_cost(inst, tour, trig):.1f}"
        print(f"{path:<26}{inst.n:>5}{cost:>12}{steps:>9}{attempts:>7}{status:>14}{dt:>8.2f}")


if __name__ == "__main__":
    main()