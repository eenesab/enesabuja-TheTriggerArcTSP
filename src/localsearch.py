"""Local search (relocate + swap) për Trigger Arc TSP, me kontroll të shpejtë fizibiliteti."""
import time


def make_arc_of(inst):
    """{(u, v): indeksi i harkut}. Supozon një hark për çift nyjesh."""
    return {(u, v): i for i, (u, v, _) in enumerate(inst.arcs)}


def tour_cost_fast(inst, arc_seq):
    """
    Kosto e turit. Për çdo hark a në pozicionin j shohim mbrapsht te harku i parë
    që është trigger për a; ai është trigger-i i fundit para a.
    """
    total = 0.0
    trg = inst.triggers
    for j, a in enumerate(arc_seq):
        c = inst.arcs[a][2]
        d = trg.get(a)
        if d:
            for i in range(j - 1, -1, -1):
                t = arc_seq[i]
                if t in d:
                    c = d[t]
                    break
        total += c
    return total


def arcs_of(nodes, arc_of):
    """Harqet e ciklit të nyjeve, ose None nëse mungon ndonjë hark."""
    n = len(nodes)
    out = []
    for i in range(n):
        a = arc_of.get((nodes[i], nodes[(i + 1) % n]))
        if a is None:
            return None
        out.append(a)
    return out


def feasible_neighbours(nodes, arc_of):
    """
    Gjeneron vetëm turet fqinje që kanë të gjitha harqet. Kontrollojmë vetëm
    harqet e reja (3 për relocate, 4 për swap) para se të ndërtojmë listën.
    Nyja 0 mbetet gjithmonë në pozicionin 0.
    """
    n = len(nodes)
    # Relocate: segment me gjatësi 1..3 hiqet dhe futet diku tjetër
    for L in (1, 2, 3):
        for i in range(1, n - L + 1):
            seg = nodes[i:i + L]
            prev = nodes[i - 1]
            nxt = nodes[(i + L) % n]
            if (prev, nxt) not in arc_of:      # vrima që lihet duhet të mbyllet
                continue
            rest = nodes[:i] + nodes[i + L:]
            m = len(rest)
            first, last = seg[0], seg[-1]
            for j in range(1, m + 1):
                if j == i:                     # pozicioni origjinal
                    continue
                if (rest[j - 1], first) in arc_of and (last, rest[j % m]) in arc_of:
                    yield rest[:j] + seg + rest[j:]
    # Swap: këmbe nyjet në pozicionet i dhe j
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            cand = nodes[:]
            cand[i], cand[j] = cand[j], cand[i]
            ok = True
            for k in {i - 1, i, j - 1, j}:     # vetëm harqet që ndryshojnë
                if (cand[k], cand[(k + 1) % n]) not in arc_of:
                    ok = False
                    break
            if ok:
                yield cand


def local_search(inst, arc_seq, time_limit=3.0, arc_of=None):
    """
    First-improvement: merr lëvizjen e parë që e ul koston dhe fillon nga e para.
    Kthen (harqet, kosto, numri i lëvizjeve).
    """
    if arc_of is None:
        arc_of = make_arc_of(inst)
    arcs = list(arc_seq)
    nodes = [inst.arcs[a][0] for a in arcs]     # nodes[0] == 0
    best = tour_cost_fast(inst, arcs)
    t0 = time.perf_counter()
    moves = 0
    improved = True
    while improved:
        improved = False
        for cand in feasible_neighbours(nodes, arc_of):
            if time.perf_counter() - t0 > time_limit:
                return arcs, best, moves
            cand_arcs = arcs_of(cand, arc_of)
            c = tour_cost_fast(inst, cand_arcs)
            if c < best - 1e-9:
                nodes, arcs, best = cand, cand_arcs, c
                moves += 1
                improved = True
                break
    return arcs, best, moves