"""Iterated Local Search: local search + kick të rastësishëm + pranim nëse jo më keq."""
import random
import time

from src.localsearch import make_arc_of, arcs_of, local_search


def _random_move(nodes, arc_of, rng, tries=100):
    """Një lëvizje e rastësishme (relocate ose swap) që jep tur të lejuar."""
    n = len(nodes)
    for _ in range(tries):
        if rng.random() < 0.5 and n > 4:
            L = rng.choice((1, 2, 3))
            i = rng.randint(1, n - L)
            seg = nodes[i:i + L]
            rest = nodes[:i] + nodes[i + L:]
            j = rng.randint(1, len(rest))
            if j == i:
                continue
            cand = rest[:j] + seg + rest[j:]
        else:
            if n < 3:
                continue
            i = rng.randint(1, n - 2)
            j = rng.randint(i + 1, n - 1)
            cand = nodes[:]
            cand[i], cand[j] = cand[j], cand[i]
        if arcs_of(cand, arc_of) is not None:
            return cand
    return nodes


def iterated_local_search(inst, arc_seq, time_limit=5.0, seed=0, kick=3):
    """Kthen (harqet më të mira, kosto, numri i iterimeve)."""
    rng = random.Random(seed)
    arc_of = make_arc_of(inst)
    t0 = time.perf_counter()

    cur, cur_cost, _ = local_search(inst, arc_seq, time_limit, arc_of)
    best, best_cost = cur, cur_cost
    iters = 0
    while time.perf_counter() - t0 < time_limit:
        nodes = [inst.arcs[a][0] for a in cur]
        for _ in range(kick):
            nodes = _random_move(nodes, arc_of, rng)
        kicked = arcs_of(nodes, arc_of)
        remaining = time_limit - (time.perf_counter() - t0)
        new, new_cost, _ = local_search(inst, kicked, remaining, arc_of)
        iters += 1
        if new_cost <= cur_cost:               # pranojmë edhe barazimin
            cur, cur_cost = new, new_cost
        if new_cost < best_cost - 1e-9:
            best, best_cost = new, new_cost
    return best, best_cost, iters